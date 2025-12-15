import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="PickMe Investor Assistant",
    page_icon="👋",
    layout="wide"
)

# --- Desktop/Laptop Message ---
st.info("For the best experience, please open this application on a desktop or laptop.")

# --- Header and App Purpose ---
st.title("Welcome to the PickMe Investor Assistant!")
st.subheader("Your AI-Powered Companion for Investment Research and Decision Making")

st.markdown("---")

st.markdown("""
Our mission is to empower investors by providing intelligent tools to navigate investment research reports and make informed decisions. 
Here's how the PickMe Investor Assistant helps you at every step:
""")

st.markdown("---")

# --- Features at a Glance ---
st.header("App Features at a Glance")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🤖 PickMe AI Assistant")
    st.write("Engage in conversational AI to quickly understand research reports and clarify investment theses.")

    st.subheader("📊 Valuation")
    st.write("Adjust valuation assumptions interactively and visualize Enterprise Value components with AI interpretation.")

with col2:
    st.subheader("📈 Stock Analysis")
    st.write("Analyze PickMe's historical price, volume, and moving averages with AI guidance on market entry.")

    st.subheader("⚙️ Portfolio Optimization")
    st.write("Simulate portfolios, optimize for risk-return (Min Variance, Max Sharpe), and visualize allocations.")

st.sidebar.success("Select a feature from the sidebar to begin your analysis.")
