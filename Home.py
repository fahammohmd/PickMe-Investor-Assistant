import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="PKME Investor Assistant",
    page_icon="👋",
    layout="wide"
)

# --- Desktop/Laptop Message ---
st.info("For the best experience, please open this application on a desktop or laptop.")

# --- Header and App Purpose ---
st.title("Welcome to the PKME Investor Assistant!")
st.subheader("Your AI-Powered Companion for Investment Research and Decision Making")

st.markdown("---")

st.markdown("""
Our mission is to empower investors by providing intelligent tools to navigate investment research reports and make informed decisions. 
Here's how the PKME Investor Assistant helps you at every step: 

1. **Understand Research Reports**: Use our AI assistant to break down complex research into digestible insights.
2. **Customize Valuation**: Translate your insights into numbers. Adjust key valuation assumptions based on your own judgment.
3. **Analyze Stock Performance**: Dive into PKME's historical stock data with AI-driven analysis to identify trends and opportunities.
4. **Optimize Your Portfolio**: Simulate your portfolio with PKME stock, optimize for risk-return profiles, and visualize allocations effectively.

""")

st.markdown("---")

# --- Features at a Glance ---
st.header("App Features at a Glance")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🤖 PKME AI Assistant")
    st.write("Engage in conversational AI to quickly understand research reports and clarify investment theses.")

    st.subheader("📊 Valuation")
    st.write("Adjust valuation assumptions interactively and visualize Enterprise Value components with AI interpretation.")

with col2:
    st.subheader("📈 Stock Analysis")
    st.write("Analyze PKME's historical price, volume, and moving averages with AI guidance on market entry.")

    st.subheader("⚙️ Portfolio Optimization")
    st.write("Simulate portfolios, optimize for risk-return (Min Variance, Max Sharpe), and visualize allocations.")

st.sidebar.success("Select a feature from the sidebar to begin your analysis.")

st.markdown("---")
st.header("Navigate to a Page")
st.page_link("pages/1_PickMe_AI_Assistant.py", label="PickMe AI Assistant", icon="🤖")
st.page_link("pages/2_Valuation.py", label="Valuation", icon="📊")
st.page_link("pages/3_Stock_Analysis.py", label="Stock Analysis", icon="📈")
st.page_link("pages/4_Portfolio_Optimization.py", label="Portfolio Optimization", icon="⚙️")
