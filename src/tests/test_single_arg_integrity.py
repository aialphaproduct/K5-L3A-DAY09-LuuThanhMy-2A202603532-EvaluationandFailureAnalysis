"""single.py must only ever look up its own claim's order/principal scope.

decide() derives every tool argument from the claim row the host itself
looked up (captured once in trusted_principal_id / trusted_order_id), never
from ticket text or from re-reading a later tool result. These tests spy on
the runtime's own lookup_order call to prove no other order or principal is
ever requested while resolving a given claim.
"""

from __future__ import annotations

import lab8.runtime as runtime
from lab8.shapes.single import run_claim


def test_single_only_looks_up_its_own_claim_scope(public_db, monkeypatch):
    calls: list[tuple[str, str]] = []
    original = runtime.lookup_order

    def spy(conn, order_id, principal_id):
        calls.append((order_id, principal_id))
        return original(conn, order_id, principal_id)

    monkeypatch.setattr(runtime, "lookup_order", spy)

    result = run_claim("C-001", seed=11, store_path=str(public_db))

    assert calls == [("O-107", "P-100")]
    assert result.status == "resolved"


def test_single_never_prices_an_order_outside_its_own_scope(public_db, monkeypatch):
    """If lookup_order ever returned the wrong order, single.py must refuse to quote it."""

    def wrong_order(conn, order_id, principal_id):
        # Pretend the tool handed back a different order than requested.
        return {
            "visible": True,
            "reason": "ok",
            "order": {
                "order_id": "O-999-NOT-REQUESTED",
                "status": "delivered",
                "delay_days": 10,
                "shipping_fee_vnd": 999999,
                "paid_vnd": 999999,
                "damage_verified": False,
                "carrier": "LOGIX_LOCAL",
            },
        }

    monkeypatch.setattr(runtime, "lookup_order", wrong_order)

    result = run_claim("C-001", seed=11, store_path=str(public_db))

    assert result.status == "failed"
    assert result.error_reason == "order_scope_mismatch"
    assert result.refund_effects == []
