from __future__ import annotations

from lab8.shapes import single


def test_single_uses_fixed_tool_order_and_host_computed_amount(public_db, monkeypatch):
    actions = []
    issued = []
    order = {
        "order_id": "O-107",
        "status": "delivered",
        "delay_days": 4,
        "shipping_fee_vnd": 12000,
        "paid_vnd": 240000,
        "damage_verified": False,
        "carrier": "LOGIX_LOCAL",
    }
    quote = {"amount_vnd": 3210, "reason": None}

    def fake_run_react(conn, budget, *, observation, decide, max_steps, worker):
        assert max_steps == 8
        assert worker is True

        action = decide(observation)
        actions.append(action)
        action = decide(
            {
                "claim": observation["claim"],
                "last_tool": "get_claim_view",
                "last_result": {"found": True, "order_id": "O-107", "principal_id": "P-100"},
            }
        )
        actions.append(action)
        action = decide(
            {
                "claim": observation["claim"],
                "last_tool": "lookup_order",
                "last_result": {"visible": True, "order": order},
            }
        )
        actions.append(action)
        action = decide(
            {
                "claim": observation["claim"],
                "last_tool": "compute_compensation",
                "last_result": quote,
            }
        )
        actions.append(action)
        return {
            "stopped": "final",
            "final": action["final"],
            "observation": {"last_tool": "compute_compensation"},
        }

    def fake_issue_refund(conn, claim_id, proposed_vnd, *, crash_at=None):
        issued.append((claim_id, proposed_vnd, crash_at))
        return {
            "ok": True,
            "reason": "committed",
            "effect": {"amount_vnd": proposed_vnd},
            "conflict": False,
        }

    monkeypatch.setattr(single, "run_react", fake_run_react)
    monkeypatch.setattr(single, "issue_refund", fake_issue_refund)

    result = single.run_claim("C-001", seed=11, store_path=str(public_db))

    assert actions == [
        {"tool": "get_claim_view", "args": {"claim_id": "C-001"}},
        {"tool": "lookup_order", "args": {"order_id": "O-107", "principal_id": "P-100"}},
        {"tool": "compute_compensation", "args": {"order": order}},
        {"final": {"status": "ready", "proposal_amount": 3210, "error_reason": None, "quote": quote}},
    ]
    assert issued == [("C-001", 3210, None)]
    assert result.status == "resolved"
    assert result.proposal_amount == 3210
