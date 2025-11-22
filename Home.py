import streamlit as st

# Page configuration
st.set_page_config(
    page_title="PickMe Investor Assistant",
    page_icon="👋",
    layout="wide"
)

# --- Header ---
st.title("Welcome to the PickMe Investor Assistant!")
st.markdown(
    """
    This is an interactive, multi-page application designed to assist with investment-related tasks.
    **👈 Select a feature from the sidebar** to get started.
    """
)
st.divider()

# --- Features Section ---
st.header("Features")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🤖 PickMe AI Assistant")
    st.write("A chatbot that can answer your questions about PickMe based on the provided documents.")

    st.subheader("📊 Valuation")
    st.write("(Under Construction) Tools for financial valuation.")

with col2:
    st.subheader("📈 Stock Analysis")
    st.write("(Under Construction) Tools for analyzing stock performance.")

    st.subheader("⚙️ Portfolio Optimization")
    st.write("(Under Construction) Tools for optimizing your investment portfolio.")

st.sidebar.success("Select a feature above.")


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