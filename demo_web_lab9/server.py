"""Demo web for Lab 9 (LogiX-VN eval): failure-mode tree + trace chat + live gate.

Not part of the grading repo. Reuses the same real code the grader runs:
lab9.trace_case.investigate for a single trial, lab9.graders for per-grader
verdicts, lab9.gate.check against the committed baseline reports.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

DEMO_DIR = Path(__file__).resolve().parent
SRC_DIR = DEMO_DIR.parent / "src"
sys.path.insert(0, str(SRC_DIR))
os.chdir(SRC_DIR)  # lab9.trace_case / lab9.gate read paths relative to src/, like every CLI entry point

from flask import Flask, jsonify, request, send_from_directory  # noqa: E402

from lab8.db import load_jsonl  # noqa: E402
from lab9 import variants  # noqa: E402
from lab9.eval import load_spec  # noqa: E402
from lab9.trace_case import investigate  # noqa: E402
from lab9.graders import GRADERS  # noqa: E402
from lab9.gate import check as gate_check  # noqa: E402
from pydantic_evals.evaluators import EvaluatorContext  # noqa: E402

app = Flask(__name__, static_folder=None)
variants.register()

CLAIMS = load_jsonl(SRC_DIR / "data" / "public_claims.jsonl")
CLAIM_INDEX = {row["claim_id"]: row for row in CLAIMS}
ITEMS = [json.loads(line) for line in (SRC_DIR / "data" / "eval" / "eval_set_v1.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
TAXONOMY_NAMES = {
    "FM-01": "leaky_trace",
    "FM-02": "ignore_denied",
    "FM-03": "ticket_trust",
    "FM-04": "sum_parts / round_down",
    "FM-05": "pre_deducted",
    "FM-06": "stale_clause",
    "FM-07": "sibling_refund",
    "FM-08": "misreport",
    "FM-09": "cross_principal",
}
SPEC = load_spec(SRC_DIR / "config" / "metric_spec.yaml")


def _grader_verdicts(trial: dict[str, Any], label: dict[str, Any]) -> list[dict[str, Any]]:
    ctx = EvaluatorContext(name="t", inputs={}, metadata=None, expected_output=label, output=trial,
                           duration=0.0, _span_tree=None, attributes={}, metrics={})
    bad_is_true = {"secret_leak", "approval_bypass"}
    out = []
    for metric_id, cls in GRADERS.items():
        if metric_id == "pass_rate":
            continue
        try:
            reason = cls().evaluate(ctx)
        except Exception as e:  # noqa: BLE001
            out.append({"id": metric_id, "ok": None, "detail": f"error: {e}"})
            continue
        value = bool(reason.value)
        ok = (not value) if metric_id in bad_is_true else value
        out.append({"id": metric_id, "ok": ok, "detail": reason.reason})
    return out


@app.get("/")
def index():
    return send_from_directory(DEMO_DIR, "index.html")


@app.get("/api/taxonomy")
def api_taxonomy():
    by_fm: dict[str, list[dict[str, Any]]] = {fm: [] for fm in TAXONOMY_NAMES}
    for item in ITEMS:
        claim = CLAIM_INDEX.get(item["claim_id"], {})
        for fm in item.get("failure_modes") or []:
            by_fm.setdefault(fm, []).append({
                "claim_id": item["claim_id"],
                "item_id": item["item_id"],
                "ticket": claim.get("ticket"),
            })
    return jsonify([
        {"id": fm, "name": name, "claims": by_fm.get(fm, [])}
        for fm, name in TAXONOMY_NAMES.items()
    ])


@app.get("/api/shapes")
def api_shapes():
    from lab8.shapes import SHAPES

    return jsonify(sorted(SHAPES.keys()))


@app.get("/api/trace")
def api_trace():
    claim_id = request.args.get("claim_id", "")
    shape = request.args.get("shape", "swarm")
    seed = int(request.args.get("seed", 11))
    if claim_id not in CLAIM_INDEX:
        return jsonify({"error": f"không tìm thấy claim_id {claim_id!r}"}), 400
    case = investigate(shape, claim_id, seed)
    trial, label = case["trial"], case["label"]
    return jsonify({
        "ticket": CLAIM_INDEX[claim_id].get("ticket"),
        "events": trial["events"],
        "result": trial["result"],
        "snapshot": trial["snapshot"],
        "label": label,
        "lab8_pass": trial["lab8_pass"],
        "lab8_reason": trial["lab8_reason"],
        "graders": _grader_verdicts(trial, label),
    })


@app.get("/api/gate")
def api_gate():
    shape = request.args.get("shape", "fixed")
    report_path = SRC_DIR / "reports" / f"eval_{shape}.json"
    baseline_path = SRC_DIR / "reports" / "baseline_v1.json"
    if not report_path.is_file() or not baseline_path.is_file():
        return jsonify({"error": f"chưa có reports/eval_{shape}.json hoặc baseline_v1.json"}), 404
    pr = json.loads(report_path.read_text(encoding="utf-8"))
    base = json.loads(baseline_path.read_text(encoding="utf-8"))
    blocked, lines = gate_check(pr, base, SPEC)
    return jsonify({
        "pr_run_id": pr["run_id"], "base_run_id": base["run_id"],
        "eval_set_sha": pr["manifest"]["eval_set_sha"],
        "blocked": blocked, "lines": lines, "exit_code": 1 if blocked else 0,
        "metrics": pr["metrics"],
    })


MUTATION_CACHE = SRC_DIR / "reports" / "mutation_scorecard.json"


@app.get("/api/mutation")
def api_mutation():
    """M5-M7 scorecard: every public variant run through the real gate (lab9.mutation.scorecard).
    ~700 trials (5 variant x 28 item x 5 seed) take ~1-2 min on this machine's dev server, too slow
    to click live in front of a class -- so by default this serves the cached result (same function,
    pre-run offline, see README). Pass ?live=1 to recompute for real during Q&A."""
    if request.args.get("live") != "1" and MUTATION_CACHE.is_file():
        data = json.loads(MUTATION_CACHE.read_text(encoding="utf-8"))
        data["cached"] = True
        return jsonify(data)

    from lab9.mutation import scorecard

    spec_v2 = load_spec(SRC_DIR / "config" / "metric_spec_v2.yaml")
    base = json.loads((SRC_DIR / "reports" / "baseline_v2.json").read_text(encoding="utf-8"))
    rows = scorecard(spec_v2, base, None)
    out = [{"variant": name, "expect": want, "got": got, "why": why} for name, want, got, why in rows]
    killed = sum(r["expect"] == r["got"] == "block" for r in out)
    regs = sum(r["expect"] == "block" for r in out)
    fa = sum(r["expect"] == "merge" and r["got"] == "block" for r in out)
    result = {"rows": out, "killed": killed, "regressions": regs, "false_alarms": fa, "cached": False}
    MUTATION_CACHE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5056, debug=False)
