import streamlit as st
from langgraph.graph import StateGraph, START, END

# Import custom modules
import scraper
import tool
import main
from main import AgentState, profiling_node

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AI Git Scout",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- TARGETED CSS FOR METRIC VISIBILITY ---
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); 
    }
    
    /* Strictly target text INSIDE the metrics components for contrast */
    div[data-testid="stMetricValue"] > div {
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    label[data-testid="stMetricLabel"] > div > p {
        color: #475569 !important;
        font-weight: 500 !important;
    }
    
    h1 { color: #1E293B; }
    h2 { color: #334155; border-bottom: 2px solid #E2E8F0; padding-bottom: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- CACHED SCRAPER FUNCTION ---
# This prevents GitHub from ratelimiting you if the same user is searched multiple times.
@st.cache_data(show_spinner=False, ttl=3600)
def fetch_github_data(target_url):
    return scraper.run_scraper(target_url)

# --- APP HEADER ---
st.title("🚀 AI GitHub Profile Scout")
st.markdown("Evaluating genuine student builders based on consistency, collaboration, and code velocity.")
st.markdown("---")

# --- USER INPUT AREA ---
target_input = st.text_input(
    "Enter GitHub Profile URL or Username:", 
    placeholder="https://github.com/akshat-gupta-111"
)

if st.button("Run Profile Audit", type="primary"):
    if not target_input.strip():
        st.warning("Please enter a valid username or URL first.")
    else:
        # Step 1: Scrape In-Memory (Cached)
        with st.spinner(f"Extracting GitHub telemetry for {target_input}... This takes ~30 seconds."):
            raw_git_data = fetch_github_data(target_input)
            
        if "error" in raw_git_data:
            st.error(f"🚨 Failed to fetch data: {raw_git_data['error']}")
        else:
            # Step 2: Compile Math and Context
            username = raw_git_data.get('profile', {}).get('username', 'Developer')
            compiled_context = tool.compile_payload_from_memory(raw_git_data, "weights.csv")
            
            metrics = compiled_context["hard_metrics"]
            final_score = metrics["final_score"]
            breakdown = metrics["breakdown"]

            # Step 3: Render Visual KPIs
            st.subheader(f"📊 Telemetry Metrics Breakdown for {username}")
            
            col_main, col_spacer = st.columns([1, 3])
            with col_main:
                st.metric(label="🏆 Final Agent Score", value=f"{final_score} / 100")
            
            st.write(" ")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Consistency", f"{breakdown['consistency']}%")
                st.progress(breakdown['consistency'] / 100.0)
            with col2:
                st.metric("Community/Collab", f"{breakdown['community']}%")
                st.progress(breakdown['community'] / 100.0)
            with col3:
                st.metric("Tech Stack Depth", f"{breakdown['technology']}%")
                st.progress(breakdown['technology'] / 100.0)
            with col4:
                st.metric("Management/Docs", f"{breakdown['management']}%")
                st.progress(breakdown['management'] / 100.0)
            with col5:
                st.metric("Advanced Contributions", f"{breakdown['advanced']}%")
                st.progress(breakdown['advanced'] / 100.0)

            st.markdown("---")

            # Step 4: Run Agent Brain
            with st.spinner("Agent is analyzing career trajectory..."):
                workflow = StateGraph(AgentState)
                workflow.add_node("profiler", profiling_node)
                workflow.add_edge(START, "profiler")
                workflow.add_edge("profiler", END)
                agent_pipeline = workflow.compile()

                initial_state = {"messages": [], "compiled_context": compiled_context}
                output_state = agent_pipeline.invoke(initial_state)
                agent_feedback = output_state["messages"][-1].content

            # Step 5: Render LLM Output
            st.subheader("🤖 Agent Career Architecture Report")
            st.markdown(agent_feedback)