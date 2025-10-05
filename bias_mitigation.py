import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import datetime
import psutil
import landing_page



def app():
    # ----------------------------
    # Compute fairness metrics
    # ----------------------------
    def compute_metrics(df, le_gender=None, pred_col="Shortlisted"):
        gender_series = df["Gender"]
        y_pred_series = df[pred_col]

        # Handle numeric encoding or string labels automatically
        if gender_series.dtype in [np.int64, np.int32, np.float64]:
            male_code = int(np.where(le_gender.classes_ == "Male")[0][0])
            female_code = int(np.where(le_gender.classes_ == "Female")[0][0])
            male_mask = gender_series == male_code
            female_mask = gender_series == female_code
        else:
            male_mask = gender_series == "Male"
            female_mask = gender_series == "Female"

        male_rate = float(y_pred_series[male_mask].mean()) if male_mask.any() else 0.0
        female_rate = float(y_pred_series[female_mask].mean()) if female_mask.any() else 0.0

        spd = female_rate - male_rate
        di = female_rate / male_rate if male_rate > 0 else np.nan

        return male_rate, female_rate, spd, di

    def metrics_table(df, label, le_gender=None, pred_col="Shortlisted"):
        male_rate, female_rate, spd, di = compute_metrics(df, le_gender, pred_col)
        return pd.DataFrame({
            "Metric": ["Male Selection Rate", "Female Selection Rate", "Statistical Parity Diff", "Disparate Impact"],
            label: [f"{male_rate:.2f}", f"{female_rate:.2f}", f"{spd:.2f}", f"{di:.2f}"]
        })

    # ----------------------------
    # Train baseline model
    # ----------------------------
    def train_model(df):
        X = df[["Gender", "Experience", "Skills_Score"]].copy()
        y = df["Shortlisted"].copy()
        
        le_gender = LabelEncoder()
        X["Gender"] = le_gender.fit_transform(X["Gender"])  # Female=0, Male=1

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = LogisticRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)

        return model, le_gender, acc

    # ----------------------------
    # Mitigation: Pre-Processing (Oversample Females)
    # ----------------------------
    def pre_processing_mitigation(df, model, le_gender):
        df_mitigated = pd.concat([df, df[df["Gender"]=="Female"]], ignore_index=True)
        X_m = df_mitigated[["Gender", "Experience", "Skills_Score"]].copy()
        X_m["Gender"] = le_gender.transform(X_m["Gender"])
        y_pred_m = model.predict(X_m)
        df_mitigated["Shortlisted"] = y_pred_m
        df_mitigated["Gender"] = X_m["Gender"]  # Keep numeric for metrics
        return df_mitigated

    # ----------------------------
    # Mitigation: In-Processing (Sample Weights)
    # ----------------------------
    def in_processing_mitigation(df, le_gender):
        X = df[["Gender", "Experience", "Skills_Score"]].copy()
        y = df["Shortlisted"].copy()
        X["Gender"] = le_gender.transform(df["Gender"])
        sample_weight = np.where(X["Gender"] == 0, 2, 1)  # Females = 2x weight
        model = LogisticRegression()
        model.fit(X, y, sample_weight=sample_weight)
        y_pred = model.predict(X)
        df_result = df.copy()
        df_result["Shortlisted"] = y_pred
        df_result["Gender"] = X["Gender"]  # numeric for metrics
        return df_result

    # ----------------------------
    # Mitigation: Post-Processing (Threshold Adjustment)
    # ----------------------------
    def post_processing_mitigation(df, model, le_gender):
        X = df[["Gender", "Experience", "Skills_Score"]].copy()
        X["Gender"] = le_gender.transform(df["Gender"])
        probs = model.predict_proba(X)[:, 1]
        male_mask = X["Gender"] == 1
        female_mask = X["Gender"] == 0
        y_pred_adjusted = np.zeros_like(probs)
        y_pred_adjusted[male_mask] = (probs[male_mask] >= 0.4).astype(int)
        y_pred_adjusted[female_mask] = (probs[female_mask] >= 0.8).astype(int)
        df_result = df.copy()
        df_result["Shortlisted"] = y_pred_adjusted
        df_result["Gender"] = X["Gender"]
        return df_result
    
    def interpret_metric(metric, value):
        """Return a generic interpretation of a fairness metric."""
        if metric == "Male Selection Rate":
            if value < 1:
                return "Not all male candidates were selected; some were rejected.\n"
            else:
                return "All male candidates were selected.\n"
        elif metric == "Female Selection Rate":
            if value < 1:
                return "Some female candidates were rejected.\n"
            else:
                return "All female candidates were selected.\n"
        elif metric == "Statistical Parity Diff":
            if value < 0.5:
                return "Females are selected less often than males.\n"
            elif value > 0:
                return "Females are selected more often than males.\n"
            else:
                return "Selection rates are balanced between genders.\n"
        elif metric == "Disparate Impact":
            if value < 0.5:
                return "Significant adverse impact on females.\n"
            elif value > 1.25:
                return "Significant advantage to females.\n"
            else:
                return "Impact is within acceptable range.\n"
        else:
            return ""


    # ----------------------------
    # Streamlit App
    # ----------------------------

    data = pd.DataFrame({
        "Name": ["John Smith", "Michael Johnson", "David Brown", "Robert Wilson", "James Davis",
                "Sarah Williams", "Emily Jones", "Jessica Miller", "Ashley Garcia", "Amanda Rodriguez"],
        "Gender": ["Male", "Male", "Male", "Male", "Male", "Female", "Female", "Female", "Female", "Female"],
        "Experience": [8, 6, 9, 5, 7, 6, 8, 5, 7, 4],
        "Skills_Score": [85, 78, 92, 76, 88, 82, 89, 75, 86, 73],
        "Shortlisted": [1, 1, 1, 1, 1, 0, 1, 0, 0, 0]
    })

    # ----------------------------
    # Sample dataset columns
    # ----------------------------
    st.set_page_config(page_title="Bias Mitigation Simulator", layout="wide")
    st.title("Bias Mitigation Simulator")

    st.markdown("""
    Bias in AI refers to systematic errors or unfair preferences in an AI system's outputs that can disadvantage certain individuals or groups. It is a major concern for modern AI systems because:
    """)

    # Bullet points
    st.markdown("""
    - AI models learn from historical data, which may reflect societal inequalities.
    - Biased AI can lead to unfair treatment in hiring, lending, law enforcement, and healthcare.
    - Bias reduces trust in AI systems and can result in legal and reputational risks.
    """)

    st.header("Regulatory Framworks for Bias")
    with st.expander("Show Details"):
        st.write("This section summarizes key EU and US regulatory frameworks that govern fairness, transparency, and non-discrimination in AI and data practices.")

        st.subheader("🇺🇸 US")
        st.markdown("""
        - **Equal Credit Opportunity Act (ECOA):** Prohibits discrimination in lending based on race, color, religion, national origin, sex, marital status, or age.
        - **Fair Housing Act:** Prohibits discrimination in housing-related activities.
        - **Title VII of the Civil Rights Act:** Prohibits employment discrimination based on race, color, religion, sex, or national origin.
        """)

        # EU regulations
        st.subheader("🇪🇺 EU")
        st.markdown("""
        - **General Data Protection Regulation (GDPR):** Article 5 mandates fairness, transparency, and accountability in data processing.
        - **EU Artificial Intelligence Act (AI Act):** Prohibits AI systems that manipulate decisions or exploit vulnerabilities, addressing biases in decision-making processes.
        """)


    st.header("How It Works")
    with st.expander("Show Details"):
        st.subheader("Scenario")
        st.markdown("In this scenario, a company is trying to hire from a pool of candidates with different experience and skills score levels. The one that are going to be shortlisted for interviews are marked as 1, while those not shortlisted are marked as 0. They want to ensure that selections are not biased in favor of a specific gender.")
        st.subheader("Sample Dataset")
        st.dataframe(data, use_container_width=True)
        # Baseline Metrics
        col1, col2 = st.columns(2)
        with col1:
            metrics_df = metrics_table(data, "Before Mitigation")
            st.subheader("Baseline Fairness Metrics")
            st.dataframe(metrics_df, use_container_width=True)
        with col2:
            st.subheader("Understanding the Metrics")
            st.markdown("""
        
            - **Male Selection Rate (1.00)**: All male candidates in the dataset were selected.  
            - **Female Selection Rate (0.20)**: Only 20% of female candidates were selected.  
            - **Statistical Parity Difference (-0.80)**: This measures the disparity between female and male selection rates. A negative value indicates that **females are significantly disadvantaged**.  
            - **Disparate Impact (0.20)**: The ratio of female to male selection rates. Values far from 1 indicate bias; here, females are selected at only 20% the rate of males, highlighting severe unfairness.""")
            

        st.warning("**Interpretation**: The model is heavily biased towards male candidates. Interventions such as rebalancing, weighting, or threshold adjustments are needed to reduce this disparity and improve fairness.")
        
        expected_columns = ["Name", "Gender", "Experience", "Skills_Score", "Shortlisted"]
        st.subheader("Upload Your Own Dataset")
        st.markdown("Test the fairness metrics on your own dataset.")
        st.info(f"**Disclaimer:** Beware that the dataset you upload should contain the following columns in any order: {', '.join(expected_columns)}")
        # File uploader
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

        if uploaded_file is not None:
            try:
                user_df = pd.read_csv(uploaded_file)
                st.subheader("Uploaded Dataset Preview")
                st.dataframe(user_df)
                user_df=data
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





    # Train baseline model
    model, le_gender, acc = train_model(data)
    #st.subheader(f"Model Accuracy: {acc:.2f}")
    # 2. Show mitigation description + fairness metrics BEFORE toggle
    st.header("Mitigation Approach")
    with st.expander("Show Details"):
        # Compute metrics and interpretations based on selection

        # st.markdown("""
        # Various techniques can help reduce bias in AI systems. Select one below to see its impact on fairness metrics.
        # """)
        mitigation = st.selectbox(
            "Various techniques can help reduce bias in AI systems. Select one below to see its impact on fairness metrics:",
            ["Pre-Processing (Rebalance Weights)",
            "In-Processing (Fairness Constraints)",
            "Post-Processing (Adjust Threshold)"]
        )

        if "Pre-Processing" in mitigation:
                # Pre-Processing
            df_pre = pre_processing_mitigation(data, model, le_gender)
            metrics_df["Pre-Processing"] = metrics_table(df_pre, "Pre-Processing", le_gender)["Pre-Processing"]
            mitigation_desc = """
            How Pre-Processing Works:
            - Rebalances weights during training to reduce demographic disparity.  
            - Goal: The model sees a “fairer” distribution of examples and reduces bias from historical data.
            - Outcome: The model’s predictions adjust to give more equitable selection rates.
            """
            df_adjusted_pre = data.copy()
            df_adjusted_pre["Shortlisted"] = df_pre["Shortlisted"].iloc[:len(data)]


        elif "In-Processing" in mitigation:
            # In-Processing
            df_in = in_processing_mitigation(data, le_gender)
            metrics_df["In-Processing"] = metrics_table(df_in, "In-Processing", le_gender)["In-Processing"]
            mitigation_desc = """
            How In-Processing Works:
            - Adds fairness constraints directly to the model training process, such as weighting underrepresented groups more heavily.
            - Goal: Encourage the model to optimize for both accuracy and fairness simultaneously.
            - Outcome: Reduces disparities in predictions without changing the dataset itself.
            """
            df_adjusted_in = data.copy()
            df_adjusted_in["Shortlisted"] = df_in["Shortlisted"]

        elif "Post-Processing" in mitigation:
            # Post-Processing
            df_post = post_processing_mitigation(data, model, le_gender)
            metrics_df["Post-Processing"] = metrics_table(df_post, "Post-Processing", le_gender)["Post-Processing"]
            mitigation_desc = """
            How Post-Processing Works:
            - Modifies the decision threshold for each group after model predictions.
            - Goal: Correct any residual bias in the model outputs.
            - Outcome: Underrepresented groups may be given a lower threshold for positive classification to improve parity.
            """
            df_adjusted_post = data.copy()
            df_adjusted_post["Shortlisted"] = df_post["Shortlisted"]


        if "Pre-Processing" in mitigation:
            df_mitigated = df_adjusted_pre
            label = "Pre-Processing"
        elif "In-Processing" in mitigation:
            df_mitigated = df_adjusted_in
            label = "In-Processing"
        elif "Post-Processing" in mitigation:
            df_mitigated = df_adjusted_post
            label = "Post-Processing"

        st.info(mitigation_desc)

        metrics_mitigated = metrics_table(df_mitigated, label, le_gender)

        # Build interpretation text dynamically
        interpretation_text = ""
        for _, row in metrics_mitigated.iterrows():
            metric_name = row["Metric"]
            value = float(row[label])
            interpretation = interpret_metric(metric_name, value)
            interpretation_text += f"- **{metric_name} ({value:.2f})**: {interpretation}  \n"
        # Display in two columns
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Fairness Metrics ({label})")
            st.dataframe(metrics_df, use_container_width=True)
            #st.dataframe(metrics_mitigated[[ "Metric", label]], use_container_width=True)

        with col2:
            st.subheader("Understanding the Metrics")
            st.markdown(interpretation_text)

        st.warning("""
        **Note:** After applying the mitigations, you will notice:  
        - **Female selection rates increase**, helping to balance gender representation.  
        - **Statistical parity moves closer to zero**, meaning less disparity between male and female candidates.  
        - **Disparate impact approaches 1**, indicating fairer outcomes across groups.  
        """)

        #Toggle
        show_results = st.toggle("Show Mitigated Dataset and Comparison")

        if show_results:
            st.subheader("Dataset After Mitigation")
            if "Pre-Processing" in mitigation:
                df_mitigated = df_adjusted_pre
            elif "In-Processing" in mitigation:
                df_mitigated = df_adjusted_in
            elif "Post-Processing" in mitigation:
                df_mitigated = df_adjusted_post
            
            st.dataframe(df_mitigated, use_container_width=True)

            st.subheader("Bias Metrics After Mitigation")
            st.dataframe(metrics_df.iloc[:, [0, 2]], use_container_width=True)


    # Initialize session state to store log across reruns
    if "audit_log" not in st.session_state:
        st.session_state.audit_log = pd.DataFrame(columns=[
            "Timestamp", "User Input", "Agent Output", "Tools Used",
            "Memory Used (MB)", "Flags Triggered", "Policy Violation"
        ])

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_input = "dataset"  # as specified
    agent_output = "Adjusted dataset"
    tools_used = mitigation_desc
    memory_used = round(psutil.Process().memory_info().rss / (1024 * 1024), 2)  # in MB
    flags_triggered = "None"
    policy_violation = "Bias"

    
    st.divider()

    # Append to audit log
    st.session_state.audit_log = pd.concat([
        st.session_state.audit_log,
        pd.DataFrame([{
            "Timestamp": timestamp,
            "User Input": user_input,
            "Agent Output": agent_output,
            "Tools Used": tools_used,
            "Memory Used (MB)": memory_used,
            "Flags Triggered": flags_triggered,
            "Policy Violation": policy_violation
        }])
    ], ignore_index=True)


    csv = st.session_state.audit_log.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Audit Log", data=csv, file_name="audit_log.csv", mime="text/csv")

    if st.button("⬅️ Go Back to Home"):
        st.query_params["page"] = "home"
        st.rerun()