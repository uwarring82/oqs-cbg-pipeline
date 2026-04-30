"""Run all DG-1 benchmark cards and write evidence artefacts.

Usage:
    python scripts/run_dg1_verdict.py

Writes JSON evidence files to ``benchmarks/results/<card_filename>_result.json``
and a top-level summary to ``benchmarks/results/DG-1_summary.json``. Prints
a verdict summary to stdout. Returns exit code 0 on PASS, 1 on FAIL.

This is the orchestrator script for DG-1 work plan v0.1.4 §4 Phase D
Commit D.1. The card YAMLs themselves are updated in a separate step
(via in-place edits, preserving comments and structure) once the
evidence files are committed; this script does not mutate the card
files on disk because the YAML library used here (PyYAML) does not
preserve comments. See SCHEMA.md §Card lifecycle for the verdict-commit
protocol.

Exit code:
    0 — DG-1 PASS (all three cards verdict = PASS)
    1 — DG-1 FAIL-WITH-CAUSE (any card verdict != PASS, or runner error)

Anchor: DG-1 work plan v0.1.4 §4 Phase D; SCHEMA.md v0.1.2 §Card lifecycle.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CARDS_DIR = REPO_ROOT / "benchmarks" / "benchmark_cards"
RESULTS_DIR = REPO_ROOT / "benchmarks" / "results"

# Allow running from repo root without `pip install -e .`. The package
# layout (cbg/, models/, numerical/, reporting/, benchmarks/) is at
# REPO_ROOT; prepending it to sys.path makes the imports below resolve.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from reporting import benchmark_card as bc  # noqa: E402

# DG-1 cards in canonical order (Card A1 first, then A3, A4).
DG1_CARD_FILES = (
    "A1_closed-form-K_v0.1.1.yaml",
    "A3_pure-dephasing_v0.1.1.yaml",
    "A4_sigma-x-thermal_v0.1.1.yaml",
)


def _evidence_filename(card_file: str) -> str:
    """E.g. 'A1_closed-form-K_v0.1.1.yaml' → 'A1_closed-form-K_v0.1.1_result.json'."""
    stem = Path(card_file).stem
    return f"{stem}_result.json"


def run_one_card(card_file: str) -> dict:
    """Run a single card; write its evidence JSON; return a summary dict."""
    card_path = CARDS_DIR / card_file
    print(f"Running {card_file}...")
    card = bc.load_card(card_path)
    result = bc.run_card(card)

    evidence_filename = _evidence_filename(card_file)
    evidence_path = RESULTS_DIR / evidence_filename

    evidence = {
        "card_id": card.card_id,
        "card_version": card.version,
        "card_path": str(card_path.relative_to(REPO_ROOT)),
        "schema_version": card.schema_version,
        "ledger_entry": card.ledger_entry,
        "verdict": result.verdict,
        "runner_version": result.runner_version,
        "computed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "test_case_results": [
            {
                "name": tcr.name,
                "passed": tcr.passed,
                "error": tcr.error,
                "threshold": tcr.threshold,
                "notes": tcr.notes,
            }
            for tcr in result.test_case_results
        ],
    }
    with open(evidence_path, "w") as f:
        json.dump(evidence, f, indent=2, ensure_ascii=False)

    print(f"  verdict = {result.verdict}")
    print(f"  evidence -> benchmarks/results/{evidence_filename}")
    for tcr in result.test_case_results:
        print(
            f"    [{tcr.name}] passed={tcr.passed} "
            f"error={tcr.error:.3e} threshold={tcr.threshold:.0e}"
        )
    return {
        "card_id": card.card_id,
        "card_version": card.version,
        "card_path": str(card_path.relative_to(REPO_ROOT)),
        "evidence_path": f"benchmarks/results/{evidence_filename}",
        "verdict": result.verdict,
        "runner_version": result.runner_version,
    }


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("DG-1 verdict runner")
    print("=" * 60)
    print(f"Cards: {len(DG1_CARD_FILES)}")
    print(f"Runner version: {bc.__version__}")
    print()

    cards_summary = []
    for card_file in DG1_CARD_FILES:
        cards_summary.append(run_one_card(card_file))
        print()

    all_pass = all(c["verdict"] == "PASS" for c in cards_summary)
    overall = "PASS" if all_pass else "FAIL-WITH-CAUSE"

    summary = {
        "dg": "DG-1",
        "verdict": overall,
        "runner_version": bc.__version__,
        "computed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ledger_anchor": "CL-2026-005 v0.4 (Entries 1, 3, 4 — DG-1 sub-cases)",
        "plan_anchor": "plans/dg-1-work-plan_v0.1.4.md",
        "schema_anchor": "benchmarks/benchmark_cards/SCHEMA.md (v0.1.2)",
        "cards": cards_summary,
    }
    summary_path = RESULTS_DIR / "DG-1_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print(f"DG-1 verdict: {overall}")
    print(f"Summary -> benchmarks/results/DG-1_summary.json")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
