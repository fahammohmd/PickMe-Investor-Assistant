import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib
import os
from dotenv import load_dotenv
import google.generativeai as genai

# --- Page Configuration ---
st.set_page_config(
    page_title="Valuation",
    page_icon="📊",
    layout="wide"
)

# --- Hardcoded Assumptions ---
FORECAST_ASSUMPTIONS = {
    'revenue_y0': 1000,
    'revenue_growth': [0.25, 0.22, 0.20, 0.18, 0.15, 0.12, 0.10, 0.08, 0.06, 0.05],
    'ebitda_margin': [0.30] * 10,
    'tax_rate': [0.25] * 10,
    'da_percent_revenue': [0.05] * 10,
    'capex_percent_revenue': [0.08] * 10,
    'nwc_percent_revenue': [0.03] * 10,
    'net_debt': 500,
    'shares_outstanding': 100,
}

# --- Helper Functions ---
def calculate_dcf(terminal_assumptions):
    """Calculates the DCF valuation based on the given assumptions."""
    
    # Create a DataFrame for the 10-year forecast
    years = list(range(1, 11))
    df = pd.DataFrame(index=years)
    
    # --- Revenue ---
    revenue = [FORECAST_ASSUMPTIONS['revenue_y0'] * (1 + FORECAST_ASSUMPTIONS['revenue_growth'][0])]
    for i in range(1, 10):
        revenue.append(revenue[i-1] * (1 + FORECAST_ASSUMPTIONS['revenue_growth'][i]))
    df['Revenue'] = revenue
    
    # --- EBITDA ---
    df['EBITDA'] = df['Revenue'] * np.array(FORECAST_ASSUMPTIONS['ebitda_margin'])
    
    # --- EBIT ---
    df['D&A'] = df['Revenue'] * np.array(FORECAST_ASSUMPTIONS['da_percent_revenue'])
    df['EBIT'] = df['EBITDA'] - df['D&A']
    
    # --- NOPAT ---
    df['NOPAT'] = df['EBIT'] * (1 - np.array(FORECAST_ASSUMPTIONS['tax_rate']))
    
    # --- Free Cash Flow ---
    df['CapEx'] = df['Revenue'] * np.array(FORECAST_ASSUMPTIONS['capex_percent_revenue'])
    df['Change in NWC'] = df['Revenue'] * np.array(FORECAST_ASSUMPTIONS['nwc_percent_revenue'])
    df['FCF'] = df['NOPAT'] + df['D&A'] - df['CapEx'] - df['Change in NWC']
    
    # --- Terminal Value ---
    if (terminal_assumptions['wacc'] - terminal_assumptions['terminal_growth_rate']) == 0:
        # Avoid division by zero
        terminal_value = 0
    else:
        fcf_y10 = df['FCF'].iloc[-1]
        terminal_value = (fcf_y10 * (1 + terminal_assumptions['terminal_growth_rate'])) / (terminal_assumptions['wacc'] - terminal_assumptions['terminal_growth_rate'])

    
    # --- Present Value of FCF ---
    df['PV Factor'] = [(1 / (1 + terminal_assumptions['wacc'])) ** year for year in years]
    df['PV of FCF'] = df['FCF'] * df['PV Factor']
    
    # --- Enterprise Value ---
    pv_terminal_value = terminal_value * df['PV Factor'].iloc[-1]
    enterprise_value = df['PV of FCF'].sum() + pv_terminal_value
    
    # --- Equity Value & Implied Share Price ---
    equity_value = enterprise_value - FORECAST_ASSUMPTIONS['net_debt']
    implied_share_price = equity_value / FORECAST_ASSUMPTIONS['shares_outstanding'] if FORECAST_ASSUMPTIONS['shares_outstanding'] != 0 else 0
    
    return df, enterprise_value, equity_value, implied_share_price, terminal_value, pv_terminal_value

def create_waterfall_chart(enterprise_value, net_debt, equity_value):
    """Creates a waterfall chart for the Enterprise to Equity Value bridge."""
    fig = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        measure = ["relative", "relative", "total"],
        x = ["Enterprise Value", "Net Debt", "Equity Value"],
        textposition = "outside",
        text = [f"LKR {enterprise_value:,.0f}", f"LKR {-net_debt:,.0f}", f"LKR {equity_value:,.0f}"],
        y = [enterprise_value, -net_debt, equity_value],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
    ))

    fig.update_layout(
            title = "Enterprise to Equity Value Bridge",
            showlegend = False
    )
    return fig

def run_monte_carlo(terminal_assumptions, n_simulations=1000):
    """Runs a Monte Carlo simulation on the valuation."""
    share_prices = []
    
    for _ in range(n_simulations):
        sim_assumptions = terminal_assumptions.copy()
        sim_assumptions['wacc'] = np.random.normal(terminal_assumptions['wacc'], 0.01)
        sim_assumptions['terminal_growth_rate'] = np.random.normal(terminal_assumptions['terminal_growth_rate'], 0.005)
        
        # Avoid wacc = terminal_growth_rate
        if sim_assumptions['wacc'] == sim_assumptions['terminal_growth_rate']:
            continue
            
        _, _, _, implied_share_price, _, _ = calculate_dcf(sim_assumptions)
        if not np.isnan(implied_share_price) and not np.isinf(implied_share_price):
            share_prices.append(implied_share_price)
        
    return share_prices

def create_sensitivity_table(terminal_assumptions):
    """Creates a sensitivity table for the implied share price."""
    wacc_range = np.linspace(terminal_assumptions['wacc'] - 0.02, terminal_assumptions['wacc'] + 0.02, 5)
    terminal_growth_range = np.linspace(terminal_assumptions['terminal_growth_rate'] - 0.01, terminal_assumptions['terminal_growth_rate'] + 0.01, 5)
    
    sensitivity_data = []
    for wacc in wacc_range:
        row = []
        for terminal_growth in terminal_growth_range:
            if wacc == terminal_growth:
                row.append(np.nan) # Or some other indicator for this case
                continue

            temp_assumptions = terminal_assumptions.copy()
            temp_assumptions['wacc'] = wacc
            temp_assumptions['terminal_growth_rate'] = terminal_growth
            _, _, _, implied_share_price, _, _ = calculate_dcf(temp_assumptions)
            row.append(implied_share_price)
        sensitivity_data.append(row)
        
    df_sensitivity = pd.DataFrame(
        sensitivity_data,
        index=[f"{w:.2%}" for w in wacc_range],
        columns=[f"{g:.2%}" for g in terminal_growth_range]
    )
    return df_sensitivity

# --- Sidebar Inputs ---
st.sidebar.header("Terminal Value Assumptions")

terminal_assumptions = {
    'wacc': st.sidebar.slider("WACC (%)", 10.0, 30.0, 9.0, 0.1) / 100.0,
    'terminal_growth_rate': st.sidebar.slider("Terminal Growth Rate (%)", 1.0, 10.0, 2.5, 0.1) / 100.0,
    'current_share_price': st.sidebar.number_input("Current Share Price", value=150.0),
}

# --- Main Page ---
st.title("PickMe DCF Valuation")
st.info("Use the sidebar to adjust the terminal valuation assumptions and see the results below.")

# --- Perform Calculations ---
df_dcf, enterprise_value, equity_value, implied_share_price, terminal_value, pv_terminal_value = calculate_dcf(terminal_assumptions)

# --- Display Results ---
upside_downside = (implied_share_price / terminal_assumptions['current_share_price']) - 1 if terminal_assumptions['current_share_price'] != 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Implied Share Price", f"LKR {implied_share_price:,.2f}" if not np.isnan(implied_share_price) else "N/A")
col2.metric("Upside/Downside", f"{upside_downside:.2%}" if not np.isnan(upside_downside) else "N/A")
col3.metric("Enterprise Value", f"LKR {enterprise_value:,.0f}" if not np.isnan(enterprise_value) else "N/A")
col4.metric("Equity Value", f"LKR {equity_value:,.0f}" if not np.isnan(equity_value) else "N/A")

st.markdown("---")

# --- AI Assistant Interpretation ---
if st.button("💬 Ask PickMe AI Assistant for Interpretation"):
    
    # Load API Key
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Google API key not found. Please set it in the .env file.")
    else:
        genai.configure(api_key=api_key)
        
        # Construct the prompt
        prompt = f"""
        As a financial analyst, provide a brief interpretation of the following DCF valuation results for a company. 
        The target audience is an investor who may not be a financial expert. Explain what the numbers mean in simple terms.

        **Valuation Metrics:**
        - **Implied Share Price:** {implied_share_price:,.2f} LKR
        - **Current Share Price:** {terminal_assumptions['current_share_price']:,.2f} LKR
        - **Upside/Downside:** {upside_downside:.2%}
        - **Enterprise Value:** {enterprise_value:,.0f} LKR

        **Key Assumptions Used:**
        - **WACC (Discount Rate):** {terminal_assumptions['wacc']:.2%}
        - **Terminal Growth Rate:** {terminal_assumptions['terminal_growth_rate']:.2%}

        Structure your interpretation as follows:
        1.  **Summary:** Start with a one-sentence summary of the valuation outcome.
        2.  **Explanation:** Briefly explain what the implied price vs. current price suggests.
        3.  **Assumptions:** Mention that the valuation is sensitive to the key assumptions (WACC and Terminal Growth).

        Keep the entire response to about 3-4 sentences.
        """
        with st.spinner("PickMe Assistant is thinking..."):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                
                with st.chat_message("assistant"):
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred with the AI Assistant: {e}")


st.markdown("---")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["Enterprise Value Bridge", "Monte Carlo Simulation", "Sensitivity Analysis"])

with tab1:
    st.header("Enterprise to Equity Value Bridge")
    if not np.isnan(enterprise_value):
        
        st.plotly_chart(create_waterfall_chart(enterprise_value, FORECAST_ASSUMPTIONS['net_debt'], equity_value), use_container_width=True)

        st.subheader("Enterprise Value Components")
        ev_components = pd.DataFrame({
            'Component': ['PV of Explicit FCFs', 'PV of Terminal Value'],
            'Value': [df_dcf['PV of FCF'].sum(), pv_terminal_value]
        })
        fig = px.pie(ev_components, values='Value', names='Component', title='Enterprise Value Breakdown')
        st.plotly_chart(fig, use_container_width=True)
            
    else:
        st.warning("Cannot display chart due to invalid valuation inputs (e.g., WACC equals Terminal Growth Rate).")


with tab2:
    st.header("Monte Carlo Simulation (1,000 runs)")
    st.write("This simulation shows the distribution of possible implied share prices by varying WACC and Terminal Growth Rate.")
    
    if st.button("Run Monte Carlo Simulation"):
        with st.spinner("Running simulation..."):
            share_prices_sim = run_monte_carlo(terminal_assumptions)
            
            if share_prices_sim:
                # --- Display Histogram ---
                fig = px.histogram(share_prices_sim, nbins=100, title="Distribution of Implied Share Prices")
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # --- Display Descriptive Stats ---
                stats_df = pd.Series(share_prices_sim).describe().to_frame().T
                st.subheader("Descriptive Statistics")
                st.dataframe(stats_df.style.format("LKR {:,.2f}"))
            else:
                st.warning("Simulation resulted in no valid data points. Try adjusting the terminal assumptions.")


with tab3:
    st.header("Sensitivity Analysis")
    st.write("This table shows how the implied share price changes with WACC and the Terminal Growth Rate.")
    
    sensitivity_df = create_sensitivity_table(terminal_assumptions)
    st.dataframe(sensitivity_df.style.format("LKR {:,.2f}", na_rep="N/A").background_gradient(cmap='viridis'))


st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 10px;">
        <p>developed by CFARC UOK Team A</p>
    </div>
    """,
    unsafe_allow_html=True
)