import argparse
from pathlib import Path

from .performance_analyzer import (
    build_recommendations,
    compute_basic_stats,
    detect_at_risk_students,
    format_recommendations,
    load_student_data,
)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Student Performance Analyzer — simple learning analytics tool."
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        required=True,
        help="Path to a CSV file with student performance data.",
    )
    parser.add_argument(
        "--score-column",
        type=str,
        default="final_score",
        help="Name of the score column in the CSV file (default: final_score).",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Compute and print basic statistics by group.",
    )
    parser.add_argument(
        "--at-risk",
        action="store_true",
        help="Print students at risk of failing.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.6,
        help="Threshold for at-risk students in normalised score [0, 1].",
    )
    parser.add_argument(
        "--recommendations",
        action="store_true",
        help="Generate textual recommendations by group.",
    )

    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    csv_path = Path(args.input)

    if not csv_path.exists():
        raise SystemExit(f"Input file not found: {csv_path}")

    df = load_student_data(str(csv_path))
    print(f"Loaded {len(df)} student records from {csv_path}")

    if args.summary:
        print("\n=== Basic statistics by group ===")
        stats = compute_basic_stats(df, score_column=args.score_column)
        print(stats)

    if args.at_risk:
        print(f"\n=== At-risk students (threshold={args.threshold:.2f}) ===")
        at_risk_df = detect_at_risk_students(
            df, score_column=args.score_column, threshold=args.threshold
        )
        print(f"Found {len(at_risk_df)} students at risk of failing.")
        if not at_risk_df.empty:
            print(at_risk_df[["student_id", "group", args.score_column]].head())

    if args.recommendations:
        print("\n=== Recommendations by group ===")
        recs = build_recommendations(df, score_column=args.score_column)
        print(format_recommendations(recs))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


