# -----------------------------------------------------
# Free Cash Flow
# -----------------------------------------------------


def free_cash_flow(operating_activity, investing_activity):
    """
    Free Cash Flow

    FCF = Operating Cash Flow + Investing Cash Flow

    Investing cash flow is usually negative,
    therefore negative FCF is valid.
    """

    return operating_activity + investing_activity


# -----------------------------------------------------
# CFO Quality Score
# -----------------------------------------------------


def cfo_quality_score(cfo_total, pat_total):
    """
    CFO / PAT Ratio

    Returns:
        ratio, quality_label
    """

    if pat_total == 0:
        return None, None

    ratio = round(cfo_total / pat_total, 2)

    if ratio > 1:
        label = "High Quality"

    elif ratio >= 0.5:
        label = "Moderate"

    else:
        label = "Accrual Risk"

    return ratio, label


# -----------------------------------------------------
# CapEx Intensity
# -----------------------------------------------------


def capex_intensity(investing_activity, sales):
    """
    CapEx Intensity

    abs(CFI) / Sales × 100
    """

    if sales == 0:
        return None, None

    value = round(abs(investing_activity) / sales * 100, 2)

    if value < 3:
        label = "Asset Light"

    elif value <= 8:
        label = "Moderate"

    else:
        label = "Capital Intensive"

    return value, label


# -----------------------------------------------------
# FCF Conversion Rate
# -----------------------------------------------------


def fcf_conversion_rate(free_cash_flow_value, operating_profit):
    """
    FCF Conversion Rate

    FCF / Operating Profit × 100
    """

    if operating_profit == 0:
        return None

    return round((free_cash_flow_value / operating_profit) * 100, 2)


# -----------------------------------------------------
# Capital Allocation Pattern
# -----------------------------------------------------


def capital_allocation_pattern(
    operating_activity, investing_activity, financing_activity, cfo_pat_ratio=None
):
    """
    Classify capital allocation pattern based on
    CFO, CFI and CFF signs.
    """

    cfo_sign = "+" if operating_activity >= 0 else "-"
    cfi_sign = "+" if investing_activity >= 0 else "-"
    cff_sign = "+" if financing_activity >= 0 else "-"

    pattern = (cfo_sign, cfi_sign, cff_sign)

    if pattern == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1:
            label = "Shareholder Returns"
        else:
            label = "Reinvestor"

    elif pattern == ("+", "+", "-"):
        label = "Liquidating Assets"

    elif pattern == ("-", "+", "+"):
        label = "Distress Signal"

    elif pattern == ("-", "-", "+"):
        label = "Growth Funded by Debt"

    elif pattern == ("+", "+", "+"):
        label = "Cash Accumulator"

    elif pattern == ("-", "-", "-"):
        label = "Pre-Revenue"

    elif pattern == ("+", "-", "+"):
        label = "Mixed"

    else:
        label = "Unknown"

    return (cfo_sign, cfi_sign, cff_sign, label)


# -----------------------------------------------------
# Capital Allocation Summary
# -----------------------------------------------------


def generate_capital_allocation_record(row):
    """
    Generate one capital allocation record.

    Returns a dictionary suitable for writing to
    output/capital_allocation.csv.
    """

    fcf = free_cash_flow(row["operating_activity"], row["investing_activity"])

    cfo_ratio, cfo_label = cfo_quality_score(row["cfo_total"], row["pat_total"])

    capex_value, capex_label = capex_intensity(row["investing_activity"], row["sales"])

    conversion = fcf_conversion_rate(fcf, row["operating_profit"])

    cfo_sign, cfi_sign, cff_sign, pattern = capital_allocation_pattern(
        row["operating_activity"],
        row["investing_activity"],
        row["financing_activity"],
        cfo_ratio,
    )

    return {
        "company_id": row["company_id"],
        "year": row["year"],
        "free_cash_flow": fcf,
        "cfo_quality_ratio": cfo_ratio,
        "cfo_quality_label": cfo_label,
        "capex_intensity": capex_value,
        "capex_label": capex_label,
        "fcf_conversion_rate": conversion,
        "cfo_sign": cfo_sign,
        "cfi_sign": cfi_sign,
        "cff_sign": cff_sign,
        "pattern_label": pattern,
    }
