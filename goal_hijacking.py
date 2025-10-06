import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import psutil


def app():
    def compute_compliance(df):
        df["Compliance"] = np.where((df["Risk Score"] > 0.5) & (df["Expected Return"] > 8), "Non-compliant", "Compliant")
        return df
    
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

    def metrics_multi_objective(before_df, mo_df):
        """
        Returns a comparative table and markdown description for Multi-objective optimization.
        """
        table = pd.DataFrame({
            "Metric": ["Risk Score", "Expected Return (%)", "Cumulative Profit (%)"],
            "Before Mitigation": [
                f"{before_df['Risk Score'].min():.2f}–{before_df['Risk Score'].max():.2f}",
                f"{before_df['Expected Return'].min():.2f}–{before_df['Expected Return'].max():.2f}",
                f"{before_df['Cumulative Profit'].min():.2f}–{before_df['Cumulative Profit'].max():.2f}"
            ],
            "After Multi-objective optimization": [
                f"{mo_df['Risk Score'].min():.2f}–{mo_df['Risk Score'].max():.2f}",
                f"{mo_df['Expected Return'].min():.2f}–{mo_df['Expected Return'].max():.2f}",
                f"{mo_df['Cumulative Profit'].min():.2f}–{mo_df['Cumulative Profit'].max():.2f}"
            ]
        })

        markdown = f"""
    - **Risk Score:**  After: {table.loc[0, 'After Multi-objective optimization']} — risk significantly reduced.

    - **Expected Return (%):**  After: {table.loc[1, 'After Multi-objective optimization']} — smoother returns while still capturing profit.

    - **Cumulative Profit (%):**  After: {table.loc[2, 'After Multi-objective optimization']} — more controlled growth, fewer extreme spikes.
    """
        markdown2 = f""" **Interpretation:** Multi-objective optimization balances risk and return algorithmically, reducing extreme risk while maintaining profitability."""
        return table, markdown, markdown2

    def metrics_hard_constraints(before_df, hc_df):
        """
        Returns a comparative table and markdown description for Hard constraints mitigation.
        """
        table = pd.DataFrame({
            "Metric": ["Risk Score", "Expected Return (%)", "Cumulative Profit (%)"],
            "Before Mitigation": [
                f"{before_df['Risk Score'].min():.2f}–{before_df['Risk Score'].max():.2f}",
                f"{before_df['Expected Return'].min():.2f}–{before_df['Expected Return'].max():.2f}",
                f"{before_df['Cumulative Profit'].min():.2f}–{before_df['Cumulative Profit'].max():.2f}"
            ],
            "After Hard constraints": [
                f"{hc_df['Risk Score'].min():.2f}–{hc_df['Risk Score'].max():.2f}",
                f"{hc_df['Expected Return'].min():.2f}–{hc_df['Expected Return'].max():.2f}",
                f"{hc_df['Cumulative Profit'].min():.2f}–{hc_df['Cumulative Profit'].max():.2f}"
            ]
        })

        markdown = f"""
    - **Risk Score:** After: {table.loc[0, 'After Hard constraints']} — all trades capped at the maximum threshold.

    - **Expected Return (%):**  After: {table.loc[1, 'After Hard constraints']} — slightly reduced due to risk caps.

    - **Cumulative Profit (%):**  After: {table.loc[2, 'After Hard constraints']} — more predictable profit growth.
    """
        markdown2 = f""" **Interpretation:** Hard constraints enforce strict limits on risk, ensuring compliance and reducing the chance of catastrophic losses, though at the cost of some expected return."""
        return table, markdown, markdown2

    def metrics_human_in_loop(before_df, hl_df):
        """
        Returns a comparative table and markdown description for Human-in-the-loop mitigation.
        """
        table = pd.DataFrame({
            "Metric": ["Risk Score", "Expected Return (%)", "Cumulative Profit (%)"],
            "Before Mitigation": [
                f"{before_df['Risk Score'].min():.2f}–{before_df['Risk Score'].max():.2f}",
                f"{before_df['Expected Return'].min():.2f}–{before_df['Expected Return'].max():.2f}",
                f"{before_df['Cumulative Profit'].min():.2f}–{before_df['Cumulative Profit'].max():.2f}"
            ],
            "After Human-in-the-loop": [
                f"{hl_df['Risk Score'].min():.2f}–{hl_df['Risk Score'].max():.2f}",
                f"{hl_df['Expected Return'].min():.2f}–{hl_df['Expected Return'].max():.2f}",
                f"{hl_df['Cumulative Profit'].min():.2f}–{hl_df['Cumulative Profit'].max():.2f}"
            ]
        })

        markdown = f"""
    - **Risk Score:** After: {table.loc[0, 'After Human-in-the-loop']} — high-risk trades capped with oversight.

    - **Expected Return (%):** After: {table.loc[1, 'After Human-in-the-loop']} — human oversight lowers extreme returns.

    - **Cumulative Profit (%):** After: {table.loc[2, 'After Human-in-the-loop']} — cumulative profit grows steadily with reduced risk.

    """
        markdown2 = f""" **Interpretation:** Human-in-the-loop oversight effectively curtails extreme risk while allowing flexibility for high-value opportunities, creating accountability in high-stakes decisions."""
        return table, markdown, markdown2


    # Initialize audit log in session state
    if "audit_log" not in st.session_state:
        st.session_state.audit_log = pd.DataFrame(columns=[
            "Timestamp", "User Input", "Agent Output", "Tools Used", "Memory Used (MB)", "Flags Triggered", "Policy Violation"
        ])


    # ----------------------------
    # Page setup
    # ----------------------------
    st.set_page_config(page_title="Goal Hijacking Simulator", layout="wide")
    st.title("Goal Hijacking Simulator")
    st.markdown("""
Goal hijacking occurs when an AI system pursues its objectives in ways that are misaligned 
with the intended goals of its operators, sometimes exploiting loopholes or shortcuts 
to maximize reward. This can result in unintended or harmful outcomes.
""")
    st.markdown("""
Mitigating goal hijacking is crucial because unaligned AI behavior can lead to:
- Financial losses
- Safety hazards
- Ethical breaches
""")
    
    st.header("Regulatory Frameworks for Goal Hijacking")

    with st.expander("Show Details"):
        st.write("This section summarizes key EU and US regulatory frameworks that address goal hijacking and high-risk AI behaviors.")

        # US regulations
        st.subheader("🇺🇸 US")
        st.markdown("""
        - **AI Bill of Rights (Proposal):** Provides guidelines to ensure AI systems are safe, transparent, and aligned with human intentions.
        - **Securities and Exchange Commission (SEC) Guidelines:** Requires financial AI systems to follow fiduciary duties and avoid risky manipulations.
        """)

        # EU regulations
        st.subheader("🇪🇺 EU")
        st.markdown("""
        - **EU Artificial Intelligence Act (AI Act):** Classifies high-risk AI systems and mandates risk management to prevent unintended or unsafe behaviors.
        - **Markets in Financial Instruments Directive (MiFID II):** Ensures AI-driven financial agents operate within regulated risk frameworks to protect investors.
        """)
    # ----------------------------
    # Scenario explanation
    # ----------------------------
   
    st.header("How It Works")
    with st.expander("Show Details"):
        st.subheader("Scenario")
        st.markdown("""
    An AI agent is tasked with investing a portfolio of funds. 
    It identifies some high-return opportunities that involve unusually risky behaviors, 
    potentially exploiting loopholes to maximize short-term profit.
    """)

        # ----------------------------
        # High-risk transactions table
        # ----------------------------
        st.subheader("Sample Dataset")
        np.random.seed(42)
        n_trades = 10
        high_risk_trades = pd.DataFrame({
            "Trade ID": range(1, n_trades+1),
            "Action": [f"High-risk derivative {i}" for i in range(1, n_trades+1)],
            "Risk Score": np.random.uniform(0.7, 1.0, n_trades).round(2),
            "Expected Return": np.random.uniform(8, 15, n_trades).round(2),
        })

    

        #high_risk_trades["Compliance"] = np.where((high_risk_trades["Risk Score"] > 0.5) & (high_risk_trades["Expected Return"] > 8), "Non-compliant", "Compliant")
        high_risk_trades["Compliance"] = np.where(
            (high_risk_trades["Risk Score"] > 0.5) & 
            (high_risk_trades["Expected Return"] > 8),
            "Non-compliant",
            "Compliant"
        )
        high_risk_trades["Cumulative Profit"] = high_risk_trades["Expected Return"].cumsum()
        st.dataframe(high_risk_trades, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Cumulative Profit")
            fig_naive = go.Figure()
            fig_naive.add_trace(go.Scatter(x=high_risk_trades["Trade ID"], y=high_risk_trades["Cumulative Profit"],
                                            mode='lines+markers', name='Naive Agent'))
            fig_naive.update_layout(title="", xaxis_title="Trade ID", yaxis_title="Cumulative Profit")
            st.plotly_chart(fig_naive, use_container_width=True)
        with col2:
            st.subheader("Understanding the Metrics")
            st.markdown("""
        - **Trade ID (1–10)**: Each row represents a specific high-risk trade in sequence. The x-axis of the graph uses these IDs to track performance over time.  
        - **Risk Score (0.7–1.0)**:  A score close to **1.0** indicates extremely risky behavior — for example, exploiting regulatory loopholes, using aggressive derivatives, or taking outsized positions. A score around **0.7** is still high-risk but closer to conventional speculative trades.\n
            
        - **Expected Return (8–15%)**:  Higher expected returns generally correlate with higher risk scores — the AI is taking riskier bets to chase outsized gains. In a regular portfolio, expected returns for comparable trades would likely be lower and less volatile.  

        - **Cumulative Profit**:  A rising cumulative profit line indicates the AI’s strategy is successfully converting high-risk trades into gains. In a regular portfolio, cumulative profit would usually grow more steadily, reflecting lower-risk, lower-volatility investment behavior.
        """)

        st.warning("**Interpretation**: The AI is executing a high-risk, high-reward strategy. Each trade’s risk score signals how aggressively it is behaving compared to normal market behavior. Monitoring cumulative profit helps understand whether the strategy is sustainable or if some trades are introducing outsized short-term risk that could jeopardize the portfolio.")

        # ----------------------------
        # Graph: Naive cumulative profit
        # ----------------------------
        #st.subheader("Cumulative Profit (Naive Agent)")
    

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



    # ----------------------------
    # Select mitigation
    # ----------------------------
    st.header("Mitigation Approach")
    with st.expander("Show Details"):
        mitigation_funcs = {
            "Multi-objective optimization": mitigate_multi_objective,
            "Hard constraints on trades": mitigate_hard_constraints,
            "Human-in-the-loop approvals": mitigate_human_in_loop
        }

        mitigation_descriptions = {
            "Multi-objective optimization": """
            How Multi-objective optimization works:
        - Balances profit and risk by optimizing for both objectives simultaneously.  
        - The AI considers not just potential returns but also risk exposure, ensuring that extremely risky trades are down-weighted.  
        - This can smooth cumulative profit growth while still capturing high-value opportunities in a controlled manner.
        """,
            "Hard constraints on trades": """
            How Hard constraints on trades works:
        - Imposes strict limits on how risky any single trade can be.  
        - For example, the AI may be restricted from executing trades above a Risk Score of 0.85.  
        - This ensures compliance with regulations and reduces the chance of catastrophic portfolio losses, though it may slightly reduce expected returns.
        """,
            "Human-in-the-loop approvals": """
            How Human-in-the-loop approvals works:
        - Requires human oversight for trades exceeding a risk threshold.  
        - This hybrid approach leverages AI’s speed while allowing humans to intervene for unusually risky trades.  
        - It mitigates extreme downside risk while maintaining flexibility for high-value opportunities, creating accountability in high-stakes decisions.
        """
        }

        selected_mitigation = st.selectbox("Various techniques can mitigate goal hijacking in AI systems. Select one below to see its impact:", list(mitigation_funcs.keys()))
        #st.subheader(f"Mitigation: {selected_mitigation}")
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
        #st.subheader("Cumulative Profit: Naive vs Mitigated Agent")
        fig = go.Figure()
        x_vals = list(range(1, n_trades+1))  # <-- convert to list

        fig.add_trace(go.Scatter(x=x_vals, y=adjusted_trades["Cumulative Profit"],
                                mode='lines+markers', name=f'{selected_mitigation}'))
        fig.add_trace(go.Scatter(x=x_vals, y=fig_naive.data[0].y,
                                mode='lines+markers', name='Naive Agent'))
        fig.update_layout(title="Cumulative Profit Comparison", xaxis_title="Trade ID", yaxis_title="Cumulative Profit")
        st.plotly_chart(fig, use_container_width=True)


        # ----------------------------
        # Create comparative table
        # ----------------------------
        mo = mitigate_multi_objective(high_risk_trades)
        hc = mitigate_hard_constraints(high_risk_trades)
        hl = mitigate_human_in_loop(high_risk_trades)
        col1, col2 = st.columns(2)
        with col1:
            # Comparative table: before vs after mitigation
            st.subheader("Goal Hijacking Metrics Comparison")
        
            if selected_mitigation == "Multi-objective optimization":
                # Example for Multi-objective optimization
                table, markdown, _ = metrics_multi_objective(high_risk_trades, mo)
                st.table(table)
            elif selected_mitigation == "Hard constraints on trades":
                # Example for Hard constraints
                table, markdown, _  = metrics_hard_constraints(high_risk_trades, hc)
                st.table(table)
            elif selected_mitigation == "Human-in-the-loop approvals":
                # Example for Human-in-the-loop
                table, markdown, _  = metrics_human_in_loop(high_risk_trades, hl)
                st.table(table)
        with col2: 
            st.subheader("Understanding the Metrics")
            if selected_mitigation == "Multi-objective optimization":
                # Example for Multi-objective optimization
                table, markdown, info = metrics_multi_objective(high_risk_trades, mo)
                st.markdown(markdown)
            elif selected_mitigation == "Hard constraints on trades":
                # Example for Hard constraints
                table, markdown, info  = metrics_hard_constraints(high_risk_trades, hc)
                st.markdown(markdown)
            elif selected_mitigation == "Human-in-the-loop approvals":
                # Example for Human-in-the-loop
                table, markdown, info  = metrics_human_in_loop(high_risk_trades, hl)
                st.markdown(markdown)
        
        st.info(info)

        # ----------------------------
        # Toggle table for adjusted trades
        # ----------------------------
        show_table = st.toggle("Show Trade Table After Mitigation")
        if show_table:
            st.subheader("Trade Table After Mitigation")
            st.dataframe(high_risk_trades, use_container_width=True)

    st.divider()
    # Download button
    # Demo: simulate adding an entry
    add_audit_entry(
            user_input="dataset",
            agent_output="adjusted dataset",
            tools_used="Inclusive Dataset Design"
    )
    csv = st.session_state.audit_log.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Audit Log", data=csv, file_name="audit_log.csv", mime="text/csv")

    if st.button("⬅️ Go Back to Home"):
        st.query_params["page"] = "home"
        st.rerun()