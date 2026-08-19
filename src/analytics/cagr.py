# -----------------------------------------------------
# CAGR Calculation
# -----------------------------------------------------


def calculate_cagr(start_value, end_value, years_available, required_years):
    """
    Calculate CAGR with edge-case handling.

    Returns:
        (cagr_value, flag)
    """

    if years_available < required_years:
        return None, "INSUFFICIENT"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    cagr = ((end_value / start_value) ** (1 / required_years) - 1) * 100

    return round(cagr, 2), None


# -----------------------------------------------------
# Revenue CAGR
# -----------------------------------------------------


def revenue_cagr(start_value, end_value, years_available, years):
    """
    Revenue CAGR wrapper.
    """
    return calculate_cagr(start_value, end_value, years_available, years)


# -----------------------------------------------------
# PAT CAGR
# -----------------------------------------------------


def pat_cagr(start_value, end_value, years_available, years):
    """
    PAT (Net Profit) CAGR wrapper.
    """
    return calculate_cagr(start_value, end_value, years_available, years)


# -----------------------------------------------------
# EPS CAGR
# -----------------------------------------------------


def eps_cagr(start_value, end_value, years_available, years):
    """
    EPS CAGR wrapper.
    """
    return calculate_cagr(start_value, end_value, years_available, years)


# -----------------------------------------------------
# CAGR Summary
# -----------------------------------------------------


def calculate_growth_metrics(data):
    """
    Calculate Revenue, PAT and EPS CAGR
    for 3, 5 and 10 years.

    Returns a dictionary containing both
    CAGR values and flags.
    """

    result = {}

    metrics = {
        "revenue": (data["revenue_start"], data["revenue_end"]),
        "pat": (data["pat_start"], data["pat_end"]),
        "eps": (data["eps_start"], data["eps_end"]),
    }

    for metric_name, (start_value, end_value) in metrics.items():

        for years in (3, 5, 10):

            cagr, flag = calculate_cagr(
                start_value, end_value, data["years_available"], years
            )

            result[f"{metric_name}_cagr_{years}yr"] = cagr
            result[f"{metric_name}_cagr_{years}yr_flag"] = flag

    return result
