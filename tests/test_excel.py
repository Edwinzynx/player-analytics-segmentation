import subprocess
import pytest
from openpyxl import load_workbook
from common import metrics,OUT,load_players
from build_excel_workbook import libreoffice,DATA_COLUMNS

def test_workbook_formulas_caches_and_data():
    path=OUT/'excel/player_analytics.xlsx'
    formulas=load_workbook(path,data_only=False)
    cached=load_workbook(path,data_only=True)
    expected=metrics()['excel']['expected_cells']
    for name,cells in expected.items():
        assert formulas[name]._charts
        for address,value in cells.items():
            assert formulas[name][address].data_type=='f'
            assert cached[name][address].value==pytest.approx(value,abs=1e-12)
    assert 'Players' in formulas['Data'].tables
    actual=list(cached['Data'].values)
    assert list(actual[0])==DATA_COLUMNS
    assert [tuple(row) for row in load_players()[DATA_COLUMNS].values.tolist()]==actual[1:]
    formulas.close(); cached.close()

@pytest.mark.skipif(libreoffice() is None, reason='LibreOffice unavailable: native recalculation not verified')
def test_libreoffice_recalculation(tmp_path):
    engine=libreoffice()
    if not engine:
        pytest.skip('LibreOffice unavailable: caches checked, native recalculation not verified')
    source=OUT/'excel/player_analytics.xlsx'
    subprocess.run([engine,'--headless',f'-env:UserInstallation={tmp_path.as_uri()}/profile',
        '--convert-to','xlsx','--outdir',str(tmp_path),str(source)],check=True,timeout=120)
    book=load_workbook(tmp_path/source.name,data_only=True)
    for name,cells in metrics()['excel']['expected_cells'].items():
        for address,value in cells.items():
            assert book[name][address].value==pytest.approx(value,abs=1e-9)
    book.close()

