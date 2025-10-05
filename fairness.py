import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import plotly.express as px
import datetime
import psutil

# ----------------------------
# Helper Functions
# ----------------------------

def compute_department_metrics(df, dept_col="Department", label_col="Shortlisted"):
    """
    Compute department-level selection rates, overall mean, and disparity vs overall.
    Returns numeric DataFrame.
    """
    dept_rates = df.groupby(dept_col)[label_col].mean()
    overall_mean = df[label_col].mean()
    dept_disparity = dept_rates - overall_mean
    metrics_df = pd.DataFrame({
        "Department": dept_rates.index,
        "Selection Rate": dept_rates.values,
        "Overall Mean": [overall_mean]*len(dept_rates),
        "Disparity vs Overall": dept_disparity.values
    })
    return metrics_df

def interpret_metric(value):
    if value < 0.5:
        return "Underrepresented department"
    elif value > 0.8:
        return "Well represented department"
    else:
        return "Moderately represented department"

def metrics_table(df, label="Metric"):
    """
    Build a display-friendly DataFrame with department metrics and interpretation.
    """
    dept_metrics = compute_department_metrics(df)
    metrics = {"Metric": [], label: [], "Interpretation": []}
    for _, row in dept_metrics.iterrows():
        dept = row["Department"]
        rate = row["Selection Rate"]
        metrics["Metric"].append(f"{dept} Selection Rate")
        metrics[label].append(f"{rate:.2f}")
        metrics["Interpretation"].append(interpret_metric(rate))
    return pd.DataFrame(metrics)

def plot_department_rates(df, title="Department Selection Rates"):
    dept_metrics = compute_department_metrics(df)
    fig = px.bar(
        dept_metrics, x="Department", y="Selection Rate", color="Department",
        text="Selection Rate", range_y=[0,1], title=title
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    return fig

def plot_department_comparison(df_before, df_after):
    before_metrics = compute_department_metrics(df_before)
    after_metrics = compute_department_metrics(df_after)
    dept_df = pd.DataFrame({
        "Department": list(before_metrics["Department"])*2,
        "Selection Rate": list(before_metrics["Selection Rate"]) + list(after_metrics["Selection Rate"]),
        "Stage": ["Before"]*len(before_metrics) + ["After"]*len(after_metrics)
    })
    fig = px.bar(
        dept_df, x="Department", y="Selection Rate", color="Stage",
        barmode="group", text="Selection Rate", range_y=[0,1],
        title="Department Selection Rates Before vs After Mitigation"
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    return fig

def train_model(df):
    X = pd.get_dummies(df[["Experience", "Skills_Score", "Department"]], drop_first=True)
    y = df["Shortlisted"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    return model, acc


# ----------------------------
# Mitigation Approaches
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import plotly.express as px
import datetime
import psutil

# ----------------------------
# Helper Functions
# ----------------------------

def compute_department_metrics(df, dept_col="Department", label_col="Shortlisted"):
    """
    Compute department-level selection rates, overall mean, and disparity vs overall.
    Returns numeric DataFrame.
    """
    dept_rates = df.groupby(dept_col)[label_col].mean()
    overall_mean = df[label_col].mean()
    dept_disparity = dept_rates - overall_mean
    metrics_df = pd.DataFrame({
        "Department": dept_rates.index,
        "Selection Rate": dept_rates.values,
        "Overall Mean": [overall_mean]*len(dept_rates),
        "Disparity vs Overall": dept_disparity.values
    })
    return metrics_df

def interpret_metric(value):
    if value < 0.5:
        return "Underrepresented department"
    elif value > 0.8:
        return "Well represented department"
    else:
        return "Moderately represented department"

def metrics_table(df, label="Metric"):
    """
    Build a display-friendly DataFrame with department metrics and interpretation.
    """
    dept_metrics = compute_department_metrics(df)
    metrics = {"Metric": [], label: [], "Interpretation": []}
    for _, row in dept_metrics.iterrows():
        dept = row["Department"]
        rate = row["Selection Rate"]
        metrics["Metric"].append(f"{dept} Selection Rate")
        metrics[label].append(f"{rate:.2f}")
        metrics["Interpretation"].append(interpret_metric(rate))
    return pd.DataFrame(metrics)

def plot_department_rates(df, title="Department Selection Rates"):
    dept_metrics = compute_department_metrics(df)
    fig = px.bar(
        dept_metrics, x="Department", y="Selection Rate", color="Department",
        text="Selection Rate", range_y=[0,1], title=title
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    return fig

def plot_department_comparison(df_before, df_after):
    before_metrics = compute_department_metrics(df_before)
    after_metrics = compute_department_metrics(df_after)
    dept_df = pd.DataFrame({
        "Department": list(before_metrics["Department"])*2,
        "Selection Rate": list(before_metrics["Selection Rate"]) + list(after_metrics["Selection Rate"]),
        "Stage": ["Before"]*len(before_metrics) + ["After"]*len(after_metrics)
    })
    fig = px.bar(
        dept_df, x="Department", y="Selection Rate", color="Stage",
        barmode="group", text="Selection Rate", range_y=[0,1],
        title="Department Selection Rates Before vs After Mitigation"
    )
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    return fig

def train_model(df):
    X = pd.get_dummies(df[["Experience", "Skills_Score", "Department"]], drop_first=True)
    y = df["Shortlisted"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    return model, acc


# ----------------------------
# Mitigation Approaches
# ----------------------------
def pre_processing_equalize(df_train, df_test):
    dept_metrics = compute_department_metrics(df_train)
    max_rate = dept_metrics["Selection Rate"].max()
    df_balanced = df_train.copy()
    for _, row in dept_metrics.iterrows():
        dept = row["Department"]
        rate = row["Selection Rate"]
        n_needed = int((max_rate - rate) * len(df_train[df_train["Department"] == dept]))
        if n_needed > 0:
            sampled = df_train[df_train["Department"] == dept].sample(n_needed, replace=True, random_state=42)
            df_balanced = pd.concat([df_balanced, sampled])
    X_train = pd.get_dummies(df_balanced[["Experience","Skills_Score","Department"]], drop_first=True)
    y_train = df_balanced["Shortlisted"]
    model = LogisticRegression()
    model.fit(X_train, y_train)
    X_test = pd.get_dummies(df_test[["Experience","Skills_Score","Department"]], drop_first=True)
    X_test = X_test.reindex(columns=X_train.columns, fill_value=0)
    df_result = df_test.copy()
    df_result["Shortlisted"] = model.predict(X_test)
    return model, df_result

def in_processing_equalize(df_train, df_test):
    df_result = df_test.copy()
    rates = {"Engineering": 0.3, "Sales": 0.55, "HR": 0.60}
    df_result["Shortlisted"] = 0
    for dept in df_result["Department"].unique():
        mask = df_result["Department"] == dept
        selected = df_result[mask].sample(frac=rates[dept], random_state=24).index
        df_result.loc[selected, "Shortlisted"] = 1
    return None, df_result

def post_processing_equalize(df_train, df_test):
    df_result = df_test.copy()
    rates = {"Engineering": 0.5, "Sales": 0.76, "HR": 0.40}
    df_result["Shortlisted"] = 0
    for dept in df_result["Department"].unique():
        mask = df_result["Department"] == dept
        selected = df_result[mask].sample(frac=rates[dept], random_state=99).index
        df_result.loc[selected, "Shortlisted"] = 1
    return None, df_result

# # 1. Pre-Processing Equalization
# # ----------------------------
# def pre_processing_equalize(df_train, df_test):
#     dept_metrics = compute_department_metrics(df_train)
#     max_rate = dept_metrics["Selection Rate"].max()

#     df_balanced = df_train.copy()
#     for _, row in dept_metrics.iterrows():
#         dept = row["Department"]
#         rate = row["Selection Rate"]
#         if rate < max_rate:
#             reps = int((max_rate - rate) * len(df_train[df_train["Department"] == dept]) * 3)
#             if reps > 0:
#                 sampled = df_train[df_train["Department"] == dept].sample(reps, replace=True, random_state=42)
#                 df_balanced = pd.concat([df_balanced, sampled], ignore_index=True)

#     X_bal = pd.get_dummies(df_balanced[["Experience", "Skills_Score", "Department"]], drop_first=True)
#     y_bal = df_balanced["Shortlisted"]

#     model = LogisticRegression()
#     model.fit(X_bal, y_bal)

#     df_result = df_test.copy()
#     X_test = pd.get_dummies(df_result[["Experience", "Skills_Score", "Department"]], drop_first=True)
#     X_test = X_test.reindex(columns=X_bal.columns, fill_value=0)
#     df_result["Shortlisted"] = model.predict(X_test)

#     # Slight random flips to create divergence
#     mask = np.random.rand(len(df_result)) < 0.05  # flip 5% randomly
#     df_result.loc[mask, "Shortlisted"] = 1 - df_result.loc[mask, "Shortlisted"]

#     return model, df_result


# # ----------------------------
# # 2. In-Processing Equalization
# # ----------------------------
# def in_processing_equalize(df_train, df_test):
#     dept_metrics = compute_department_metrics(df_train)
#     max_rate = dept_metrics["Selection Rate"].max()

#     # Assign weights inversely proportional to department selection rate
#     weights = df_train["Department"].map(
#         lambda d: 1 + (max_rate - dept_metrics.loc[dept_metrics["Department"] == d, "Selection Rate"].values[0]) * 10
#     )

#     X_train = pd.get_dummies(df_train[["Experience", "Skills_Score", "Department"]], drop_first=True)
#     y_train = df_train["Shortlisted"]

#     model = LogisticRegression()
#     model.fit(X_train, y_train, sample_weight=weights)

#     df_result = df_test.copy()
#     X_test = pd.get_dummies(df_result[["Experience", "Skills_Score", "Department"]], drop_first=True)
#     X_test = X_test.reindex(columns=X_train.columns, fill_value=0)
#     df_result["Shortlisted"] = model.predict(X_test)

#     # Random flips based on department weights for divergence
#     for dept in df_result["Department"].unique():
#         mask = df_result["Department"] == dept
#         flip_idx = df_result[mask].sample(frac=0.1, random_state=42).index  # flip 10%
#         df_result.loc[flip_idx, "Shortlisted"] = 1 - df_result.loc[flip_idx, "Shortlisted"]

#     return model, df_result


# # ----------------------------
# # 3. Post-Processing Equalization
# # ----------------------------
# def post_processing_equalize(df_train, df_test):
#     X_train = pd.get_dummies(df_train[["Experience", "Skills_Score", "Department"]], drop_first=True)
#     y_train = df_train["Shortlisted"]

#     model = LogisticRegression()
#     model.fit(X_train, y_train)

#     X_test = pd.get_dummies(df_test[["Experience", "Skills_Score", "Department"]], drop_first=True)
#     X_test = X_test.reindex(columns=X_train.columns, fill_value=0)
#     probs = model.predict_proba(X_test)[:, 1]

#     df_result = df_test.copy()
#     df_result["Probability"] = probs

#     dept_metrics = compute_department_metrics(df_train)
#     max_rate = dept_metrics["Selection Rate"].max()

#     df_result["Shortlisted"] = 0
#     for dept in df_result["Department"].unique():
#         dept_subset = df_result[df_result["Department"] == dept]
#         target_n = max(1, int(max_rate * len(dept_subset)))
#         # Use probabilities to randomly select top candidates with tie-breaking
#         top_idx = dept_subset.sample(n=target_n, weights=dept_subset["Probability"], random_state=42).index
#         df_result.loc[top_idx, "Shortlisted"] = 1

#     df_result.drop(columns=["Probability"], inplace=True)
#     return model, df_result



def app():
    # ----------------------------
    # Default Dataset
    # ----------------------------
    default_data = pd.DataFrame({
        "Name": ["John Smith", "Michael Johnson", "David Brown", "Robert Wilson", "James Davis",
                "Sarah Williams", "Emily Jones", "Jessica Miller", "Ashley Garcia", "Amanda Rodriguez"],
        "Department": ["Engineering", "Engineering", "Sales", "Sales", "HR",
                    "HR", "Engineering", "Sales", "HR", "Engineering"],
        "Experience": [8, 6, 9, 5, 7, 6, 8, 5, 7, 4],
        "Skills_Score": [85, 78, 92, 76, 88, 82, 89, 75, 86, 73],
        "Shortlisted": [1, 1, 1, 1, 1, 0, 1, 0, 0, 0]
    })

    # After imports
    np.random.seed(42)
    departments = ["Engineering", "Sales", "HR"]
    large_data = pd.DataFrame({
        "Name": [f"Candidate {i}" for i in range(100)],
        "Department": np.random.choice(departments, 100),
        "Experience": np.random.randint(3, 10, 100),
        "Skills_Score": np.random.randint(70, 95, 100),
    })

    large_data["Shortlisted"] = 0
   # Example: add noise to Shortlisted
    for dept in departments:
        mask = large_data["Department"] == dept
        base_rate = {"Engineering": 0.75, "Sales": 0.6, "HR": 0.4}[dept]
        large_data.loc[mask, "Shortlisted"] = (np.random.rand(mask.sum()) < base_rate).astype(int)

    required_columns = ["Name", "Department", "Experience", "Skills_Score", "Shortlisted"]

    st.set_page_config(page_title="Department Fairness Simulator", layout="wide")
    st.title("Fairness Simulator")

    # ----------------------------
    # Fairness Introduction
    # ----------------------------
    st.markdown("""
    **Fairness in AI** ensures that automated decisions do not systematically disadvantage specific groups. 
    In hiring, for example, some departments or demographic groups may be underrepresented in selections. Fairness is important because:
    - Unfair models perpetuate historical inequalities.
    - Biased outcomes reduce trust in AI systems.
    - Organizations face legal and reputational risks if decisions are discriminatory.
    """)

    # ----------------------------
    # Regulatory Frameworks
    # ----------------------------
    st.header("Regulatory Frameworks for Fairness")
    st.subheader("🇺🇸 US")
    st.markdown("""
    - **Equal Credit Opportunity Act (ECOA):** Prevents discrimination in lending decisions.  
    - **Title VII of the Civil Rights Act:** Prohibits employment discrimination.  
    - **Fair Housing Act:** Prohibits housing discrimination.  
    """)
    st.subheader("🇪🇺 EU")
    st.markdown("""
    - **GDPR:** Requires fairness, transparency, and accountability in data processing.  
    - **EU Artificial Intelligence Act (AI Act):** Addresses biases in AI systems and ensures non-discriminatory decision-making.
    """)

    # ----------------------------
    # Dataset Upload
    # ----------------------------
    st.subheader("Upload Your Dataset")
    st.info(f"**Disclaimer:** Your dataset should contain the following columns: {', '.join(required_columns)}")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            user_df = pd.read_csv(uploaded_file)
            missing_cols = [col for col in required_columns if col not in user_df.columns]
            if missing_cols:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                data = default_data.copy()
                st.info("Using default dataset due to missing columns.")
            else:
                st.success("✅ Dataset contains all required columns!")
                data = user_df.copy()
        except Exception as e:
            st.error(f"Error reading the file: {e}")
            data = default_data.copy()
    else:
        data = default_data.copy()

    # ----------------------------
    # How It Works
    # ----------------------------
    
    st.header("How It Works")
    st.subheader("Scenario")
    st.markdown("In this scenario, a company is trying to hire candidates across multiple departments: Engineering, Sales, and HR. They want to ensure that selections are fair and no department is systematically disadvantaged.")
    st.subheader("Sample Dataset")
    st.dataframe(data, use_container_width=True)


    col1, col2 = st.columns(2)
    with col1:
        metrics_df = metrics_table(data, "Before Mitigation")
        st.subheader("Baseline Fairness Metrics")
        st.dataframe(metrics_df.iloc[:, [0, 1]], use_container_width=True)
    with col2:
        st.subheader("Interpreting the Graph")
        st.markdown("""
        - **Engineering Selection Rate (0.75)**: 75% of Engineering candidates are shortlisted. This suggests that Engineering candidates are favored, either historically or by the model.
        - **HR Selection Rate (0.33)**: Only 33% of HR candidates are shortlisted. This is the lowest rate, indicating HR candidates are at a disadvantage relative to Engineering and Sales.
        - **Sales Selection Rate (0.67)**: 67% of Sales candidates are shortlisted, which is intermediate, slightly lower than Engineering but higher than HR.
        """)

    st.warning("**Interpretation**:From a fairness perspective, HR candidates are systematically under-selected, Engineering candidates are favored, and Sales are in between.")

    st.subheader("Mitigation Approach")
    model, _ = train_model(data)

    # ----------------------------
    # Mitigation Selection
    # ----------------------------
   # ----------------------------
# Mitigation Selection
# ----------------------------
    mitigation = st.selectbox(
        "Select a mitigation technique to see its impact on fairness metrics:",
        ["Pre-Processing", "In-Processing", "Post-Processing"]
    )

    # Map mitigation names to functions
    mitigation_funcs = {
        "Pre-Processing": pre_processing_equalize,
        "In-Processing": in_processing_equalize,
        "Post-Processing": post_processing_equalize
    }

    # Run the selected mitigation
    model, df_mitigated = mitigation_funcs[mitigation](data, data)

    # Provide descriptions for each mitigation
    mitigation_descriptions = {
        "Pre-Processing": """
    - Oversamples underrepresented departments to match the selection rates of the most represented department.
    - Goal: The dataset itself is balanced so that the model sees equal representation across departments before training.
    - Outcome: The model’s predictions are less biased toward historically favored departments.
    """,
        "In-Processing": """
    - Rebalances weights during training to reduce demographic disparity.
    - Goal: The model sees a “fairer” distribution of examples and reduces bias from historical data.
    - Outcome: The model’s predictions adjust to give more equitable selection rates.
    """,
        "Post-Processing": """
    - Adjusts department-specific thresholds to equalize selection rates.
    - Goal: Corrects biased outputs without retraining the model.
    - Outcome: Departments with lower historical selection rates receive a boost to achieve fairer outcomes.
    """
    }

    st.markdown(f"**How {mitigation} works:**")
    st.markdown(mitigation_descriptions[mitigation])

    # ----------------------------
    # Metrics: Before and After
    # ----------------------------

    # Compute metrics before mitigation (once)
    if "metrics_before" not in st.session_state:
        st.session_state.metrics_before = metrics_table(data, "Before Mitigation")

    # Compute metrics after mitigation
    st.session_state.metrics_after = metrics_table(df_mitigated, "After Mitigation")

    # Merge for display
    metrics_comparison = st.session_state.metrics_before.merge(
        st.session_state.metrics_after,
        on="Metric",
        how="inner",
        suffixes=("_Before", "_After")
    )

    # Display side-by-side
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Fairness Metrics Table")
        st.dataframe(metrics_comparison, use_container_width=True)

    with col2:
        st.subheader("Understanding the Metrics")
        interpretation_text = ""
        for _, row in metrics_comparison.iterrows():
            interpretation_text += f"- **{row['Metric']}**: Before = {row['_Before']}, After = {row['_After']}\n"
        st.markdown(interpretation_text)

    # ----------------------------
    # Department Selection Rates Comparison
    # ----------------------------
    st.subheader("Department Selection Rates Comparison")
    st.plotly_chart(plot_department_comparison(data, df_mitigated), use_container_width=True)

    st.info("""
💡 After mitigation:  
- Departments with previously low selection rates are boosted. 
- Selection rates across departments are more balanced.  
- Overall model accuracy remains reasonable while fairness improves.
""")

    # ----------------------------
    # Toggle to show mitigated dataset
    # ----------------------------
    show_results = st.toggle("Show Mitigated Dataset")
    if show_results:
        st.subheader("Dataset After Mitigation")
        st.dataframe(df_mitigated, use_container_width=True)

    # ----------------------------
    # Audit log
    # ----------------------------
    st.divider()
    if "audit_log" not in st.session_state:
        st.session_state.audit_log = pd.DataFrame(columns=[
            "Timestamp", "User Input", "Agent Output", "Tools Used",
            "Memory Used (MB)", "Flags Triggered", "Policy Violation"
        ])

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.audit_log = pd.concat([
        st.session_state.audit_log,
        pd.DataFrame([{
            "Timestamp": timestamp,
            "User Input": "dataset",
            "Agent Output": "adjusted dataset",
            "Tools Used": mitigation,
            "Memory Used (MB)": round(psutil.Process().memory_info().rss / (1024*1024),2),
            "Flags Triggered": "None",
            "Policy Violation": "Department Fairness"
        }])
    ], ignore_index=True)

    csv = st.session_state.audit_log.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Audit Log", data=csv, file_name="audit_log.csv", mime="text/csv")

    if st.button("⬅️ Go Back to Home"):
        st.query_params["page"] = "home"
        st.rerun()


  
   
# # 1. Pre-Processing Equalization
# # ----------------------------
# def pre_processing_equalize(df_train, df_test):
#     dept_metrics = compute_department_metrics(df_train)
#     max_rate = dept_metrics["Selection Rate"].max()

#     df_balanced = df_train.copy()
#     for _, row in dept_metrics.iterrows():
#         dept = row["Department"]
#         rate = row["Selection Rate"]
#         if rate < max_rate:
#             reps = int((max_rate - rate) * len(df_train[df_train["Department"] == dept]) * 3)
#             if reps > 0:
#                 sampled = df_train[df_train["Department"] == dept].sample(reps, replace=True, random_state=42)
#                 df_balanced = pd.concat([df_balanced, sampled], ignore_index=True)

#     X_bal = pd.get_dummies(df_balanced[["Experience", "Skills_Score", "Department"]], drop_first=True)
#     y_bal = df_balanced["Shortlisted"]

#     model = LogisticRegression()
#     model.fit(X_bal, y_bal)

#     df_result = df_test.copy()
#     X_test = pd.get_dummies(df_result[["Experience", "Skills_Score", "Department"]], drop_first=True)
#     X_test = X_test.reindex(columns=X_bal.columns, fill_value=0)
#     df_result["Shortlisted"] = model.predict(X_test)

#     # Slight random flips to create divergence
#     mask = np.random.rand(len(df_result)) < 0.05  # flip 5% randomly
#     df_result.loc[mask, "Shortlisted"] = 1 - df_result.loc[mask, "Shortlisted"]

#     return model, df_result


# # ----------------------------
# # 2. In-Processing Equalization
# # ----------------------------
# def in_processing_equalize(df_train, df_test):
#     dept_metrics = compute_department_metrics(df_train)
#     max_rate = dept_metrics["Selection Rate"].max()

#     # Assign weights inversely proportional to department selection rate
#     weights = df_train["Department"].map(
#         lambda d: 1 + (max_rate - dept_metrics.loc[dept_metrics["Department"] == d, "Selection Rate"].values[0]) * 10
#     )

#     X_train = pd.get_dummies(df_train[["Experience", "Skills_Score", "Department"]], drop_first=True)
#     y_train = df_train["Shortlisted"]

#     model = LogisticRegression()
#     model.fit(X_train, y_train, sample_weight=weights)

#     df_result = df_test.copy()
#     X_test = pd.get_dummies(df_result[["Experience", "Skills_Score", "Department"]], drop_first=True)
#     X_test = X_test.reindex(columns=X_train.columns, fill_value=0)
#     df_result["Shortlisted"] = model.predict(X_test)

#     # Random flips based on department weights for divergence
#     for dept in df_result["Department"].unique():
#         mask = df_result["Department"] == dept
#         flip_idx = df_result[mask].sample(frac=0.1, random_state=42).index  # flip 10%
#         df_result.loc[flip_idx, "Shortlisted"] = 1 - df_result.loc[flip_idx, "Shortlisted"]

#     return model, df_result


# # ----------------------------
# # 3. Post-Processing Equalization
# # ----------------------------
# def post_processing_equalize(df_train, df_test):
#     X_train = pd.get_dummies(df_train[["Experience", "Skills_Score", "Department"]], drop_first=True)
#     y_train = df_train["Shortlisted"]

#     model = LogisticRegression()
#     model.fit(X_train, y_train)

#     X_test = pd.get_dummies(df_test[["Experience", "Skills_Score", "Department"]], drop_first=True)
#     X_test = X_test.reindex(columns=X_train.columns, fill_value=0)
#     probs = model.predict_proba(X_test)[:, 1]

#     df_result = df_test.copy()
#     df_result["Probability"] = probs

#     dept_metrics = compute_department_metrics(df_train)
#     max_rate = dept_metrics["Selection Rate"].max()

#     df_result["Shortlisted"] = 0
#     for dept in df_result["Department"].unique():
#         dept_subset = df_result[df_result["Department"] == dept]
#         target_n = max(1, int(max_rate * len(dept_subset)))
#         # Use probabilities to randomly select top candidates with tie-breaking
#         top_idx = dept_subset.sample(n=target_n, weights=dept_subset["Probability"], random_state=42).index
#         df_result.loc[top_idx, "Shortlisted"] = 1

#     df_result.drop(columns=["Probability"], inplace=True)
#     return model, df_result



def app():
    # ----------------------------
    # Default Dataset
    # ----------------------------
    default_data = pd.DataFrame({
        "Name": ["John Smith", "Michael Johnson", "David Brown", "Robert Wilson", "James Davis",
                "Sarah Williams", "Emily Jones", "Jessica Miller", "Ashley Garcia", "Amanda Rodriguez"],
        "Department": ["Engineering", "Engineering", "Sales", "Sales", "HR",
                    "HR", "Engineering", "Sales", "HR", "Engineering"],
        "Experience": [8, 6, 9, 5, 7, 6, 8, 5, 7, 4],
        "Skills_Score": [85, 78, 92, 76, 88, 82, 89, 75, 86, 73],
        "Shortlisted": [1, 1, 1, 1, 1, 0, 1, 0, 0, 0]
    })

    # After imports
    np.random.seed(42)
    departments = ["Engineering", "Sales", "HR"]
    large_data = pd.DataFrame({
        "Name": [f"Candidate {i}" for i in range(100)],
        "Department": np.random.choice(departments, 100),
        "Experience": np.random.randint(3, 10, 100),
        "Skills_Score": np.random.randint(70, 95, 100),
    })

    large_data["Shortlisted"] = 0
   # Example: add noise to Shortlisted
    for dept in departments:
        mask = large_data["Department"] == dept
        base_rate = {"Engineering": 0.75, "Sales": 0.6, "HR": 0.4}[dept]
        large_data.loc[mask, "Shortlisted"] = (np.random.rand(mask.sum()) < base_rate).astype(int)

    required_columns = ["Name", "Department", "Experience", "Skills_Score", "Shortlisted"]

    st.set_page_config(page_title="Department Fairness Simulator", layout="wide")
    st.title("Fairness Simulator")

    # ----------------------------
    # Fairness Introduction
    # ----------------------------
    st.markdown("""
    **Fairness in AI** ensures that automated decisions do not systematically disadvantage specific groups. 
    In hiring, for example, some departments or demographic groups may be underrepresented in selections. Fairness is important because:
    - Unfair models perpetuate historical inequalities.
    - Biased outcomes reduce trust in AI systems.
    - Organizations face legal and reputational risks if decisions are discriminatory.
    """)

    # ----------------------------
    # Regulatory Frameworks
    # ----------------------------
    st.header("Regulatory Frameworks for Fairness")
    with st.expander("Show Details"):
        st.markdown("This section summarizes key EU and US regulatory frameworks that govern fairness, transparency, and non-discrimination in AI and data practices.")
        st.subheader("🇺🇸 US")
        st.markdown("""
        - **Equal Credit Opportunity Act (ECOA):** Prevents discrimination in lending decisions.  
        - **Title VII of the Civil Rights Act:** Prohibits employment discrimination.  
        - **Fair Housing Act:** Prohibits housing discrimination.  
        """)
        st.subheader("🇪🇺 EU")
        st.markdown("""
        - **GDPR:** Requires fairness, transparency, and accountability in data processing.  
        - **EU Artificial Intelligence Act (AI Act):** Addresses biases in AI systems and ensures non-discriminatory decision-making.
        """)

    

    # ----------------------------
    # How It Works
    # ----------------------------
    
    st.header("How It Works")
    with st.expander("Show Details"):
        st.subheader("Scenario")
        st.markdown("In this scenario, a company is trying to hire candidates across multiple departments: Engineering, Sales, and HR. They want to ensure that selections are fair and no department is systematically disadvantaged.")
        st.subheader("Sample Dataset")
        data = default_data.copy()
        st.dataframe(data, use_container_width=True)


        col1, col2 = st.columns(2)
        with col1:
            metrics_df = metrics_table(data, "Before Mitigation")
            st.subheader("Baseline Fairness Metrics")
            st.dataframe(metrics_df.iloc[:, [0, 1]], use_container_width=True)
        with col2:
            st.subheader("Interpreting the Graph")
            st.markdown("""
            - **Engineering Selection Rate (0.75)**: 75% of Engineering candidates are shortlisted. This suggests that Engineering candidates are favored, either historically or by the model.
            - **HR Selection Rate (0.33)**: Only 33% of HR candidates are shortlisted. This is the lowest rate, indicating HR candidates are at a disadvantage relative to Engineering and Sales.
            - **Sales Selection Rate (0.67)**: 67% of Sales candidates are shortlisted, which is intermediate, slightly lower than Engineering but higher than HR.
            """)

        st.warning("**Interpretation**:From a fairness perspective, HR candidates are systematically under-selected, Engineering candidates are favored, and Sales are in between.")

        # ----------------------------
        # Dataset Upload
        # ----------------------------
        st.subheader("Upload Your Dataset")
        st.info(f"**Disclaimer:** Your dataset should contain the following columns: {', '.join(required_columns)}")
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

        if uploaded_file is not None:
            try:
                user_df = pd.read_csv(uploaded_file)
                missing_cols = [col for col in required_columns if col not in user_df.columns]
                if missing_cols:
                    st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                    data = default_data.copy()
                    st.info("Using default dataset due to missing columns.")
                else:
                    st.success("✅ Dataset contains all required columns!")
                    data = user_df.copy()
            except Exception as e:
                st.error(f"Error reading the file: {e}")
                data = default_data.copy()
        else:
            data = default_data.copy()

    st.subheader("Mitigation Approach")
    with st.expander("Show Details"):
        model, _ = train_model(data)

        # ----------------------------
        # Mitigation Selection
        # ----------------------------
        mitigation = st.selectbox(
        "Various techniques can help reduce fairness in AI systems. Select one below to see its impact on fairness metrics:",
            ["Pre-Processing", "In-Processing", "Post-Processing"]
        )

        if mitigation=="Pre-Processing":
            _, df_mitigated = pre_processing_equalize(default_data, default_data)
            metrics_df["Pre-Processing"] = metrics_table(df_mitigated, "Pre-processing")["Pre-processing"]
            mitigation_desc = """
            How Pre-Processing works:
            - Oversamples underrepresented departments to match the selection rates of the most represented department.
            - Goal: The dataset itself is balanced so that the model sees equal representation across departments before training.
            - Outcome: The model’s predictions are less biased toward historically favored departments.
            """
        elif mitigation=="In-Processing":
            _, df_mitigated = in_processing_equalize(default_data, default_data)
            metrics_df["In-Processing"] = metrics_table(df_mitigated, "In-processing")["In-processing"]
            mitigation_desc = """
            How In-Processing works:
            - Rebalances weights during training to reduce demographic disparity.
            - Goal: The model sees a “fairer” distribution of examples and reduces bias from historical data.
            - Outcome: The model’s predictions adjust to give more equitable selection rates.
            """
        else:
            _, df_mitigated = post_processing_equalize(default_data, default_data)
            metrics_df["Post-Processing"] = metrics_table(df_mitigated, "Post-processing")["Post-processing"]
            mitigation_desc = """
            How Post-Processing works:
            - Adjusts department-specific thresholds to equalize selection rates.
            - Goal: Corrects biased outputs without retraining the model.
            - Outcome: Departments with lower historical selection rates receive a boost to achieve fairer outcomes.
            """
    
        st.info(mitigation_desc)

        # ----------------------------
        # Metrics and Interpretations After Mitigation
        # ----------------------------

        # Compute metrics before and after mitigation
        metrics_df_before = metrics_table(data, "Before Mitigation")

        # Merge on "Metric"
        metrics_comparison = metrics_df_before.merge(
            metrics_df,
            on="Metric",
            how="outer"
        )

        # Rename the value columns
        metrics_comparison = metrics_comparison.rename(columns={
            "Before Mitigation": "Before Mitigation",
        })

        print("METRICS DF", metrics_df.columns)
        interpretation_text = "\n".join([
            f"- **{row['Metric']} ({row[mitigation]}):** {row['Interpretation']}\n" 
            for _, row in metrics_df.iterrows()
        ])
        
        metrics_comparison = metrics_comparison.rename(columns={"Before Mitigation_x": "Before Mitigation"})
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Fairness Metrics ({mitigation})")
            st.dataframe(metrics_comparison.iloc[:, [0, 1, 5]], use_container_width=True)
        with col2:
            st.subheader("Understanding the Metrics")
            st.markdown(interpretation_text)


        #st.subheader("Department Selection Rates Comparison")
        st.plotly_chart(plot_department_comparison(data, df_mitigated), use_container_width=True)
        st.warning("""
    **Note:** After applying the mitigations, you will notice:  
    - Departments with previously low selection rates are boosted. 
    - Selection rates across departments are more balanced.  
    - Overall model accuracy remains reasonable while fairness improves.
    """)

        # ----------------------------
        # Toggle to show mitigated dataset
        # ----------------------------
        show_results = st.toggle("Show Mitigated Dataset")
        if show_results:
            st.subheader("Dataset After Mitigation")
            st.dataframe(df_mitigated, use_container_width=True)
            st.subheader("Fairness After Mitigation")
            st.dataframe(metrics_comparison.iloc[:, [0, 5]], use_container_width=True)

    # ----------------------------
    # Audit log
    # ----------------------------
    st.divider()
    if "audit_log" not in st.session_state:
        st.session_state.audit_log = pd.DataFrame(columns=[
            "Timestamp", "User Input", "Agent Output", "Tools Used",
            "Memory Used (MB)", "Flags Triggered", "Policy Violation"
        ])

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.audit_log = pd.concat([
        st.session_state.audit_log,
        pd.DataFrame([{
            "Timestamp": timestamp,
            "User Input": "dataset",
            "Agent Output": "Mitigated prompt",
            "Tools Used": mitigation,
            "Memory Used (MB)": round(psutil.Process().memory_info().rss / (1024*1024),2),
            "Flags Triggered": "None",
            "Policy Violation": "Fairness"
        }])
    ], ignore_index=True)

    csv = st.session_state.audit_log.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Audit Log", data=csv, file_name="audit_log.csv", mime="text/csv")

    if st.button("⬅️ Go Back to Home"):
        st.query_params["page"] = "home"
        st.rerun()


  
   