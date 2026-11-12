"""Replace only the marked metrics block, from the machine-readable source."""
from common import ROOT,metrics

START='<!-- METRICS:START -->'
END='<!-- METRICS:END -->'

def render(m):
    o=m['overall']; a=m['audit']; s=m['segmentation']
    lines=[START,'',
        f"The local raw file has **{a['raw_rows']:,} records**, including **{m['data_quality']['quarantined_rows']}** incomplete trailing record; **{o['n']:,} players** are analyzed. "
        f"It is an exact byte prefix of the declared source (**{a['source_rows']:,} rows**). "
        f"Maximum rounds: **{o['max_rounds']:,}** locally versus **{a['source_max_rounds']:,}** in that source. Valid outliers are retained.",'',
        '| Baseline metric | Result |','|---|---:|',
        f"| D1 retention | {o['d1']:.2%} ({o['d1_n']:,} players) |",
        f"| D7 retention | {o['d7']:.2%} ({o['d7_n']:,} players) |",
        f"| Mean / median rounds | {o['mean_rounds']:.2f} / {o['median_rounds']:.1f} |",
        f"| Total rounds | {o['total_rounds']:,} |",
        f"| D7 conditional on D1 | {o['d7_given_d1']:.2%} |",
        f"| D7-only players | {o['d7_only_n']:,} |",'',
        '| Metric | Gate 30 | Gate 40 | Difference (pp), CI | Two-sided p | One-sided p | Holm p |',
        '|---|---:|---:|---|---:|---:|---:|']
    for name,r in m['ab'].items():
        lines.append(f"| {name} | {r['rate_gate30']:.2%} | {r['rate_gate40']:.2%} | {100*r['difference']:+.3f} [{100*r['ci95'][0]:+.3f}, {100*r['ci95'][1]:+.3f}] | {r['p_two_sided']:.5f} | {r['p_one_sided_gate40_lower']:.5f} | {r['p_holm']:.5f} |")
    lines+=['',
        f"Primary tests are two-sided at alpha **{m['analysis_plan']['alpha']}**, adjusted across D1 and D7 with Holm. "
        f"Intervals are **{m['analysis_plan']['ci_level']:.0%}** marginal Newcombe intervals. "
        'Effects are gate_40 minus gate_30; one-sided alternatives are exploratory gate_40 < gate_30.',
        '',f"**D7: {m['ab']['D7']['conclusion']}.** The data do not justify a definitive rollout or rollback recommendation.",
        '', '| Primary cohort | Players | Size | Rounds share | Mean / median rounds | D1 | D7 |',
        '|---|---:|---:|---:|---|---:|---:|']
    for r in m['profiles']['cohort']:
        lines.append(f"| {r['cohort']} | {r['n']:,} | {r['size_share']:.2%} | {r['rounds_share']:.2%} | {r['mean_rounds']:.2f} / {r['median_rounds']:.1f} | {r['d1']:.2%} | {r['d7']:.2%} |")
    top=m['profiles']['decile'][0]
    lines+=['',
        f"The highest-round decile contributes **{top['rounds_share']:.2%}** of activity. "
        f"Engagement-tier versus D7 association has Cramer's V **{m['association']['cramers_v']:.4f}**, separately from the A/B test.",
        f"Secondary K-means agreement: adjusted Rand index **{s['ari_cohort']:.4f}** with retention cohorts and **{s['ari_cohort_tier']:.4f}** with cohort-by-tier groups. "
        'Retention is included in those model features, so segment retention is partly true by construction.',
        '',END]
    return '\n'.join(lines)

def main():
    path=ROOT/'README.md'; text=path.read_text(encoding='utf-8-sig')
    block=render(metrics())
    if START in text:
        assert text.count(START)==text.count(END)==1
        before,rest=text.split(START); _,after=rest.split(END)
        text=before+block+after
    else:
        text+='\n\n'+block+'\n'
    path.write_text(text,encoding='utf-8')

if __name__=='__main__':
    main()

