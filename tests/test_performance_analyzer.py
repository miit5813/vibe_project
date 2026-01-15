import pandas as pd
import pytest

from src.performance_analyzer import (
    DataValidationError,
    build_recommendations,
    compute_basic_stats,
    detect_at_risk_students,
    load_student_data,
)


def test_load_student_data_missing_columns(tmp_path):
    csv_path = tmp_path / "students.csv"
    pd.DataFrame({"student_id": [1], "final_score": [0.5]}).to_csv(csv_path, index=False)

    try:
        load_student_data(str(csv_path))
    except DataValidationError as exc:
        assert "Missing required columns" in str(exc)
    else:
        raise AssertionError("DataValidationError was not raised for missing columns")


def test_compute_basic_stats_groups_and_means():
    df = pd.DataFrame(
        {
            "student_id": [1, 2, 3, 4],
            "group": ["G1", "G1", "G2", "G2"],
            "final_score": [0.5, 0.7, 0.9, 1.0],
        }
    )

    stats = compute_basic_stats(df)

    assert list(stats.index) == ["G1", "G2"]
    assert stats.loc["G1", "count"] == 2
    assert stats.loc["G2", "count"] == 2
    assert stats.loc["G1", "mean_score"] == pytest.approx(0.6, rel=1e-6)
    assert stats.loc["G2", "mean_score"] == pytest.approx(0.95, rel=1e-6)


def test_detect_at_risk_students_threshold_and_scaling():
    df = pd.DataFrame(
        {
            "student_id": [1, 2, 3],
            "group": ["G1", "G1", "G2"],
            "final_score": [40, 75, 95],  # will be scaled to [0, 1]
        }
    )

    at_risk = detect_at_risk_students(df, threshold=0.6)
    assert len(at_risk) == 1
    assert at_risk.iloc[0]["student_id"] == 1


def test_build_recommendations_texts():
    df = pd.DataFrame(
        {
            "student_id": [1, 2, 3],
            "group": ["G1", "G2", "G3"],
            "final_score": [0.4, 0.7, 0.9],
        }
    )

    recs = build_recommendations(df)
    by_group = {r.group: r for r in recs}

    assert "increase support" in by_group["G1"].recommendation
    assert "monitor" in by_group["G2"].recommendation
    assert "stable" in by_group["G3"].recommendation


