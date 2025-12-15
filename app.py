import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="PickMe Investor Assistant",
    page_icon="👋",
    layout="wide"
)

# --- Custom CSS for Modern Cards ---
st.markdown("""
<style>
.feature-card {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 10px;
    padding: 25px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
    height: 100%;
}
.feature-card:hover {
    box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
    transform: translateY(-5px);
}
body.dark .feature-card {
    background-color: #262730;
    border: 1px solid #444;
}
.feature-card h3 {
    font-size: 1.5em;
    margin-bottom: 15px;
    color: var(--text-color);
}
.feature-card .icon {
    font-size: 3em;
    margin-bottom: 20px;
}
.feature-card .description {
    font-size: 1em;
    opacity: 0.7;
    color: var(--text-color);
}
</style>
""", unsafe_allow_html=True)


# --- Header and App Purpose ---
st.info("For the best experience, please open this application on a desktop or laptop.")
st.title("Welcome to the PickMe Investor Assistant!")
st.subheader("Your AI-Powered Companion for Investment Research and Decision Making")
st.markdown("---")
st.markdown("""
Our mission is to empower investors by providing intelligent tools to navigate investment research reports and make informed decisions. 
Here's how the PickMe Investor Assistant helps you at every step:
""")

# --- Investor Workflow ---
st.markdown("### Investor Workflow:")
st.markdown("""
1.  **Insight Generation:** Start by engaging with the **PickMe AI Assistant**. Ask questions about research reports or investment theses to extract key insights and clarify complex information.
2.  **In-depth Valuation:** Transition to the **Valuation** page. Based on the insights gained, adjust critical assumptions in a dynamic DCF model to derive a fundamental valuation.
3.  **Market Behavior Analysis:** Utilize the **Stock Analysis** page to understand PickMe's current market behavior, analyzing price action and moving averages to gauge market sentiment.
4.  **Strategic Portfolio Management:** Finally, move to **Portfolio Optimization**. Simulate investment scenarios and construct diversified portfolios to see how PickMe fits into a broader strategy.
""")

st.markdown("---")

# --- Features at a Glance (Modern Cards) ---
st.header("App Features at a Glance")
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="icon">🤖</div>
        <h3>PickMe AI Assistant</h3>
        <div class="description">Engage in conversational AI to quickly understand research reports and clarify investment theses.</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True) # Spacer

    st.markdown("""
    <div class="feature-card">
        <div class="icon">📈</div>
        <h3>Stock Analysis</h3>
        <div class="description">Analyze PickMe's historical price, volume, and moving averages with AI guidance on market entry.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="icon">📊</div>
        <h3>Valuation</h3>
        <div class="description">Adjust valuation assumptions interactively and visualize Enterprise Value components with AI interpretation.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True) # Spacer

    st.markdown("""
    <div class="feature-card">
        <div class="icon">⚙️</div>
        <h3>Portfolio Optimization</h3>
        <div class="description">Simulate portfolios, optimize for risk-return, and visualize asset allocations with the Efficient Frontier.</div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.success("Select a feature from the sidebar to begin your analysis.")


