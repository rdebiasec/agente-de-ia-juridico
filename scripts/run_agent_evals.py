#!/usr/bin/env python3
"""Corre evals deterministas y, opcionalmente, un prompt canary shadow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agents.evals import compare_prompt_canary, run_eval_suite  # noqa: E402
from src.config_store import load_prompt_text  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Eval suite de agentes y canary shadow de prompt."
    )
    parser.add_argument("--eval-set", type=Path, default=None)
    parser.add_argument(
        "--candidate",
        type=Path,
        help="Prompt candidato del Gerente. No se publica ni activa.",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--fail-under", type=float, default=1.0)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.candidate:
        baseline = load_prompt_text("coordinador_expediente_penal")
        candidate = args.candidate.read_text(encoding="utf-8")
        report = compare_prompt_canary(
            agent_id="coordinador_expediente_penal",
            baseline_prompt=baseline,
            candidate_prompt=candidate,
            eval_path=args.eval_set,
        )
        payload = report.to_dict()
        score = report.eval_report.score
        safe = report.recommended_action == "eligible_for_human_review"
    else:
        report = run_eval_suite(args.eval_set)
        payload = report.to_dict()
        score = report.score
        safe = True

    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            f"Eval score: {score:.1%} "
            f"({payload['eval_report']['passed'] if args.candidate else payload['passed']}/"
            f"{payload['eval_report']['total'] if args.candidate else payload['total']})"
        )
        categories = (
            payload["eval_report"]["category_scores"]
            if args.candidate
            else payload["category_scores"]
        )
        for category, category_score in categories.items():
            print(f"- {category}: {category_score:.1%}")
        if args.candidate:
            print(f"Canary: {payload['recommended_action']}")
            if payload["security_regressions"]:
                print(
                    "Regresiones de seguridad: "
                    + ", ".join(payload["security_regressions"])
                )

    return 0 if score >= args.fail_under and safe else 1


if __name__ == "__main__":
    raise SystemExit(main())
