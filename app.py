import streamlit as st

# --- IMPORT OUR MODULAR ECOSYSTEM ---
import sidebar
import scraper
import tool
import ui_components
import agent_runner

# 1. PAGE CONFIGURATION (Must be the very first Streamlit command)
st.set_page_config(
    page_title="AI Git Scout | Transparent Auditor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. INJECT UI THEME
ui_components.apply_custom_css()

# 3. INITIALIZE APP-LEVEL SESSION STATE
if "raw_git_data" not in st.session_state:
    st.session_state.raw_git_data = None
if "target_user" not in st.session_state:
    st.session_state.target_user = ""
if "audit_report" not in st.session_state:
    st.session_state.audit_report = None

# 4. RENDER SIDEBAR & CAPTURE THE 20 CALIBRATION CONSTANTS
engine_config = sidebar.render_sidebar()

# 5. RENDER MAIN HEADER
st.title("🚀 AI GitHub Profile Scout")
st.markdown("A transparent, mathematically-grounded auditing tool for developer portfolios.")
st.markdown("---")

# 6. INPUT CAPTURE
col_input, col_btn = st.columns([4, 1])
with col_input:
    target_input = st.text_input("Enter GitHub Profile URL or Username:", value=st.session_state.target_user)
with col_btn:
    st.write("") # Spacing
    st.write("")
    run_audit = st.button("Fetch GitHub Telemetry", type="primary", use_container_width=True)

# 7. EXECUTE DATA PIPELINE
if run_audit:
    if target_input.strip():
        st.session_state.target_user = target_input.strip()
        # Clear the old AI report when searching a new user
        st.session_state.audit_report = None 
        
        with st.spinner("Scraping telemetry from GitHub..."):
            st.session_state.raw_git_data = scraper.run_scraper(st.session_state.target_user)
    else:
        st.warning("Please enter a valid username.")

# 8. RENDER THE DASHBOARD
if st.session_state.raw_git_data:
    raw_data = st.session_state.raw_git_data
    
    if "error" in raw_data:
        st.error(f"🚨 Failed to fetch data: {raw_data['error']}")
    else:
        # Step A: Compile the Math based on UI sliders
        compiled_context = tool.compile_payload_from_memory(raw_data, engine_config)
        
        metrics = compiled_context["hard_metrics"]
        username = compiled_context["user_target"]

        # Step B: Render Visuals (Updates instantly when sliders move)
        ui_components.render_kpi_dashboard(metrics, username)
        ui_components.render_math_explainers(metrics["breakdowns"], metrics["category_scores"])

        # Step C: The AI Engine Execution Gate
        st.markdown("---")
        st.subheader("🤖 Career Architecture Agent")
        st.markdown(f"The Agent will analyze this math using the **{engine_config['persona']}** mindset.")
        
        # If we haven't generated a report yet, show the button
        if not st.session_state.audit_report:
            if st.button("✨ Generate AI Narrative Audit", type="primary"):
                with st.spinner("Analyzing math and deducing career roadmap..."):
                    st.session_state.audit_report = agent_runner.run_ai_auditor(compiled_context)
                    st.rerun() # Refresh the page to show the report
        
        # If the report exists, display it via the Markdown viewer
        if st.session_state.audit_report:
            ui_components.render_markdown_viewer(st.session_state.audit_report, username)
            
            # Allow the user to regenerate the report if they changed sliders
            if st.button("🔄 Regenerate AI Audit (Apply New Sliders)"):
                with st.spinner("Re-analyzing with updated metrics..."):
                    st.session_state.audit_report = agent_runner.run_ai_auditor(compiled_context)
                    st.rerun()