import pandas as pd
import numpy as np

# This file centralizes the DCF valuation logic to be shared across pages.

# Hardcoded default assumptions for the static "Implied Price" calculation
DEFAULT_FORECAST_ASSUMPTIONS = {
    'fcff_forecast': [
        1241793558, 1125496234, 2162454601, 4391014761, 5652970707,
        6575053076, 7955001263, 9562063303, 11418747504, 13546453598
    ],
    'net_adjustments':   -822499000,
    'shares_outstanding': 333323673,
}
DEFAULT_TERMINAL_ASSUMPTIONS = {'wacc': 0.10, 'terminal_growth_rate': 0.03}

def perform_dcf_calculation(terminal_assumptions, forecast_assumptions):
    """
    Performs a DCF calculation with a given set of assumptions.
    Returns a tuple of: (df, enterprise_value, equity_value, implied_share_price, terminal_value, pv_terminal_value)
    """
    years = list(range(1, 11))
    fcff_forecast = forecast_assumptions['fcff_forecast']
    
    df = pd.DataFrame({'FCF': fcff_forecast}, index=years)
    
    # --- Terminal Value ---
    if (terminal_assumptions['wacc'] - terminal_assumptions['terminal_growth_rate']) <= 0:
        terminal_value = 0
    else:
        fcf_y10 = df['FCF'].iloc[-1]
        terminal_value = (fcf_y10 * (1 + terminal_assumptions['terminal_growth_rate'])) / (terminal_assumptions['wacc'] - terminal_assumptions['terminal_growth_rate'])

    # --- Present Value of FCF ---
    df['PV Factor'] = [(1 / (1 + terminal_assumptions['wacc'])) ** (year - 0.5) for year in years]
    df['PV of FCF'] = df['FCF'] * df['PV Factor']
    
    pv_terminal_value = terminal_value * df['PV Factor'].iloc[-1]
    enterprise_value = df['PV of FCF'].sum() + pv_terminal_value
    
    # --- Final Share Price ---
    equity_value = enterprise_value - forecast_assumptions['net_adjustments']
    implied_share_price = equity_value / forecast_assumptions['shares_outstanding'] if forecast_assumptions['shares_outstanding'] != 0 else 0
    
    return df, enterprise_value, equity_value, implied_share_price, terminal_value, pv_terminal_value

def get_default_implied_price():
    """Calculates the implied price using only the default hardcoded assumptions."""
    _, _, _, implied_share_price, _, _ = perform_dcf_calculation(
        DEFAULT_TERMINAL_ASSUMPTIONS, 
        DEFAULT_FORECAST_ASSUMPTIONS
    )
    return implied_share_price