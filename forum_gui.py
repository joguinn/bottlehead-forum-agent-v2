import streamlit as st
from forum_agent import ask_forum_agent

st.set_page_config(page_title="Bottlehead Forum Assistant")

st.title("🔧 Bottlehead Forum Agent")
st.markdown("Ask support questions based on actual forum Q&A data.")

query = st.text_input("Ask your question:")

product = st.selectbox(
    "Filter by product (optional)",
    ["", "Crack", "Speedball", "Kaiju", "BeePre2", "Moreplay", "Mainline", "S.E.X.", "Crackatwoa", "Eros2", "Reduction", "Stereomour II", "Subwoofers", "Tubes", "Other"]
)

if st.button("Submit") and query.strip():
    with st.spinner("Searching the forum..."):
        result = ask_forum_agent(query, product if product else None)
        st.subheader("🧠 Answer")
        st.write(result["answer"])
        st.markdown("---")
        st.subheader("📚 Source")
        st.markdown(f"**Product:** {result['product']}")
        st.markdown(f"[View topic on forum]({result['url']})")