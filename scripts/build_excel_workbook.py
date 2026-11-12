"""Build an Excel Table, live summaries and native charts, with metric-derived caches."""
from datetime import datetime
import shutil
import subprocess
from pathlib import Path
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
from common import ROOT, OUT, metrics, load_players, update_metrics, digest, TIERS

SHEETS={'tier':'Retention by tier','version':'Retention by version','cohort':'Retention by cohort','decile':'Pareto'}
DATA_COLUMNS=['userid','version','sum_gamerounds','retention_1','retention_7','tier','cohort','decile']

def libreoffice():
    candidates=[shutil.which('soffice'),r'C:/Program Files/LibreOffice/program/soffice.exe',
                r'C:/Program Files (x86)/LibreOffice/program/soffice.exe']
    return next((str(p) for p in candidates if p and Path(p).exists()),None)

def main():
    m=metrics(); df=load_players()[DATA_COLUMNS]
    dest=OUT/'excel/player_analytics.xlsx'; dest.parent.mkdir(parents=True,exist_ok=True)
    book=xlsxwriter.Workbook(dest)
    book.set_properties({'title':'Product retention and activity analysis',
        'author':'Portfolio analytics','created':datetime(2020,1,1)})
    book.set_calc_mode('auto')
    title=book.add_format({'font_name':'Arial','font_size':16,'bold':True,'font_color':'#233e56'})
    header=book.add_format({'font_name':'Arial','font_size':11,'bold':True,'bg_color':'#233e56',
        'font_color':'white','text_wrap':True,'valign':'vcenter'})
    number=book.add_format({'font_name':'Arial','num_format':'#,##0.00'})
    integer=book.add_format({'font_name':'Arial','num_format':'#,##0'})
    pct=book.add_format({'font_name':'Arial','num_format':'0.00%'})
    note=book.add_format({'font_name':'Arial','font_size':11,'text_wrap':True,'valign':'top'})
    expected={}
    for key,sheet_name in SHEETS.items():
        ws=book.add_worksheet(sheet_name); ws.hide_gridlines(2)
        ws.set_tab_color('#233e56'); ws.write(1,0,sheet_name,title)
        columns=[key,'Players','Mean rounds','D1 rate','D7 rate','Total rounds','Player share','Rounds share']
        if key=='decile': columns+=['Cumulative share']
        ws.write_row(3,0,columns,header); ws.set_row(3,32)
        ws.set_column(0,0,20); ws.set_column(1,len(columns)-1,17)
        rows=m['profiles'][key]
        if key=='tier': rows=sorted(rows,key=lambda r:TIERS.index(r[key]))
        expected[sheet_name]={}
        for row_i,row in enumerate(rows,4):
            excel=row_i+1; criterion=f'$A{excel}'; label=row[key]
            ws.write(row_i,0,label)
            formulas=[
                (f'=COUNTIFS(Players[{key}],{criterion})',row['n'],integer),
                (f'=IF(B{excel}=0,"n.a.",AVERAGEIFS(Players[sum_gamerounds],Players[{key}],{criterion}))',row['mean_rounds'],number),
                (f'=IF(B{excel}=0,"n.a.",AVERAGEIFS(Players[retention_1],Players[{key}],{criterion}))',row['d1'],pct),
                (f'=IF(B{excel}=0,"n.a.",AVERAGEIFS(Players[retention_7],Players[{key}],{criterion}))',row['d7'],pct),
                (f'=SUMIFS(Players[sum_gamerounds],Players[{key}],{criterion})',row['rounds'],integer),
                (f'=B{excel}/COUNTA(Players[userid])',row['size_share'],pct),
                (f'=IF(SUM(Players[sum_gamerounds])=0,"n.a.",F{excel}/SUM(Players[sum_gamerounds]))',row['rounds_share'],pct)]
            if key=='decile':
                formulas.append((f'=SUM($H$5:H{excel})',row['cumulative_rounds_share'],pct))
            for col_i,(formula,value,fmt) in enumerate(formulas,1):
                ws.write_formula(row_i,col_i,formula,fmt,value)
                expected[sheet_name][xl_rowcol_to_cell(row_i,col_i)]=value
        chart=book.add_chart({'type':'column'})
        for col in ([7] if key=='decile' else [3,4]):
            chart.add_series({'name':[sheet_name,3,col],
                'categories':[sheet_name,4,0,3+len(rows),0],
                'values':[sheet_name,4,col,3+len(rows),col]})
        if key=='decile':
            line=book.add_chart({'type':'line'})
            line.add_series({'name':[sheet_name,3,8],'categories':[sheet_name,4,0,3+len(rows),0],
                'values':[sheet_name,4,8,3+len(rows),8],'line':{'color':'#bb7226'}})
            chart.combine(line)
        chart.set_title({'name':'Activity concentration' if key=='decile' else 'Observed retention'})
        chart.set_y_axis({'num_format':'0%','min':0,'max':1})
        chart.set_legend({'position':'bottom'}); chart.set_size({'width':740,'height':350})
        ws.insert_chart(len(rows)+6,0,chart)
        ws.set_landscape(); ws.fit_to_pages(1,1)
        ws.print_area(0,0,len(rows)+25,len(columns)-1)
        ws.set_paper(9)
    ws=book.add_worksheet('Data'); ws.hide_gridlines(2); ws.freeze_panes(1,2)
    ws.set_column(0,0,14); ws.set_column(1,len(DATA_COLUMNS)-1,19)
    ws.add_table(0,0,len(df),len(DATA_COLUMNS)-1,{'name':'Players','style':'Table Style Medium 2',
        'columns':[{'header':c} for c in DATA_COLUMNS],'data':df.values.tolist()})
    readme=book.add_worksheet('README'); readme.hide_gridlines(2)
    readme.set_column(0,0,110); readme.write(1,0,'Workbook guide',title)
    text=[
        'Purpose: describe retention, assigned-version performance and activity concentration in Cookie Cats.',
        'Source: '+m['audit']['source_url'],
        f"Local raw SHA-256: {m['audit']['raw_sha256']}. Accepted players: {m['overall']['n']:,}.",
        'The local file is a truncated prefix. Its known incomplete final row is quarantined. All valid outliers are retained.',
        f"Rounds cover the stated {m['data_contract']['observation_days']}-day window. D1 and D7 are supplied return flags. No timestamps or revenue are available.",
        'Cohorts: none = neither flag; D1 only; D7 only; both. Cohort retention rates are true by definition, not predictive validation.',
        'Tiers use the documented inclusive upper bounds: '+', '.join(str(x) for x in m['data_contract']['tier_bounds'])+'; the final tier is strictly higher.',
        'Summary sheets contain live COUNTIFS, AVERAGEIFS and SUMIFS formulas over the Players Excel Table. Native charts reference these summaries.',
        'Cached formula results are generated from metrics.json for preview. Excel recalculates on opening. Caches are not evidence of native-engine recalculation.',
        'Change numeric inputs in Data to recalculate summaries. Cohort, tier and decile labels are baseline Python classifications: rerun the pipeline to refresh them after input changes.',
        'Deciles descend by rounds with userid as tie-breaker. Cumulative share is measured from highest to lowest activity.',
        'To add a PivotTable: select a cell in Data; choose Insert > PivotTable; select Players as source and New Worksheet.',
        'Drag cohort or tier to Rows, version to Columns, userid to Values (Count), and retention_1 / retention_7 to Values (Average).',
        'Format retention values as percentages. Add sum_gamerounds as Sum or Average. Use Insert Slicer for version, tier or cohort.',
        'After changing source data, choose Data > Refresh All. This workbook contains no prebuilt PivotTables.',
        'Post-assignment cohort/tier comparisons are descriptive. Use the full-population statistical report for A/B decisions.',
        'Recalculation validation: '+('LibreOffice available; automated parity test can run.' if libreoffice() else 'SKIPPED: LibreOffice is not installed. Open in Excel to recalculate.')]
    for i,t in enumerate(text,4):
        readme.write(i,0,t,note); readme.set_row(i,42 if len(t)>145 else 32)
    readme.set_tab_color('#8095a6'); readme.set_landscape(); readme.fit_to_pages(1,2)
    readme.print_area(0,0,len(text)+5,0)
    book.close()
    update_metrics(excel={'path':str(dest.relative_to(ROOT)).replace('\\','/'),
        'expected_cells':expected,'data_sha256':digest(ROOT/'data/player_segments.csv'),
        'native_recalculation':'available' if libreoffice() else 'skipped: LibreOffice unavailable',
        'has_live_formulas':True,'has_native_charts':True,'has_pivot_tables':False})
    print(dest)

if __name__=='__main__':
    main()

