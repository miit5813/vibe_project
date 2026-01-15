from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

import pandas as pd


REQUIRED_COLUMNS = {"student_id", "group", "final_score"}


class DataValidationError(ValueError):
    """Raised when the input student data does not satisfy expected constraints."""


def load_student_data(path: str) -> pd.DataFrame:
    """Load student performance data from a CSV file.

    The CSV is expected to contain at least the following columns:
    - student_id: unique identifier of the student
    - group: group or class identifier
    - final_score: final numeric score in range [0, 1] or [0, 100]
    """
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise DataValidationError(f"Missing required columns: {', '.join(sorted(missing))}")

    return df


def _normalise_scores(df: pd.DataFrame, score_column: str = "final_score") -> pd.Series:
    """Return scores normalised to [0, 1] regardless of original scale."""
    scores = df[score_column].astype(float)
    if scores.max() > 1.0:
        return scores / 100.0
    return scores


def compute_basic_stats(df: pd.DataFrame, score_column: str = "final_score") -> pd.DataFrame:
    """Compute simple descriptive statistics by group.

    Returns a DataFrame with one row per group and columns:
    - count
    - mean_score
    - min_score
    - max_score
    """
    scores = _normalise_scores(df, score_column=score_column)
    grouped = scores.groupby(df["group"])

    stats = pd.DataFrame(
        {
            "count": grouped.size(),
            "mean_score": grouped.mean(),
            "min_score": grouped.min(),
            "max_score": grouped.max(),
        }
    )

    return stats.sort_index()


def detect_at_risk_students(
    df: pd.DataFrame,
    score_column: str = "final_score",
    threshold: float = 0.6,
) -> pd.DataFrame:
    """Return subset of students whose normalised score is below a threshold."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be in [0.0, 1.0]")

    scores = _normalise_scores(df, score_column=score_column)
    mask = scores < threshold
    return df.loc[mask].copy()


@dataclass
class Recommendation:
    """Simple recommendation for a group based on mean score."""

    group: str
    mean_score: float
    recommendation: str


def build_recommendations(
    df: pd.DataFrame,
    score_column: str = "final_score",
    low_threshold: float = 0.6,
    high_threshold: float = 0.8,
) -> List[Recommendation]:
    """Generate simple textual recommendations per group.

    - mean < low_threshold  → "increase support and monitor weekly"
    - low_threshold <= mean < high_threshold → "monitor progress"
    - mean >= high_threshold → "performance is stable"
    """
    stats = compute_basic_stats(df, score_column=score_column)

    recommendations: List[Recommendation] = []
    for group, row in stats.iterrows():
        mean_score = float(row["mean_score"])

        if mean_score < low_threshold:
            text = "increase support and monitor weekly"
        elif mean_score < high_threshold:
            text = "monitor progress"
        else:
            text = "performance is stable"

        recommendations.append(
            Recommendation(group=str(group), mean_score=mean_score, recommendation=text)
        )

    return recommendations


def format_recommendations(recs: Iterable[Recommendation]) -> str:
    """Format recommendations in a human-readable table-like text."""
    lines: List[str] = ["Group\tMean score\tRecommendation"]

    for rec in recs:
        lines.append(f"{rec.group}\t{rec.mean_score:.2f}\t{rec.recommendation}")

    return "\n".join(lines)


