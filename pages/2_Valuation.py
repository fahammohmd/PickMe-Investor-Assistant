import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib
import os
from dotenv import load_dotenv
import google.generativeai as genai
from src.valuation_logic import perform_dcf_calculation, DEFAULT_FORECAST_ASSUMPTIONS
from src.data_utils import load_stock_data

# --- Page Configuration ---
st.set_page_config(
    page_title="Valuation",
    page_icon="📊",
    layout="wide"
)

# --- Helper Functions (Visualization and Monte Carlo) ---
def create_waterfall_chart(enterprise_value, net_debt, equity_value):
    """Creates a waterfall chart for the Enterprise to Equity Value bridge."""
    fig = go.Figure(go.Waterfall(
        name="bridge", orientation="v",
        measure=["relative", "relative", "total"],
        x=["Enterprise Value", "Net Debt", "Equity Value"],
        textposition="outside",
        text=[f"LKR {enterprise_value:,.0f}", f"LKR {-net_debt:,.0f}", f"LKR {equity_value:,.0f}"],
        y=[enterprise_value, -net_debt, equity_value],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    fig.update_layout(title="Enterprise to Equity Value Bridge", showlegend=False)
    return fig

def run_monte_carlo(terminal_assumptions, n_simulations=1000):
    """Runs a Monte Carlo simulation on the valuation."""
    share_prices = []
    for _ in range(n_simulations):
        sim_assumptions = terminal_assumptions.copy()
        sim_assumptions['wacc'] = np.random.normal(terminal_assumptions['wacc'], 0.01)
        sim_assumptions['terminal_growth_rate'] = np.random.normal(terminal_assumptions['terminal_growth_rate'], 0.005)
        
        if sim_assumptions['wacc'] <= sim_assumptions['terminal_growth_rate']: continue
            
        _, _, _, implied_share_price, _, _ = perform_dcf_calculation(sim_assumptions, DEFAULT_FORECAST_ASSUMPTIONS)
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
            if wacc <= terminal_growth:
                row.append(np.nan)
                continue
            temp_assumptions = terminal_assumptions.copy()
            temp_assumptions['wacc'] = wacc
            temp_assumptions['terminal_growth_rate'] = terminal_growth
            _, _, _, implied_share_price, _, _ = perform_dcf_calculation(temp_assumptions, DEFAULT_FORECAST_ASSUMPTIONS)
            row.append(implied_share_price)
        sensitivity_data.append(row)
        
    df_sensitivity = pd.DataFrame(
        sensitivity_data,
        index=[f"{w:.2%}" for w in wacc_range],
        columns=[f"{g:.2%}" for g in terminal_growth_range]
    )
    return df_sensitivity

# --- Load Data for Default Price ---
pickme_data = load_stock_data("PickMe_Stock_Price_History.csv", is_pickme=True)
if pickme_data is not None and not pickme_data.empty:
    latest_actual_price = pickme_data['close'].iloc[-1]
else:
    latest_actual_price = 150.0 # Fallback

# --- Sidebar Inputs ---
st.sidebar.header("Terminal Value Assumptions")
terminal_assumptions = {
    'wacc': st.sidebar.slider("WACC (%)", 10.0, 30.0, 15.0, 0.1) / 100.0,
    'terminal_growth_rate': st.sidebar.slider("Terminal Growth Rate (%)", 1.0, 10.0, 5.0, 0.1) / 100.0,
    'current_share_price': st.sidebar.number_input("Current Share Price", value=float(latest_actual_price)),
}

# --- Main Page ---
st.title("Interactive DCF Valuation")
st.info("Use the sidebar to adjust the terminal valuation assumptions and see the results below.")

# --- Perform Calculations ---
df_dcf, enterprise_value, equity_value, implied_share_price, terminal_value, pv_terminal_value = perform_dcf_calculation(terminal_assumptions, DEFAULT_FORECAST_ASSUMPTIONS)

# --- Display Results ---
upside_downside = (implied_share_price / terminal_assumptions['current_share_price']) - 1 if terminal_assumptions['current_share_price'] != 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Implied Share Price", f"LKR {implied_share_price:,.2f}" if not np.isnan(implied_share_price) else "N/A")
col2.metric("Upside/Downside", f"{upside_downside:.2%}" if not np.isnan(upside_downside) else "N/A")
col3.metric("Enterprise Value", f"LKR {enterprise_value:,.0f}" if not np.isnan(enterprise_value) else "N/A")
col4.metric("Equity Value", f"LKR {equity_value:,.0f}" if not np.isnan(equity_value) else "N/A")

st.markdown("---")

# --- AI Assistant Interpretation ---
if st.button("💬 Ask PickMe AI Assistant for Valuation Interpretation"):
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Google API key not found. Please set it in the .env file.")
    else:
        genai.configure(api_key=api_key)
        prompt = f"""
        Act as a seasoned investment analyst providing a summary for a client.
        Based on the DCF valuation results below, give a short, intelligent interpretation.

        **Valuation Data:**
        - Implied Share Price (Our DCF Result): {implied_share_price:,.2f} LKR
        - Current Market Price: {terminal_assumptions['current_share_price']:,.2f} LKR
        - Potential Upside/Downside: {upside_downside:.2%}

        **Key Assumptions:**
        - WACC: {terminal_assumptions['wacc']:.2%}
        - Terminal Growth Rate: {terminal_assumptions['terminal_growth_rate']:.2%}

        **Your Task:**
        In 3-4 sentences, state whether the stock appears undervalued or overvalued based on this model. Briefly explain what the 'Potential Upside/Downside' signifies and conclude with a crucial caveat about the valuation's sensitivity to the key assumptions.
        """
        with st.spinner("PickMe Assistant is thinking..."):
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')
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
        st.plotly_chart(create_waterfall_chart(enterprise_value, DEFAULT_FORECAST_ASSUMPTIONS['net_debt'], equity_value), use_container_width=True)
        st.subheader("Enterprise Value Components")
        ev_components = pd.DataFrame({
            'Component': ['PV of Explicit FCFs', 'PV of Terminal Value'],
            'Value': [df_dcf['PV of FCF'].sum(), pv_terminal_value]
        })
        fig = px.pie(ev_components, values='Value', names='Component', title='Enterprise Value Breakdown')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Cannot display chart due to invalid valuation inputs (e.g., WACC is less than or equal to Terminal Growth Rate).")

with tab2:
    st.header("Monte Carlo Simulation (1,000 runs)")
    st.write("This simulation shows the distribution of possible implied share prices by varying WACC and Terminal Growth Rate.")
    if st.button("Run Monte Carlo Simulation"):
        with st.spinner("Running simulation..."):
            share_prices_sim = run_monte_carlo(terminal_assumptions)
            if share_prices_sim:
                fig = px.histogram(share_prices_sim, nbins=100, title="Distribution of Implied Share Prices")
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
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

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 10px;">
        <p>developed by CFARC UOK Team A</p>
    </div>
    """,
    unsafe_allow_html=True
)