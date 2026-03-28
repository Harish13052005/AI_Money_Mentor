import streamlit as st
import requests
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI Money Mentor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("💰 AI Money Mentor")
st.markdown("*Your Intelligent Financial Planning Assistant*")
st.divider()

# Sidebar
with st.sidebar:
    st.header("📋 Navigation")
    page = st.radio("Choose a section:", ["Financial Analysis", "Ask for Explanation", "About"])

if page == "Financial Analysis":
    st.header("📊 Enter Your Financial Data")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        income = st.number_input("💵 Monthly Income (USD)", min_value=0.0, value=5000.0)
    with col2:
        expenses = st.number_input("💸 Monthly Expenses (USD)", min_value=0.0, value=3000.0)
    with col3:
        savings = st.number_input("🏦 Current Savings (USD)", min_value=0.0, value=1000.0)
    
    st.divider()
    st.subheader("📈 Investments")
    
    num_inv = st.number_input("Number of Investments", min_value=0, max_value=10, value=1)
    investments = []
    
    if num_inv > 0:
        for i in range(int(num_inv)):
            col1, col2 = st.columns(2)
            with col1:
                inv_type = st.text_input(f"Investment {i+1} Type (e.g., stocks, bonds)", key=f"type_{i}", value="stocks" if i == 0 else "")
            with col2:
                inv_amount = st.number_input(f"Investment {i+1} Amount (USD)", min_value=0.0, key=f"amount_{i}", value=2000.0 if i == 0 else 0.0)
            if inv_type and inv_amount > 0:
                investments.append({"type": inv_type, "amount": inv_amount})
    
    st.divider()
    st.subheader("🎯 Financial Goals")
    goals_text = st.text_area(
        "Enter your financial goals (comma separated)",
        value="Early retirement, Buy a house, Save for education",
        help="Example: Early retirement, Buy a house, Save for education"
    )
    goals = [g.strip() for g in goals_text.split(',') if g.strip()]
    
    st.divider()
    
    # Display summary before analysis
    st.subheader("📋 Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Monthly Income", f"${income:,.2f}")
    with col2:
        st.metric("Monthly Expenses", f"${expenses:,.2f}")
    with col3:
        monthly_savings = income - expenses
        st.metric("Monthly Savings", f"${monthly_savings:,.2f}", delta="+" if monthly_savings > 0 else "-")
    
    # Analyze button
    if st.button("🚀 Generate Financial Plan", use_container_width=True, type="primary"):
        if not goals:
            st.error("❌ Please enter at least one financial goal.")
        elif income <= 0:
            st.error("❌ Please enter a valid income.")
        else:
            with st.spinner("🔄 Analyzing your financial situation..."):
                data = {
                    "income": income,
                    "expenses": expenses,
                    "savings": savings,
                    "investments": investments if investments else [{"type": "none", "amount": 0}],
                    "goals": goals
                }
                try:
                    response = requests.post("http://localhost:8000/analyze", json=data, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Analysis Complete!")
                        
                        # Display results in tabs
                        tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Issues", "Plan", "Actions"])
                        
                        with tab1:
                            st.subheader("📊 Analysis Summary")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Savings Rate", f"{result['summary'].split('Savings rate: ')[1].split('%')[0]}%")
                            with col2:
                                risk = result['risk_level']
                                st.metric("Risk Level", risk, delta=risk.lower())
                        
                        with tab2:
                            st.subheader("⚠️ Detected Issues")
                            if result['issues']:
                                for i, issue in enumerate(result['issues'], 1):
                                    st.warning(f"• {issue}")
                            else:
                                st.success("✅ No issues detected!")
                        
                        with tab3:
                            st.subheader("📈 Financial Plan")
                            st.write(result['financial_plan'])
                        
                        with tab4:
                            st.subheader("✅ Recommended Actions")
                            for i, action in enumerate(result['recommended_actions'], 1):
                                st.info(f"**Step {i}:** {action}")
                    else:
                        error_msg = response.json().get('detail', response.text)
                        st.error(f"❌ Error: {error_msg}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend server. Please ensure the FastAPI server is running on http://localhost:8000")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

elif page == "Ask for Explanation":
    st.header("❓ Ask for Explanation")
    st.markdown("Ask questions about your financial plan and analysis.")
    st.divider()
    
    question = st.text_area(
        "Your Question",
        placeholder="e.g., Based on my current monthly surplus of $2,000, should I prioritize increasing my Index Fund contribution?",
        height=150
    )
    
    if st.button("💡 Get Explanation", use_container_width=True, type="primary"):
        if not question or question.strip() == "":
            st.error("❌ Please enter a question.")
        else:
            with st.spinner("🤔 Generating explanation..."):
                try:
                    # Send question as query parameters
                    params = {"question": question, "context": ""}
                    response = requests.post("http://localhost:8000/explain", params=params, timeout=30)
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Explanation Generated!")
                        st.info(result["explanation"])
                    else:
                        error_msg = response.json().get('detail', response.text)
                        st.error(f"❌ Error: {error_msg}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend server. Please ensure the FastAPI server is running.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

else:  # About page
    st.header("ℹ️ About AI Money Mentor")
    st.markdown("""
    ### What is AI Money Mentor?
    
    AI Money Mentor is an intelligent financial planning system powered by advanced AI agents. 
    It analyzes your financial situation and provides personalized recommendations.
    
    ### Key Features
    
    - **Multi-Agent Analysis**: Uses specialized AI agents for different aspects of financial planning
    - **Financial Insights**: Detects savings issues, investment risks, and inefficiencies
    - **Personalized Plans**: Generates customized financial strategies based on your goals
    - **Explainable AI**: Get detailed explanations for every recommendation
    - **Risk Assessment**: Evaluates your investment portfolio risk level
    
    ### How It Works
    
    1. **Data Intake**: Your financial information is validated and processed
    2. **Analysis**: Our agents analyze your data for issues and opportunities
    3. **Strategy**: AI generates a personalized financial plan
    4. **Compliance**: Plans are checked for safety and realism
    5. **Recommendations**: Actionable steps are provided
    6. **Explanation**: You can ask follow-up questions anytime
    
    ### Getting Started
    
    1. Go to the "Financial Analysis" tab
    2. Enter your financial data
    3. Click "Generate Financial Plan"
    4. Review the analysis and recommendations
    5. Ask questions in the "Ask for Explanation" tab
    
    **Note**: Set your OpenAI API key in the `.env` file for the system to work properly.
    """)
    st.divider()
    st.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")