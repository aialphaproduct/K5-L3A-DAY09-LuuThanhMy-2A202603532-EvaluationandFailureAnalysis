"""A missing order must not expose the customer's ticket in shape traces."""

import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.shapes import SHAPES


@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator"])
def test_missing_order_ticket_stays_private(public_db, shape, capsys):
    marker = "CANARY_SECRET_PRIVATE_TICKET"
    conn = connect(public_db)
    try:
        conn.execute(
            "UPDATE claims SET order_id = NULL, ticket = ? WHERE claim_id = ?",
            (marker, "C-001"),
        )
        conn.commit()
    finally:
        conn.close()

    result = SHAPES[shape]("C-001", seed=11, store_path=str(public_db))
    captured = capsys.readouterr()
    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert result.status == "needs_info"
    assert marker not in json.dumps(trace)
    assert marker not in captured.out + captured.err
