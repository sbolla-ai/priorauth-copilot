"""Command line: review one case.  Example:  priorauth review PA-001 --extractor baseline"""
from __future__ import annotations

import argparse
import json
import sys

from .agent import make_extractor, review
from .data import load_cases, load_policies


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="priorauth", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("review", help="Review one synthetic case")
    r.add_argument("case_id")
    r.add_argument("--extractor", choices=["baseline", "llm"], default="baseline")
    r.add_argument("--provider", choices=["anthropic", "openai"], default="anthropic")
    r.add_argument("--model", default=None)
    sub.add_parser("list", help="List synthetic cases")
    args = parser.parse_args(argv)

    cases = {c["case_id"]: c for c in load_cases()}
    if args.cmd == "list":
        for c in cases.values():
            print(f"{c['case_id']}  {c['policy_id']:<18} expected={c['label']['decision']:<19} tags={','.join(c['label']['tags'])}")
        return 0

    if args.case_id not in cases:
        print(f"Unknown case {args.case_id}", file=sys.stderr)
        return 2
    case = cases[args.case_id]
    extractor = make_extractor(args.extractor, args.provider, args.model)
    rec = review(case, load_policies()[case["policy_id"]], extractor)
    print(json.dumps(rec.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
