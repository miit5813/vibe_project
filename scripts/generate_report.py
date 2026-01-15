from pathlib import Path
from datetime import datetime

from src.performance_analyzer import (
    build_recommendations,
    compute_basic_stats,
    detect_at_risk_students,
    format_recommendations,
    load_student_data,
)


def generate_report(data_path: str = "data/sample_students.csv", reports_dir: str = "reports") -> Path:
    df = load_student_data(data_path)

    stats = compute_basic_stats(df)
    at_risk = detect_at_risk_students(df)
    recs = build_recommendations(df)

    reports_path = Path(reports_dir)
    reports_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = reports_path / f"student_performance_report_{timestamp}.md"

    with report_file.open("w", encoding="utf-8") as f:
        f.write("# Daily Student Performance Report\n\n")
        f.write(f"Generated at: {timestamp} UTC\n\n")

        f.write("## Basic statistics by group\n\n")
        f.write(stats.to_markdown() + "\n\n")

        f.write("## At-risk students (default threshold=0.6)\n\n")
        if at_risk.empty:
            f.write("No students at risk based on the current threshold.\n\n")
        else:
            f.write(at_risk[["student_id", "group", "final_score"]].to_markdown() + "\n\n")

        f.write("## Recommendations by group\n\n")
        f.write("```\n")
        f.write(format_recommendations(recs))
        f.write("\n```\n")

    return report_file


if __name__ == "__main__":
    path = generate_report()
    print(f"Report generated at: {path}")


