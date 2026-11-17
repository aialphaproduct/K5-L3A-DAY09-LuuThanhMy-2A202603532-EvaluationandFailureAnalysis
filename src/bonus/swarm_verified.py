"""B3 — swarm with a code-based verifier before the write.

Same flow as lab8.shapes.swarm_reference, but right before pricing the quote,
a verifier re-reads the order's own structured row and compares it against
every field the quote was about to be computed from (delay_days, status,
damage_verified). swarm_reference has a known weakness: on seed % 5 == 0 it
lets a parsed number from the customer's own ticket text overwrite
delay_days before quoting. The verifier catches exactly that and any other
place a field drifted from the structured order, reverts to the structured
value, and logs one `verifier_override` trace event. There is only ever one
correction round — the model never gets a second try, and the verifier
itself never invents or raises an amount, it only restores what the host's
own order row already said.

Source: Google Research 2026, error amplification (independent agents
amplify error up to 17.2x; centralized verification brings it to 4.4x).
This is the code-only version of that idea: no second model call, just a
field-level diff against the host's own data.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, tool_cost
from lab8.trace import Trace

# Fields the quote is computed from. Anything outside this list never reaches
# compute_compensation, so there is nothing else for the verifier to check.
VERIFIED_FIELDS = ("delay_days", "status", "damage_verified")


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    run_id = make_run_id("swarm_verified", claim_id, seed)
    trace = Trace(run_id)

    budget.add_tool(tool_cost())
    claim_row = conn.execute(
        "SELECT claim_id, principal_id, order_id, ticket FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()
    if claim_row is None:
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn, shape="swarm_verified", claim_id=claim_id, seed=seed, status="failed",
            proposal_amount=0, budget=budget, trace=trace, error_reason="unknown_claim",
        )

    ticket = claim_row["ticket"]
    complete(budget, seed=seed, purpose="peer", prompt=ticket)
    parsed_delay = parse_delay_days(ticket)
    complete(budget, seed=seed, purpose="parse", prompt=ticket)

    if not claim_row["order_id"]:
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn, shape="swarm_verified", claim_id=claim_id, seed=seed, status="needs_info",
            proposal_amount=0, budget=budget, trace=trace, error_reason="missing_order_id",
        )

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}", claim_id=claim_id, task="check_applicable_policy", facts={},
        allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"],
    )
    trace.add("handoff", safe_dump(handoff))
    investigated = run_readonly_investigators(
        conn, budget, handoff, principal_id=claim_row["principal_id"]
    )
    order_view = investigated["tools"].get("lookup_order", {})
    if not order_view.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return finish(
            conn, shape="swarm_verified", claim_id=claim_id, seed=seed, status="escalated",
            proposal_amount=0, budget=budget, trace=trace, error_reason=order_view.get("reason"),
        )

    structured_order = dict(order_view["order"])
    order = dict(structured_order)
    # Same weakness as swarm_reference: one seed in five trusts a delay parsed
    # from the ticket over the order row.
    if parsed_delay is not None and parsed_delay != int(order["delay_days"]) and seed % 5 == 0:
        order["delay_days"] = parsed_delay
        trace.add("model_override", {"delay_days": parsed_delay})

    # Verifier: every field the quote is about to use must match the host's
    # own structured order. One correction round, no negotiation with the
    # model about it.
    mismatches = {
        field: {"model": order[field], "structured": structured_order[field]}
        for field in VERIFIED_FIELDS
        if order[field] != structured_order[field]
    }
    if mismatches:
        order = dict(structured_order)
        trace.add("verifier_override", {"fields": mismatches})

    budget.add_tool(tool_cost())
    quote_payload = compute_compensation(conn, order)
    trace.add("quote", quote_payload)
    proposal = int(quote_payload["amount_vnd"])
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    if proposal <= 0:
        return finish(
            conn, shape="swarm_verified", claim_id=claim_id, seed=seed, status="denied",
            proposal_amount=0, budget=budget, trace=trace, error_reason=quote_payload.get("reason"),
        )

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return finish(
            conn, shape="swarm_verified", claim_id=claim_id, seed=seed, status=status,
            proposal_amount=proposal, budget=budget, trace=trace, error_reason=outcome["reason"],
        )
    return finish(
        conn, shape="swarm_verified", claim_id=claim_id, seed=seed, status="resolved",
        proposal_amount=proposal, budget=budget, trace=trace, error_reason=None,
    )
