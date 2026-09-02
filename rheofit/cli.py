"""Command-line interface for rheofit (``rheofit`` / ``python -m rheofit``)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analysis import analyze, list_models, print_steps
from .io import DEMO_SAMPLE_NAME, demo_source


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="rheofit",
        description="Fit a TRIOS JSON flow curve and produce a scorecard "
                    "(PNG + CSV by default, optionally PowerPoint).",
    )
    p.add_argument(
        "json_file",
        nargs="?",
        default=None,
        help="Path or HTTP(S) URL to a TA Instruments TRIOS JSON file",
    )
    p.add_argument(
        "--demo",
        action="store_true",
        help="Use the demo TRIOS JSON bundled with the library "
             "(falls back to the online demo URL if the file is missing).",
    )
    p.add_argument(
        "--steps", nargs="+", type=int, default=None, metavar="N",
        help="Step indices to analyze (e.g. --steps 1 3). "
             "Omit to list available steps and exit.",
    )
    p.add_argument(
        "--model", default=None, choices=list_models(),
        help="Rheological model to fit",
    )
    p.add_argument(
        "--labels", nargs="+", default=None, metavar="LABEL",
        help="Human-readable label per step (e.g. --labels 25C 40C). "
             "Must match number of --steps. Defaults to 'Step N'.",
    )
    p.add_argument(
        "--effort", default="thorough", choices=["fast", "normal", "thorough"],
        help="Global-search intensity: number of multi-start seeds explored "
             "before the tight polish (default: thorough).",
    )
    p.add_argument(
        "--seed", type=int, default=0,
        help="Random seed for the Sobol multi-start, for reproducible fits.",
    )
    p.add_argument(
        "--sample-name", default=None,
        help="Optional output sample name override (useful for URL inputs).",
    )
    p.add_argument(
        "--output", default="png_csv", choices=["png_csv", "pptx", "both", "none"],
        help="Artifact mode: png_csv (default), pptx, both, or none (fit only).",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        if not args.demo and not args.json_file:
            print("[!] Provide <json_file> or use --demo")
            return 2

        source = demo_source() if args.demo else args.json_file
        sample_name = args.sample_name
        if args.demo and not sample_name:
            sample_name = DEMO_SAMPLE_NAME

        if args.steps is None or args.model is None:
            print_steps(source)
            if args.steps is None:
                print("Re-run with --steps <indices> --model <name>")
                return 0

        analyze(
            source=source,
            steps=args.steps,
            model=args.model,
            labels=args.labels,
            effort=args.effort,
            seed=args.seed,
            output=args.output,
            sample_name=sample_name,
            results_base=Path.cwd() if args.demo else None,
        )
        return 0
    except (RuntimeError, ValueError) as exc:
        print(f"[!] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
