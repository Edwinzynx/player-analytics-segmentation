from common import ROOT,OUT,metrics
from update_readme_metrics import render,START,END
from build_insights_brief import render as brief

def test_readme_metrics_match_source():
    text=(ROOT/'README.md').read_text(encoding='utf-8')
    block=START+text.split(START)[1].split(END)[0]+END
    assert block==render(metrics())

def test_brief_is_generated_from_metrics():
    assert (OUT/'insights_brief.md').read_text(encoding='utf-8')==brief(metrics())

def test_methodology_and_comparison_are_generated():
    from build_documentation import render_methodology,render_comparison,render_audit_verified
    assert (ROOT/'docs/methodology.md').read_text(encoding='utf-8')==render_methodology(metrics())
    assert (OUT/'metric_comparison.md').read_text(encoding='utf-8')==render_comparison(metrics())
    assert (ROOT/'docs/audit_notes.md').read_text(encoding='utf-8').endswith(render_audit_verified(metrics()))

