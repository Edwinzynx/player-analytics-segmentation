from common import ROOT,OUT,metrics
from update_readme_metrics import render,START,END
from build_insights_brief import render as brief

def test_readme_metrics_match_source():
    text=(ROOT/'README.md').read_text(encoding='utf-8')
    block=START+text.split(START)[1].split(END)[0]+END
    assert block==render(metrics())

def test_brief_is_generated_from_metrics():
    assert (OUT/'insights_brief.md').read_text(encoding='utf-8')==brief(metrics())

