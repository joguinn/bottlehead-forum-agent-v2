import streamlit as st
import pandas as pd
from forum_agent import forum_agent, ask_forum_agent

# URL to your hosted CSV (must end in &raw=1)
CSV_URL = "https://www.dropbox.com/scl/fi/e5v4hxp68apt7n13hits6/bottlehead_qna.csv?rlkey=ly6wrdcyobqqj4ug2gr9cin61&raw=1"

# App layout
st.set_page_config(page_title="Bottlehead Forum Agent", layout="wide")
st.title("🧠 Bottlehead Forum Support Agent")

# Load CSV from Dropbox
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip().str.lower()  # Normalize column names
        return df
    except Exception as e:
        st.error(f"❌ Failed to load CSV: {e}")
        return pd.DataFrame()

# Load data
df = load_data()

# Validate CSV content
if df.empty or "question" not in df.columns or "answer" not in df.columns:
    st.error("CSV must contain at least 'question' and 'answer' columns.")
    st.stop()

# Build agent
with st.spinner("🔧 Building the forum agent..."):
    try:
        forum_agent = build_forum_agent(df)
    except Exception as e:
        st.error(f"❌ Error building agent: {e}")
        st.stop()

# Product filter (if product column is present)
product_filter = None
if "product" in df.columns:
    products = ["All"] + sorted(df["product"].dropna().unique().tolist())
    selected_product = st.selectbox("Filter by product:", products)
    if selected_product != "All":
        product_filter = selected_product

# Query input
query = st.text_input("Ask a question about Bottlehead kits:", placeholder="e.g., How do I wire the Speedball upgrade?")

# Handle query
if query:
    with st.spinner("🧠 Thinking..."):
        try:
            result = ask_forum_agent(query, product=product_filter)
            st.markdown("### ✅ Answer")
            st.write(result)
        except Exception as e:
            st.error(f"❌ Error answering question: {e}")
