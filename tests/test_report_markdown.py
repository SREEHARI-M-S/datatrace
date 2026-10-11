from datatrace.analysis.root_cause import RootCauseFinding
from datatrace.report.markdown import explain_report_markdown


def test_explain_markdown() -> None:
    finding = RootCauseFinding(
        transformation="identity_mapping.sql",
        summary="Value changed",
        evidence={"operation": "UPDATE"},
    )
    md = explain_report_markdown("183729", ["raw_customer", "billing_export"], finding)
    assert "183729" in md
    assert "identity_mapping.sql" in md
