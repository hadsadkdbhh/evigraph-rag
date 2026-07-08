from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from evigraph.retrieval_portfolio import (
    build_portfolio_rows,
    read_csv,
    render_portfolio_report,
    write_csv,
)


def main() -> int:
    args = _parse_args()
    primary_rows = read_csv(args.primary_csv)
    candidate_rows = read_csv(args.candidate_csv)
    rows = build_portfolio_rows(
        primary_rows,
        candidate_rows,
        primary_name=args.primary_name,
        candidate_name=args.candidate_name,
        policy=args.policy,
    )
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    portfolio_csv = output_dir / args.output_csv_name
    report_path = output_dir / args.report_name
    write_csv(portfolio_csv, rows)
    report_path.write_text(
        render_portfolio_report(
            rows,
            title=args.title,
            primary_name=args.primary_name,
            candidate_name=args.candidate_name,
        ),
        encoding="utf-8",
    )
    print(
        {
            "portfolio_csv": str(portfolio_csv),
            "report": str(report_path),
        }
    )
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a no-gold retrieval portfolio from two completed evaluation CSVs.")
    parser.add_argument("--primary-csv", required=True)
    parser.add_argument("--candidate-csv", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--primary-name", default="bm25")
    parser.add_argument("--candidate-name", default="neural_hybrid")
    parser.add_argument("--policy", default="fallback_numeric_calculation", choices=["fallback_numeric_calculation", "strict_supported_fallback"])
    parser.add_argument("--title", default="EviGraph Retrieval Portfolio")
    parser.add_argument("--output-csv-name", default="portfolio.csv")
    parser.add_argument("--report-name", default="portfolio_report.md")
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
