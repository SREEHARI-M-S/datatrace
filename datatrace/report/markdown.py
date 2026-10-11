from __future__ import annotations

from datatrace.analysis.root_cause import RootCauseFinding


def explain_report_markdown(
    record_id: str,
    lineage: list[str],
    finding: RootCauseFinding | None,
) -> str:
    lines = [
        "# DataTrace forensics report",
        "",
        f"**Record:** `{record_id}`",
        "",
        "## Lineage",
        "",
    ]
    for dataset in lineage:
        lines.append(f"- {dataset}")
    if finding:
        lines.extend(
            [
                "",
                "## Root cause",
                "",
                finding.summary,
                "",
                f"- Transformation: `{finding.transformation}`",
                f"- Operation: `{finding.evidence.get('operation', 'unknown')}`",
            ],
        )
    return "\n".join(lines) + "\n"
