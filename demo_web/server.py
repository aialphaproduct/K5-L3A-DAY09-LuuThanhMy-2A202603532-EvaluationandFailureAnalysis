"""Demo web for Lab 8 (LogiX-VN): benchmark dashboard + live claim runner.

Not part of the grading repo. Runs the real shapes via lab8.app.run_shape
against a fresh temp copy of the public store for every request.
"""

from __future__ import annotations

import json
import sys
import tempfile
import uuid
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent
SRC_DIR = DEMO_DIR.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from flask import Flask, jsonify, request, send_from_directory  # noqa: E402

from lab8.app import PUBLIC_CLAIMS, prepare_store, run_shape  # noqa: E402
from lab8.db import load_jsonl  # noqa: E402
from lab8.shapes import SHAPES  # noqa: E402

app = Flask(__name__, static_folder=None)

RUN_DIR = Path(tempfile.gettempdir()) / "lab8-demo-runs"
RUN_DIR.mkdir(parents=True, exist_ok=True)

CLAIMS = load_jsonl(PUBLIC_CLAIMS)
CLAIM_INDEX = {row["claim_id"]: row for row in CLAIMS}


@app.get("/")
def index():
    return send_from_directory(DEMO_DIR, "index.html")


@app.get("/api/claims")
def api_claims():
    rows = [
        {
            "claim_id": row["claim_id"],
            "ticket": row["ticket"],
            "matrix_id": row.get("matrix_id"),
            "expected_status": row.get("expected", {}).get("status"),
        }
        for row in CLAIMS
    ]
    return jsonify(rows)


@app.get("/api/shapes")
def api_shapes():
    return jsonify(sorted(SHAPES.keys()))


@app.get("/api/benchmark")
def api_benchmark():
    path = SRC_DIR / "reports" / "benchmark.json"
    if not path.exists():
        return jsonify({"error": "chưa có reports/benchmark.json, hãy chạy lab8.benchmark trước"}), 404
    return jsonify(json.loads(path.read_text(encoding="utf-8")))


@app.post("/api/run")
def api_run():
    payload = request.get_json(force=True) or {}
    claim_id = payload.get("claim_id")
    shape = payload.get("shape")
    seed = int(payload.get("seed", 11))

    if claim_id not in CLAIM_INDEX:
        return jsonify({"error": f"không tìm thấy claim_id {claim_id!r}"}), 400
    if shape not in SHAPES:
        return jsonify({"error": f"shape {shape!r} không hợp lệ"}), 400

    run_token = uuid.uuid4().hex[:8]
    store_path = RUN_DIR / f"demo-{run_token}.sqlite"
    traces_dir = RUN_DIR / f"traces-{run_token}"
    traces_dir.mkdir(parents=True, exist_ok=True)

    prepare_store(store_path)

    import os

    cwd = os.getcwd()
    os.chdir(traces_dir)
    try:
        result = run_shape(shape, claim_id, seed=seed, store_path=str(store_path))
    finally:
        os.chdir(cwd)

    trace_data = None
    trace_path = Path(result.trace_path)
    if not trace_path.is_absolute():
        trace_path = traces_dir / trace_path
    if trace_path.exists():
        trace_data = json.loads(trace_path.read_text(encoding="utf-8"))

    ticket = CLAIM_INDEX[claim_id].get("ticket")
    return jsonify(
        {
            "ticket": ticket,
            "result": result.as_dict(),
            "trace": trace_data,
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5055, debug=False)
