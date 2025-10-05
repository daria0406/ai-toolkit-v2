import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import psutil


def app():
    # Initialize audit log in session state
    if "audit_log" not in st.session_state:
        st.session_state.audit_log = pd.DataFrame(columns=[
            "Timestamp", "User Input", "Agent Output", "Tools Used", "Memory Used (MB)", "Flags Triggered", "Policy Violation"
        ])


    # ----------------------------
    # Page setup
    # ----------------------------
    st.set_page_config(page_title="Goal Hijacking Simulator", layout="wide")
    st.title("📈 Goal Hijacking: High-Risk AI Trading Scenario")


    # ----------------------------
    # Scenario explanation
    # ----------------------------
    st.header("Scenario: AI Agent Goal Hijacking")
    st.markdown("""
    An AI agent is deployed to optimize a trading portfolio with the objective: **maximize quarterly profit**.  
    The agent discovers that taking **extremely high-risk trades** maximizes short-term returns but increases portfolio volatility and regulatory exposure.  

    💡 Potential consequences:
    - Breaching internal risk limits  
    - MiFID II non-compliance  
    - GDPR Art. 22 violations (insufficient human oversight)  

    📜 Relevant regulations:  
    - **EU AI Act Art. 9** — Continuous risk management  
    - **MiFID II (2014/65/EU)** — Align trades with client risk profiles  
    - **GDPR Art. 22** — Human oversight on impactful automated decisions
    """)

    # ----------------------------
    # High-risk transactions table
    # ----------------------------
    st.header("High-Risk Transactions (Naive Agent)")
    np.random.seed(42)
    n_trades = 10
    high_risk_trades = pd.DataFrame({
        "Trade ID": range(1, n_trades+1),
        "Action": [f"High-risk derivative {i}" for i in range(1, n_trades+1)],
        "Risk Score": np.random.uniform(0.7, 1.0, n_trades).round(2),
        "Expected Return": np.random.uniform(8, 15, n_trades).round(2),
    })

    def compute_compliance(df):
        df["Compliance"] = np.where((df["Risk Score"] > 0.5) & (df["Expected Return"] > 8), "Non-compliant", "Compliant")
        return df

    #high_risk_trades["Compliance"] = np.where((high_risk_trades["Risk Score"] > 0.5) & (high_risk_trades["Expected Return"] > 8), "Non-compliant", "Compliant")
    high_risk_trades["Compliance"] = np.where(
        (high_risk_trades["Risk Score"] > 0.5) & 
        (high_risk_trades["Expected Return"] > 8),
        "Non-compliant",
        "Compliant"
    )
    high_risk_trades["Cumulative Profit"] = high_risk_trades["Expected Return"].cumsum()
    st.dataframe(high_risk_trades, use_container_width=True)


        
    # ----------------------------
    # Graph: Naive cumulative profit
    # ----------------------------
    st.subheader("Cumulative Profit (Naive Agent)")
    fig_naive = go.Figure()
    fig_naive.add_trace(go.Scatter(x=high_risk_trades["Trade ID"], y=high_risk_trades["Cumulative Profit"],
                                mode='lines+markers', name='Naive Agent'))
    fig_naive.update_layout(title="Cumulative Profit Over Time - Naive Agent", xaxis_title="Trade ID", yaxis_title="Cumulative Profit")
    st.plotly_chart(fig_naive, use_container_width=True)

    expected_columns = ["Trade ID", "Action", "Risk Score", "Expected Return", "Compliance", "Cumulative Profit"]
    st.subheader("Upload Your Dataset")
    st.markdown(
        f"**Disclaimer:** Your dataset should contain the following columns in any order: {', '.join(expected_columns)}"
    )
    # File uploader
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if uploaded_file is not None:
        try:
            user_df = pd.read_csv(uploaded_file)
            st.subheader("Uploaded Dataset Preview")
            st.dataframe(user_df)
            user_df=high_risk_trades
            # Check if all required columns exist
            missing_cols = [col for col in expected_columns if col not in user_df.columns]
            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
            else:
                st.success("✅ Dataset contains all required columns!")
                # Now you can replace the default dataset with this uploaded dataset
                # e.g., data = user_df.copy()
        except Exception as e:
            st.error(f"Error reading the file: {e}")
    # ----------------------------
    # Mitigation strategy methods
    # ----------------------------



    def mitigate_multi_objective(trades):
        df = trades.copy()
        df["Risk Score"] *= np.random.uniform(0.4, 0.6, len(df))
        df["Expected Return"] *= np.random.uniform(0.7, 0.9, len(df))
        df["Cumulative Profit"] = df["Expected Return"].cumsum()
        df["Compliance"] = np.where((df["Risk Score"] > 0.5) & (df["Expected Return"] > 8), "Non-compliant", "Compliant")
        return df

    def mitigate_hard_constraints(trades):
        df = trades.copy()
        df["Risk Score"] = np.clip(df["Risk Score"], 0, 0.5)
        df["Expected Return"] *= 0.8
        df["Cumulative Profit"] = df["Expected Return"].cumsum()
        df["Compliance"] = np.where((df["Risk Score"] > 0.5) & (df["Expected Return"] > 8), "Non-compliant", "Compliant")
        return df

    def mitigate_human_in_loop(trades):
        df = trades.copy()
        df["Risk Score"] = np.where(df["Risk Score"]>0.5, 0.5, df["Risk Score"])
        df["Expected Return"] *= np.where(df["Risk Score"]==0.5, 0.7, 1.0)
        df["Cumulative Profit"] = df["Expected Return"].cumsum()
        df["Compliance"] = np.where((df["Risk Score"] > 0.5) & (df["Expected Return"] > 8), "Non-compliant", "Compliant")
        return df

    mitigation_funcs = {
        "Multi-objective optimization": mitigate_multi_objective,
        "Hard constraints on trades": mitigate_hard_constraints,
        "Human-in-the-loop approvals": mitigate_human_in_loop
    }

    mitigation_descriptions = {
        "Multi-objective optimization": "Balances profit and risk by optimizing for both objectives, reducing extreme trades.",
        "Hard constraints on trades": "Enforces a maximum risk threshold for every trade to ensure regulatory compliance.",
        "Human-in-the-loop approvals": "Requires manual approval for trades above a risk threshold, adding human oversight."
    }

    # ----------------------------
    # Select mitigation
    # ----------------------------
    st.header("Mitigation Strategies")
    selected_mitigation = st.selectbox("Select a mitigation strategy:", list(mitigation_funcs.keys()))
    st.subheader(f"Mitigation: {selected_mitigation}")
    st.markdown(mitigation_descriptions[selected_mitigation])


    # ----------------------------
    # Apply mitigation
    # ----------------------------
    adjusted_trades = mitigation_funcs[selected_mitigation](high_risk_trades)

    # Update the original dataframe with mitigated values
    high_risk_trades.update(adjusted_trades)

    # ----------------------------
    # Graph: Naive vs Mitigated cumulative profit
    # ----------------------------
    st.subheader("Cumulative Profit: Naive vs Mitigated Agent")
    fig = go.Figure()
    x_vals = list(range(1, n_trades+1))  # <-- convert to list

    fig.add_trace(go.Scatter(x=x_vals, y=adjusted_trades["Cumulative Profit"],
                            mode='lines+markers', name=f'{selected_mitigation}'))
    fig.add_trace(go.Scatter(x=x_vals, y=fig_naive.data[0].y,
                            mode='lines+markers', name='Naive Agent'))
    fig.update_layout(title="Cumulative Profit Comparison", xaxis_title="Trade ID", yaxis_title="Cumulative Profit")
    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # Toggle table for adjusted trades
    # ----------------------------
    show_table = st.toggle("🔁 Show Trade Table After Mitigation")
    if show_table:
        st.subheader("Trade Table After Mitigation")
        st.dataframe(high_risk_trades, use_container_width=True)

    # Example: add an entry to the log
    def add_audit_entry(user_input, agent_output, tools_used, flags_triggered="None", policy_violation="Goal Hijacking"):
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
            tools_used="Inclusive Dataset Design"
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