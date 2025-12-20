import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy.optimize import minimize
import os
from dotenv import load_dotenv
import google.generativeai as genai
from src.valuation_logic import get_default_implied_price
from src.data_utils import load_all_stock_data, load_stock_data

# --- Page Configuration ---
st.set_page_config(
    page_title="Portfolio Optimization",
    page_icon="⚙️",
    layout="wide"
)

# --- PORTFOLIO OPTIMIZATION LOGIC ---
def portfolio_performance(weights, mean_returns, cov_matrix):
    """Calculates portfolio performance stats."""
    returns = np.sum(mean_returns * weights) * 252
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return returns, std

def neg_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate):
    """Calculates the negative Sharpe ratio for optimization."""
    p_returns, p_std = portfolio_performance(weights, mean_returns, cov_matrix)
    if p_std == 0: return 0
    return -(p_returns - risk_free_rate) / p_std

def portfolio_variance(weights, mean_returns, cov_matrix):
    """Calculates portfolio variance."""
    return portfolio_performance(weights, mean_returns, cov_matrix)[1]

def optimize_portfolio(mean_returns, cov_matrix, risk_free_rate, num_assets):
    """Finds the min variance and max sharpe ratio portfolios."""
    args = (mean_returns, cov_matrix)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    initial_weights = num_assets * [1. / num_assets]

    min_var_result = minimize(portfolio_variance, initial_weights, args=args,
                              method='SLSQP', bounds=bounds, constraints=constraints)
    min_var_weights = min_var_result.x

    max_sharpe_args = (mean_returns, cov_matrix, risk_free_rate)
    max_sharpe_result = minimize(neg_sharpe_ratio, initial_weights, args=max_sharpe_args,
                                 method='SLSQP', bounds=bounds, constraints=constraints)
    max_sharpe_weights = max_sharpe_result.x
    
    return min_var_weights, max_sharpe_weights

@st.cache_data
def calculate_efficient_frontier(num_assets, mean_returns, cov_matrix, risk_free_rate):
    """Calculates points for the efficient frontier scatter plot."""
    results = np.zeros((3, 10000))
    for i in range(10000):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        portfolio_return, portfolio_std = portfolio_performance(weights, mean_returns, cov_matrix)
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std
        if portfolio_std != 0:
            results[2,i] = (portfolio_return - risk_free_rate) / portfolio_std
        else:
            results[2,i] = 0
    return pd.DataFrame(results.T, columns=['Return', 'Volatility', 'Sharpe Ratio'])

# --- UI & VISUALIZATION ---
st.title("⚙️ Portfolio Optimization")

all_prices = load_all_stock_data()

main_tab1, main_tab2 = st.tabs(["PKME Investment Scenario", "Markowitz Portfolio Optimization"])

# --- TAB 1: PKME Investment Scenario ---
with main_tab1:
    st.subheader("Calculate Potential Return for PKME")
    
    # Check session state for the dynamic price from the Valuation page
    if 'dynamic_implied_price' in st.session_state and st.session_state.dynamic_implied_price is not None and not np.isnan(st.session_state.dynamic_implied_price):
        implied_price = st.session_state.dynamic_implied_price
        price_source_label = ""
    else:
        implied_price = np.nan # Set to NaN if not calculated yet
        price_source_label = "(N/A - Please visit Valuation page to calculate)"

    # Load ONLY PKME data to get its true latest price
    pickme_df = load_stock_data("PKME_Stock_Price_History.csv", is_pickme=True)
    if pickme_df is not None and not pickme_df.empty:
        latest_actual_price = pickme_df['close'].iloc[-1]
    else:
        latest_actual_price = 150.0 # Fallback

    col1, col2 = st.columns(2)
    with col1:
        investment_amount = st.number_input("Amount to Invest in PKME (LKR)", min_value=1000, value=100000, step=1000)
        current_price = st.number_input("Current Share Price (LKR)", value=float(latest_actual_price))
    with col2:
        st.markdown(
            f"""
            <div style="border: 1px solid #E0E0E0; padding: 10px; text-align: center;">
                <p style="font-size: 0.9em; color: grey; margin-bottom: 0;">Implied Share Price {price_source_label}</p>
                <p style="font-size: 2em; font-weight: bold; margin-top: 0;">{f"LKR {implied_price:,.2f}" if not np.isnan(implied_price) else "N/A"}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    if current_price > 0:
        num_shares = investment_amount / current_price
        future_value = num_shares * implied_price
        potential_return = (future_value / investment_amount) - 1
        st.markdown("---")
        st.subheader("Potential Outcome")
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.metric("Shares You Can Buy", f"{num_shares:,.2f}")
        col_res2.metric("Estimated Future Value", f"LKR {future_value:,.0f}")
        col_res3.metric("Potential Return", f"{potential_return:.1%}")

        st.markdown("---")
        if st.button("💬 Ask PKME AI Assistant for Interpretation on Market Entry"):
            load_dotenv()
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                st.error("Google API key not found. Please set it in the .env file.")
            else:
                genai.configure(api_key=api_key)
                
                prompt = f"""
                Act as a market strategist providing advice on market entry for PKME stock.
                Based on the following moving average data, provide an intelligent and comprehensive interpretation of the current market timing.

                **Current Market Data:**
                - Latest Closing Price: {latest_actual_price:,.2f} LKR
                - 20-Day Moving Average (Short-term Trend): {pickme_df['ma_20'].iloc[-1]:,.2f} LKR
                - 50-Day Moving Average (Mid-term Trend): {pickme_df['ma_50'].iloc[-1]:,.2f} LKR

                **Framework for Analysis:**
                - A price above both MAs can indicate bullish momentum (potential strength).
                - A price below both MAs can indicate bearish momentum (potential weakness).
                - A "Golden Cross" (short-term MA crossing above mid-term MA) is a classic bullish signal.
                - A "Death Cross" (short-term MA crossing below mid-term MA) is a classic bearish signal.
                - Consider the distance between the price and the MAs as an indicator of how extended a move might be.

                **Your Task:**
                1.  Provide a short analysis (2-3 sentences) of the current trend based on the data.
                2.  Based on your analysis, suggest a potential strategy for an investor considering entering the market (e.g., "This could be a favorable entry point for trend-following investors," or "Investors might wait for signs of a reversal," or "The current setup suggests caution").
                3.  Conclude with a brief note on how an investor might navigate this situation (e.g., "One might consider a partial entry and watch for a price pullback to the 20-day MA").

                Keep the entire response concise and actionable.
                """
                with st.spinner("PKME Assistant is analyzing the market entry..."):
                    try:
                        model = genai.GenerativeModel('gemini-2.0-flash')
                        response = model.generate_content(prompt)
                        with st.chat_message("assistant"):
                            st.markdown(response.text)
                    except Exception as e:
                        st.error(f"An error occurred with the AI Assistant: {e}")

# --- TAB 2: Portfolio Strategies ---
with main_tab2:
    if all_prices is None:
        st.error("Could not load stock price data. Please check the CSV files.")
    else:
        all_tickers = all_prices.columns.tolist()
        default_selection = [ticker for ticker in ['PKME', 'HHL', 'TJL'] if ticker in all_tickers]
        
        selected_stocks = st.multiselect("Select stocks for the portfolio:", options=all_tickers, default=default_selection)
        risk_free_rate = st.slider("Risk-Free Rate (%)", 0.0, 20.0, 10.8, 0.1) / 100.0
        
        if len(selected_stocks) < 2:
            st.warning("Please select at least two stocks for optimization.")
        else:
            # --- Perform Calculations ---
            portfolio_data = all_prices[selected_stocks].dropna() # Dropna here on the filtered data
            returns = portfolio_data.pct_change().dropna()
            mean_returns = returns.mean()
            cov_matrix = returns.cov()
            num_assets = len(selected_stocks)

            min_var_weights, max_sharpe_weights = optimize_portfolio(mean_returns, cov_matrix, risk_free_rate, num_assets)
            min_var_perf = portfolio_performance(min_var_weights, mean_returns, cov_matrix)
            max_sharpe_perf = portfolio_performance(max_sharpe_weights, mean_returns, cov_matrix)
            results_df = calculate_efficient_frontier(num_assets, mean_returns, cov_matrix, risk_free_rate)

            # --- Create Tabs for Each Strategy ---
            sub_tab1, sub_tab2 = st.tabs(["Minimum Variance Portfolio", "Maximum Sharpe Ratio Portfolio"])

            with sub_tab1:
                st.subheader("Portfolio with Minimum Risk")
                st.metric("Expected Annual Return", f"{min_var_perf[0]:.1%}")
                st.metric("Expected Annual Volatility", f"{min_var_perf[1]:.1%}")
                
                st.markdown("##### Asset Allocation")
                res_col_mv1, res_col_mv2 = st.columns([0.6, 0.4])
                with res_col_mv1:
                    min_var_df = pd.DataFrame({'Asset': selected_stocks, 'Weight': min_var_weights})
                    fig_mv = px.pie(min_var_df, values='Weight', names='Asset', title='Minimum Variance Asset Allocation')
                    st.plotly_chart(fig_mv, use_container_width=True)
                with res_col_mv2:
                    st.dataframe(min_var_df.style.format({'Weight': '{:.1%}'}))
                
                st.markdown("##### Efficient Frontier")
                fig_ef_mv = go.Figure()
                fig_ef_mv.add_trace(go.Scatter(x=results_df['Volatility'], y=results_df['Return'], mode='markers', marker=dict(color=results_df['Sharpe Ratio'], showscale=True, size=7, colorbar=dict(title="Sharpe Ratio"), colorscale="Viridis")))
                fig_ef_mv.add_trace(go.Scatter(x=[min_var_perf[1]], y=[min_var_perf[0]], mode='markers', marker=dict(size=15, color='red', symbol='star'), name='This Portfolio'))
                fig_ef_mv.update_layout(title='Efficient Frontier', xaxis_title='Annual Volatility (Risk)', yaxis_title='Annual Return', height=500)
                st.plotly_chart(fig_ef_mv, use_container_width=True)

            with sub_tab2:
                st.subheader("Portfolio with Maximum Risk-Adjusted Return")
                st.metric("Expected Annual Return", f"{max_sharpe_perf[0]:.1%}")
                st.metric("Expected Annual Volatility", f"{max_sharpe_perf[1]:.1%}")
                
                st.markdown("##### Asset Allocation")
                res_col_ms1, res_col_ms2 = st.columns([0.6, 0.4])
                with res_col_ms1:
                    max_sharpe_df = pd.DataFrame({'Asset': selected_stocks, 'Weight': max_sharpe_weights})
                    fig_ms = px.pie(max_sharpe_df, values='Weight', names='Asset', title='Max Sharpe Ratio Asset Allocation')
                    st.plotly_chart(fig_ms, use_container_width=True)
                with res_col_ms2:
                    st.dataframe(max_sharpe_df.style.format({'Weight': '{:.1%}'}))
                
                st.markdown("##### Efficient Frontier")
                fig_ef_ms = go.Figure()
                fig_ef_ms.add_trace(go.Scatter(x=results_df['Volatility'], y=results_df['Return'], mode='markers', marker=dict(color=results_df['Sharpe Ratio'], showscale=True, size=7, colorbar=dict(title="Sharpe Ratio"), colorscale="Viridis")))
                fig_ef_ms.add_trace(go.Scatter(x=[max_sharpe_perf[1]], y=[max_sharpe_perf[0]], mode='markers', marker=dict(size=15, color='red', symbol='star'), name='This Portfolio'))
                fig_ef_ms.update_layout(title='Efficient Frontier', xaxis_title='Annual Volatility (Risk)', yaxis_title='Annual Return', height=500)
                st.plotly_chart(fig_ef_ms, use_container_width=True)
