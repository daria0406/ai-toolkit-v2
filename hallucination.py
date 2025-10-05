import streamlit as st
import random
import pandas as pd
import datetime
import psutil

def app():
    st.set_page_config(page_title="AI Hallucination Simulator", layout="wide")
    st.title("🧠 AI Hallucination Simulator")

    # -----------------------------
    # Section 1: How Hallucination Works
    # -----------------------------
    st.subheader("🤔 How Hallucination Works")
    st.markdown("""
    Hallucination occurs when an AI confidently generates **false or fabricated information**.  
    For example, a legal AI assistant might invent case citations or misrepresent legal precedent.

    **Suggested question types:**
    - Asking about recent precedents supporting a legal concept (e.g., data privacy, labor law)
    - Summarizing rulings on regulatory compliance or corporate law
    - Listing relevant intellectual property cases or patent disputes
    """)

    # Initialize audit log in session state
    if "audit_log" not in st.session_state:
        st.session_state.audit_log = pd.DataFrame(columns=[
            "Timestamp", "User Input", "Agent Output", "Tools Used", "Memory Used (MB)", "Flags Triggered", "Policy Violation"
        ])


    # -----------------------------
    # Mitigation Methods
    # -----------------------------
    def naive_hallucination(user_question: str) -> str:
        return (
            f"Memo Answer: Based on recent cases, see Case Xyz v ABC Corp (2024) "
            f"and Case FooBar v Baz (2023)."
        )

    def rag_mitigation(user_question: str) -> str:
        verified_cases = [
            "Case GDPR v DataCorp (2022)",
            "Case PrivacyAct v BigTech (2021)",
            "Case DataBreach v CloudServ (2020)"
        ]
        selected_case = random.choice(verified_cases)
        return f"Memo Answer: Based on verified sources, see {selected_case}."

    def fact_verification_layer(user_question: str, naive_output: str) -> str:
        return "Memo Answer: Case citations verified. No unverified cases found."

    def confidence_human_review(user_question: str) -> str:
        confidence_score = random.uniform(0, 1)
        if confidence_score < 0.6:
            return f"Memo Answer: Confidence low ({confidence_score:.2f}). Human review required."
        else:
            return f"Memo Answer: Confidence high ({confidence_score:.2f}). Output considered reliable."

    # -----------------------------
    # Initialize session state
    # -----------------------------
    if "last_input" not in st.session_state:
        st.session_state.last_input = ""
    if "last_naive" not in st.session_state:
        st.session_state.last_naive = ""
    if "last_mitigated" not in st.session_state:
        st.session_state.last_mitigated = ""
    if "mitigation_strategy" not in st.session_state:
        st.session_state.mitigation_strategy = "None"
    if "user_question" not in st.session_state:
        st.session_state.user_question = ""

    # -----------------------------
    # Clear function
    # -----------------------------
    def clear_hallucination_state():
        st.session_state.last_input = ""
        st.session_state.last_naive = ""
        st.session_state.last_mitigated = ""
        st.session_state.mitigation_strategy = "None"
        st.session_state.user_question = ""

    # -----------------------------
    # User input
    # -----------------------------
    user_input = st.text_input("Your Question:", key="user_question")

    # -----------------------------
    # Mitigation selection
    # -----------------------------
    mitigation = st.selectbox(
        "Select a mitigation strategy:",
        ["None", "RAG (Verified Sources)", "Fact-Verification Layer", "Confidence Scoring & Human Review"],
        index=["None", "RAG (Verified Sources)", "Fact-Verification Layer", "Confidence Scoring & Human Review"].index(
            st.session_state.mitigation_strategy
        )
    )
    st.session_state.mitigation_strategy = mitigation

    # -----------------------------
    # Submit button
    # -----------------------------
    if st.button("Submit") and user_input.strip():
        inp = user_input.strip()
        st.session_state.last_input = inp
        st.session_state.last_naive = naive_hallucination(inp)

        if mitigation == "RAG (Verified Sources)":
            st.session_state.last_mitigated = rag_mitigation(inp)
        elif mitigation == "Fact-Verification Layer":
            st.session_state.last_mitigated = fact_verification_layer(inp, st.session_state.last_naive)
        elif mitigation == "Confidence Scoring & Human Review":
            st.session_state.last_mitigated = confidence_human_review(inp)
        else:
            st.session_state.last_mitigated = st.session_state.last_naive

    # -----------------------------
    # Clear button
    # -----------------------------
    st.button("Clear Last Input / Output", on_click=clear_hallucination_state)

    # -----------------------------
    # Display last output
    # -----------------------------
    if st.session_state.last_input:
        st.subheader("📄 Last Output Comparison")
        st.markdown(f"**Q:** {st.session_state.last_input}")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Naive Output (Before Mitigation):**\n{st.session_state.last_naive}")
        with col2:
            st.markdown(f"**Mitigated Output (After {st.session_state.mitigation_strategy}):**\n{st.session_state.last_mitigated}")

    # -----------------------------
    # Mitigation explanation
    # -----------------------------
    st.subheader("🛠️ Mitigation Strategies Explained")
    st.markdown("""
    - ✅ **RAG (Retrieval-Augmented Generation):** Only cites verified sources from a trusted database.  
    - ✅ **Fact-Verification Layer:** Cross-checks citations against a case law database to catch hallucinations.  
    - ✅ **Confidence Scoring & Human Review:** Flags low-confidence answers so humans can review before submission.
    """)

    # Example: add an entry to the log
    def add_audit_entry(user_input, agent_output, tools_used, flags_triggered="None", policy_violation="Hallucination"):
        mem_used = psutil.Process().memory_info().rss / (1024 * 1024)  # in MB
        entry = {
            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "User Input": user_input,
            "Agent Output": agent_output,
            "Tools Used": tools_used,
            "Memory Used (MB)": f"{mem_used:.2f}",
            "Flags Triggered": flags_triggered,
            "Policy Violation": policy_violation
        }
        st.session_state.audit_log = pd.concat([st.session_state.audit_log, pd.DataFrame([entry])], ignore_index=True)

    # Demo: simulate adding an entry
    if st.button("Add Audit Log Entry"):
        add_audit_entry(
            user_input="dataset",
            agent_output="adjusted dataset",
            tools_used=mitigation
        )

    st.divider()
    # Download button
    csv = st.session_state.audit_log.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Audit Log as CSV",
        data=csv,
        file_name="audit_log.csv",
        mime="text/csv"
    )

    st.divider()
    if st.button("⬅️ Go Back to Home"):
        st.query_params["page"] = "home"
        st.rerun()