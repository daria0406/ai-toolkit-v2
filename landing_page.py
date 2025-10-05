import streamlit as st
import bias_mitigation
import fairness
import goal_hijacking
import prompt_injection
import hallucination

st.set_page_config(page_title="AI Risk Simulator", layout="wide")

# Only show cards on the landing page
query_params = st.query_params
selected_page = query_params.get("page", "home")

if selected_page == "home":
    st.title("AI Safety Toolkit Demo")
    st.write("Explore AI risks and mitigation strategies below:")
    # Add custom CSS for clickable cards
    st.markdown("""
    <style>
        .card-container {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }
        .card {
            flex: 1 1 250px;
            background: #f9f9f9;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.08);
            text-align: center;
            transition: 0.3s;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
        }
        .card:hover {
            background: #f0f4ff;
            transform: translateY(-5px);
            box-shadow: 0 6px 14px rgba(0,0,0,0.12);
        }
        .emoji {
            font-size: 32px;
            margin-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card-container">
        <a class="card" href="?page=bias">
            <div class="emoji">⚖️</div>
            <h3>Bias</h3>
            <p>Explore how to mitigate bias</p>
        </a>
        <a class="card" href="?page=fairness">
            <div class="emoji">🫱🏽‍🫲🏼</div>
            <h3>Fairness</h3>
            <p>Explore how algorithms may discriminate</p>
        </a>
        <a class="card" href="?page=prompt">
            <div class="emoji">💉</div>
            <h3>Prompt Injection</h3>
            <p>See how attackers manipulate model inputs and test defenses</p>
        </a>
       
    </div>
    """, unsafe_allow_html=True)
elif selected_page == "bias":
    bias_mitigation.app()
elif selected_page == "fairness":
    fairness.app()
elif selected_page == "prompt":
    prompt_injection.app()
# elif selected_page == "goal":
#     goal_hijacking.app()
# elif selected_page == "hallucination":
#     hallucination.app()
else:
    st.error("Page not found. Please select a valid option from the home page.")

 # <a class="card" href="?page=goal">
        #     <div class="emoji">🎯</div>
        #     <h3>Goal Hijacking</h3>
        #     <p>Investigate how models can drift from intended goals</p>
        # </a>
        # <a class="card" href="?page=hallucination">
        #     <div class="emoji">📝</div>
        #     <h3>Hallucination</h3>
        #     <p>Analyze how LLMs fabricate facts and how to detect them</p>
        # </a>