import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv
import google.generativeai as genai
from src.data_utils import load_stock_data

# --- Page Configuration ---
st.set_page_config(
    page_title="Stock Analysis",
    page_icon="📈",
    layout="wide"
)

# --- Main Application ---
st.title("📈 PickMe Stock Analysis")

# Load the data using the shared utility function
stock_df = load_stock_data("PickMe_Stock_Price_History.csv", is_pickme=True)

if stock_df is not None:
    
    # --- Key Metrics ---
    st.subheader("Key Metrics")
    latest_price = stock_df['close'].iloc[-1]
    high_52_week = stock_df['high'][-252:].max()
    low_52_week = stock_df['low'][-252:].min()
    avg_volume = stock_df['share_volume'][-20:].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Latest Close Price", f"LKR {latest_price:,.2f}")
    col2.metric("52-Week High", f"LKR {high_52_week:,.2f}")
    col3.metric("52-Week Low", f"LKR {low_52_week:,.2f}")
    col4.metric("Avg. 20-Day Volume", f"{avg_volume:,.0f}")
    
    st.markdown("---")

    # --- AI Assistant for MA Interpretation ---
    if st.button("💬 Ask PickMe AI Assistant for MA Interpretation"):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("Google API key not found. Please set it in the .env file.")
        else:
            genai.configure(api_key=api_key)
            
            latest_data = stock_df.iloc[-1]
            prompt = f"""
            Act as a technical chartist analyzing a stock's trend for a trading decision.
            Synthesize the following moving average data into a cohesive interpretation.

            **Latest Technical Data:**
            - Closing Price: {latest_data['close']:,.2f} LKR
            - 20-Day Moving Average (Short-term trend): {latest_data['ma_20']:,.2f} LKR
            - 50-Day Moving Average (Mid-term trend): {latest_data['ma_50']:,.2f} LKR

            **Framework for Analysis:**
            1.  **Trend Strength:** Is the price above/below the MAs?
            2.  **Trend Direction:** Is the short-term MA above/below the mid-term MA (Golden/Death Cross context)?

            **Your Task:**
            In 3-4 sentences, provide a summary of the current trend (e.g., bullish, bearish, neutral). State the strength of the signal based on how the indicators align and conclude with a final signal (e.g., "Strong Bullish", "Weak Bearish", "Neutral").
            """
            with st.spinner("PickMe Assistant is analyzing the trend..."):
                try:
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    response = model.generate_content(prompt)
                    with st.chat_message("assistant"):
                        st.markdown(response.text)
                except Exception as e:
                    st.error(f"An error occurred with the AI Assistant: {e}")
    st.markdown("---")
    
    # --- Charting Section ---
    tab1, tab2 = st.tabs(["Price Action", "Returns Analysis"])

    with tab1:
        st.subheader("Price and Volume History")
        
        with st.expander("Chart Options"):
            show_ma_20 = st.checkbox("Show 20-Day Moving Average", value=True)
            show_ma_50 = st.checkbox("Show 50-Day Moving Average", value=True)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                              vertical_spacing=0.03, subplot_titles=('Price', 'Volume'), 
                              row_heights=[0.7, 0.3]) # Adjusted row heights

        fig.add_trace(go.Candlestick(x=stock_df.index,
                        open=stock_df['open'], high=stock_df['high'],
                        low=stock_df['low'], close=stock_df['close'], name="Price"), 
                      row=1, col=1)

        if show_ma_20:
            fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['ma_20'], mode='lines', name='20-Day MA'), row=1, col=1)
        if show_ma_50:
            fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['ma_50'], mode='lines', name='50-Day MA'), row=1, col=1)

        fig.add_trace(go.Bar(x=stock_df.index, y=stock_df['share_volume'], name='Volume'), row=2, col=1)

        fig.update_layout(xaxis_rangeslider_visible=False, height=600,
                          title="Candlestick Chart with Volume", yaxis1_title="Price (LKR)", yaxis2_title="Volume")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Daily Returns Analysis")
        returns_fig = go.Figure()
        returns_fig.add_trace(go.Histogram(x=stock_df['returns'], nbinsx=50, name='returns'))
        mean_return = stock_df['returns'].mean()
        std_return = stock_df['returns'].std()
        returns_fig.add_vline(x=mean_return, line_width=2, line_dash="dash", line_color="red")
        returns_fig.update_layout(title_text='Distribution of Daily Returns',
                                  xaxis_title_text='Daily Return', yaxis_title_text='Frequency',
                                  annotations=[dict(x=0.05, y=0.95, showarrow=False,
                                                    text=f"Mean: {mean_return:.4%}<br>Std Dev: {std_return:.4%}",
                                                    xref="paper", yref="paper", align="left")])
        st.plotly_chart(returns_fig, use_container_width=True)
