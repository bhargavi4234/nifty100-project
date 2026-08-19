import pandas as pd

from src.etl.loader import TABLE_MAP, clean_columns


def test_loader_has_all_12_files():
    assert len(TABLE_MAP) == 12


def test_companies_mapping():
    assert TABLE_MAP["companies.xlsx"] == "companies"


def test_sectors_mapping():
    assert TABLE_MAP["sectors.xlsx"] == "sectors"


def test_peer_groups_mapping():
    assert TABLE_MAP["peer_groups.xlsx"] == "peer_groups"


def test_analysis_mapping():
    assert TABLE_MAP["analysis.xlsx"] == "analysis"


def test_documents_mapping():
    assert TABLE_MAP["documents.xlsx"] == "documents"


def test_profitandloss_mapping():
    assert TABLE_MAP["profitandloss.xlsx"] == "profitandloss"


def test_balancesheet_mapping():
    assert TABLE_MAP["balancesheet.xlsx"] == "balancesheet"


def test_cashflow_mapping():
    assert TABLE_MAP["cashflow.xlsx"] == "cashflow"


def test_clean_columns():
    df = pd.DataFrame(columns=[" Company Name ", "Return On Equity"])

    result = clean_columns(df)

    assert list(result.columns) == [
        "company_name",
        "return_on_equity",
    ]
