import pandas as pd
import numpy as np

# This file centralizes the DCF valuation logic to be shared across pages.

# Hardcoded default assumptions for the static "Implied Price" calculation
DEFAULT_FORECAST_ASSUMPTIONS = {
    'revenue_y0': 5834554372,
    'revenue_growth': [0.21] * 10, #[0.25, 0.22, 0.20, 0.18, 0.15, 0.12, 0.10, 0.08, 0.06, 0.05],
    'ebitda_margin': [0.55] * 10,
    'tax_rate': [0.3] * 10,
    'da_percent_revenue': [0.1] * 10,
    'capex_percent_revenue': [0.042] * 10,
    'nwc_percent_revenue': [0.011] * 10,
    'net_debt': 1572529949,
    'shares_outstanding':  333323673,
}
DEFAULT_TERMINAL_ASSUMPTIONS = {'wacc': 0.09, 'terminal_growth_rate': 0.025}


def perform_dcf_calculation(terminal_assumptions, forecast_assumptions):
    """
    Performs a DCF calculation with a given set of assumptions.
    Returns a tuple of: (df, enterprise_value, equity_value, implied_share_price, terminal_value, pv_terminal_value)
    """
    years = list(range(1, 11))
    df = pd.DataFrame(index=years)
    
    # --- Revenue ---
    revenue = [forecast_assumptions['revenue_y0'] * (1 + forecast_assumptions['revenue_growth'][0])]
    for i in range(1, 10):
        revenue.append(revenue[i-1] * (1 + forecast_assumptions['revenue_growth'][i]))
    df['Revenue'] = revenue
    
    # --- FCFF Calculations ---
    df['EBITDA'] = df['Revenue'] * np.array(forecast_assumptions['ebitda_margin'])
    df['D&A'] = df['Revenue'] * np.array(forecast_assumptions['da_percent_revenue'])
    df['EBIT'] = df['EBITDA'] - df['D&A']
    df['NOPAT'] = df['EBIT'] * (1 - np.array(forecast_assumptions['tax_rate']))
    df['CapEx'] = df['Revenue'] * np.array(forecast_assumptions['capex_percent_revenue'])
    df['Change in NWC'] = df['Revenue'] * np.array(forecast_assumptions['nwc_percent_revenue'])
    df['FCF'] = df['NOPAT'] + df['D&A'] - df['CapEx'] - df['Change in NWC']
    
    # --- Terminal Value ---
    if (terminal_assumptions['wacc'] - terminal_assumptions['terminal_growth_rate']) == 0:
        terminal_value = 0
    else:
        fcf_y10 = df['FCF'].iloc[-1]
        terminal_value = (fcf_y10 * (1 + terminal_assumptions['terminal_growth_rate'])) / (terminal_assumptions['wacc'] - terminal_assumptions['terminal_growth_rate'])

    # --- Present Value Calculations ---
    df['PV Factor'] = [(1 / (1 + terminal_assumptions['wacc'])) ** year for year in years]
    df['PV of FCF'] = df['FCF'] * df['PV Factor']
    
    pv_terminal_value = terminal_value * df['PV Factor'].iloc[-1]
    enterprise_value = df['PV of FCF'].sum() + pv_terminal_value
    
    # --- Final Share Price ---
    equity_value = enterprise_value - forecast_assumptions['net_debt']
    implied_share_price = equity_value / forecast_assumptions['shares_outstanding'] if forecast_assumptions['shares_outstanding'] != 0 else 0
    
    return df, enterprise_value, equity_value, implied_share_price, terminal_value, pv_terminal_value

def get_default_implied_price():
    """Calculates the implied price using only the default hardcoded assumptions."""
    _, _, _, implied_share_price, _, _ = perform_dcf_calculation(
        DEFAULT_TERMINAL_ASSUMPTIONS, 
        DEFAULT_FORECAST_ASSUMPTIONS
    )
    return implied_share_price
