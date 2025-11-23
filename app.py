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

st.markdown("### Investor Workflow:")
st.markdown("""
1.  **Insight Generation:** Start by engaging with the **PickMe AI Assistant**. Upload research reports or investment theses, and ask questions to extract key insights and clarify complex information.
2.  **In-depth Valuation:** Transition to the **Valuation** page. Based on the insights gained, adjust critical assumptions in a dynamic Discounted Cash Flow (DCF) model to derive a fundamental valuation. The AI Assistant is available here to interpret your results.
3.  **Market Behavior Analysis:** Utilize the **Stock Analysis** page to understand PickMe's current market behavior. Analyze historical price action, moving averages, and other technical indicators to gauge market sentiment and trends. The AI Assistant can help interpret these signals.
4.  **Strategic Portfolio Management:** Finally, move to **Portfolio Optimization**. Simulate various investment scenarios, construct diversified portfolios using Markowitz optimization (Minimum Variance and Maximum Sharpe Ratio strategies), and see how your PickMe investment fits into a broader portfolio context. The AI can even guide your market entry.
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

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 10px;">
        <p>developed by CFARC UOK Team A</p>
    </div>
    """,
    unsafe_allow_html=True
)