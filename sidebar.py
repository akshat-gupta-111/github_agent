import streamlit as st

# --- PRESET EVALUATION PERSONAS ---
# These dictionaries now hold all 20 constants and weights for total architectural control.
PERSONAS = {
    "Default (Balanced Assessor)": {
        "weights": {"consistency": 20, "community": 30, "technology": 25, "management": 15, "advanced": 10},
        "constants": {
            "epsilon": 1.0, 
            "alpha": 5.0, "beta": 3.0, "breadth_ceiling": 8.0, 
            "gamma": 10.0, "adv_target": 3,
            "sweet_spot_low": 0.15, "sweet_spot_high": 0.85, "points_per_collab": 20.0, 
            "partial_credit": 0.2, "star_bonus": 2.0, "fork_bonus": 5.0,
            "target_ratio": 0.75, "bio_bonus": 10.0, "name_bonus": 5.0
        }
    },
    "The Enterprise Recruiter": {
        "weights": {"consistency": 30, "community": 20, "technology": 20, "management": 20, "advanced": 10},
        "constants": {
            "epsilon": 0.5, 
            "alpha": 4.0, "beta": 4.0, "breadth_ceiling": 5.0, 
            "gamma": 15.0, "adv_target": 5,
            "sweet_spot_low": 0.25, "sweet_spot_high": 0.75, "points_per_collab": 25.0, 
            "partial_credit": 0.0, "star_bonus": 1.0, "fork_bonus": 2.0,
            "target_ratio": 0.90, "bio_bonus": 5.0, "name_bonus": 0.0
        }
    },
    "The Hackathon Judge": {
        "weights": {"consistency": 5, "community": 35, "technology": 40, "management": 10, "advanced": 10},
        "constants": {
            "epsilon": 3.0, 
            "alpha": 7.0, "beta": 2.0, "breadth_ceiling": 12.0, 
            "gamma": 5.0, "adv_target": 2,
            "sweet_spot_low": 0.05, "sweet_spot_high": 0.95, "points_per_collab": 50.0, 
            "partial_credit": 0.5, "star_bonus": 5.0, "fork_bonus": 10.0,
            "target_ratio": 0.50, "bio_bonus": 15.0, "name_bonus": 10.0
        }
    }
}

def init_session_state():
    """Initializes all 20 variables in session state to prevent UI reset errors."""
    if "persona" not in st.session_state: st.session_state.persona = "Default (Balanced Assessor)"
    
    # 1. Weights (5)
    if "w_cons" not in st.session_state: st.session_state.w_cons = 20
    if "w_comm" not in st.session_state: st.session_state.w_comm = 30
    if "w_tech" not in st.session_state: st.session_state.w_tech = 25
    if "w_mgmt" not in st.session_state: st.session_state.w_mgmt = 15
    if "w_adv" not in st.session_state: st.session_state.w_adv = 10

    # 2. Consistency Constants (1)
    if "epsilon" not in st.session_state: st.session_state.epsilon = 1.0
    
    # 3. Technology Constants (3)
    if "alpha" not in st.session_state: st.session_state.alpha = 5.0
    if "beta" not in st.session_state: st.session_state.beta = 3.0
    if "breadth_ceiling" not in st.session_state: st.session_state.breadth_ceiling = 8.0

    # 4. Advanced Constants (2)
    if "gamma" not in st.session_state: st.session_state.gamma = 10.0
    if "adv_target" not in st.session_state: st.session_state.adv_target = 3

    # 5. Community Constants (6)
    if "sweet_spot_low" not in st.session_state: st.session_state.sweet_spot_low = 0.15
    if "sweet_spot_high" not in st.session_state: st.session_state.sweet_spot_high = 0.85
    if "points_per_collab" not in st.session_state: st.session_state.points_per_collab = 20.0
    if "partial_credit" not in st.session_state: st.session_state.partial_credit = 0.2
    if "star_bonus" not in st.session_state: st.session_state.star_bonus = 2.0
    if "fork_bonus" not in st.session_state: st.session_state.fork_bonus = 5.0

    # 6. Management Constants (3)
    if "target_ratio" not in st.session_state: st.session_state.target_ratio = 0.75
    if "bio_bonus" not in st.session_state: st.session_state.bio_bonus = 10.0
    if "name_bonus" not in st.session_state: st.session_state.name_bonus = 5.0

def apply_persona_defaults():
    """Auto-snaps all 20 sliders to the designated Sweet Spots when a persona is selected."""
    selected = st.session_state.persona
    p = PERSONAS[selected]
    
    st.session_state.update({
        "w_cons": p["weights"]["consistency"], "w_comm": p["weights"]["community"],
        "w_tech": p["weights"]["technology"], "w_mgmt": p["weights"]["management"], "w_adv": p["weights"]["advanced"],
        "epsilon": p["constants"]["epsilon"], "alpha": p["constants"]["alpha"],
        "beta": p["constants"]["beta"], "breadth_ceiling": p["constants"]["breadth_ceiling"],
        "gamma": p["constants"]["gamma"], "adv_target": p["constants"]["adv_target"],
        "sweet_spot_low": p["constants"]["sweet_spot_low"], "sweet_spot_high": p["constants"]["sweet_spot_high"],
        "points_per_collab": p["constants"]["points_per_collab"], "partial_credit": p["constants"]["partial_credit"],
        "star_bonus": p["constants"]["star_bonus"], "fork_bonus": p["constants"]["fork_bonus"],
        "target_ratio": p["constants"]["target_ratio"], "bio_bonus": p["constants"]["bio_bonus"],
        "name_bonus": p["constants"]["name_bonus"]
    })

def render_sidebar():
    """Renders the transparent sidebar UI and returns the compiled engine configuration."""
    init_session_state()
    
    with st.sidebar:
        st.header("⚙️ Engine Calibration")
        st.markdown("Absolute control over the mathematical grading logic.")
        
        st.selectbox("Evaluation Persona", options=list(PERSONAS.keys()), key="persona", on_change=apply_persona_defaults)
        
        # --- 1. OVERALL CATEGORY WEIGHTS (5 Sliders) ---
        with st.expander("⚖️ Final Category Weights", expanded=False):
            st.markdown("<small>Increase to make a category dominate the final score. Decrease to reduce its impact.</small>", unsafe_allow_html=True)
            w_cons = st.slider("Consistency", 0, 100, key="w_cons", help="Increase to heavily reward daily coding discipline. Decrease to focus purely on output quality regardless of timeline.")
            w_comm = st.slider("Community", 0, 100, key="w_comm", help="Increase to favor developers who collaborate with others. Decrease to favor lone-wolf builders.")
            w_tech = st.slider("Tech Stack Depth", 0, 100, key="w_tech", help="Increase to reward developers who know many tools. Decrease to ignore language diversity.")
            w_mgmt = st.slider("Management", 0, 100, key="w_mgmt", help="Increase to prioritize documentation (READMEs). Decrease to judge purely on code.")
            w_adv = st.slider("Advanced", 0, 100, key="w_adv", help="Increase to demand open-source contributions to famous repositories.")
            
            total_weight = max(w_cons + w_comm + w_tech + w_mgmt + w_adv, 1) # Prevent div by zero
            st.info(f"Total sums to {total_weight}. The engine auto-normalizes these to exactly 100%.")

        # --- 2. CONSISTENCY (1 Slider) ---
        with st.expander("📅 Consistency Limits", expanded=False):
            epsilon = st.slider("Epsilon (ε) [Forgiveness]", 0.1, 5.0, key="epsilon", step=0.1,
                                help="INCREASE to forgive sporadic coding (good for students). DECREASE to ruthlessly demand high monthly commit volumes.")

        # --- 3. COMMUNITY & COLLABORATION (6 Sliders) ---
        with st.expander("🤝 Community & Teamwork", expanded=False):
            sweet_spot_low = st.slider("Team Player Min Ratio", 0.01, 0.50, key="sweet_spot_low", step=0.01,
                                       help="DECREASE to let 'passengers' (low commit %) get full points. INCREASE to demand they write a larger share of the code to be considered a team player.")
            sweet_spot_high = st.slider("Team Player Max Ratio", 0.50, 0.99, key="sweet_spot_high", step=0.01,
                                        help="INCREASE to let solo devs (high commit %) get full team points. DECREASE to punish people who don't share the workload.")
            points_per_collab = st.slider("Points Per Shared Repo", 5.0, 50.0, key="points_per_collab", step=1.0,
                                          help="INCREASE to easily give 100% to anyone with 2 or 3 team projects. DECREASE to demand 5+ team projects for a perfect score.")
            partial_credit = st.slider("Partial Credit Penalty", 0.0, 1.0, key="partial_credit", step=0.1,
                                       help="INCREASE to give 'participation trophies' for barely contributing. DECREASE to strictly award 0 points if they miss the sweet spot.")
            star_bonus = st.slider("Personal Star Bonus", 0.0, 10.0, key="star_bonus", step=0.5,
                                   help="INCREASE to treat stars on personal repos as highly valuable validation. DECREASE to ignore vanity metrics.")
            fork_bonus = st.slider("Personal Fork Bonus", 0.0, 10.0, key="fork_bonus", step=0.5,
                                   help="INCREASE to heavily reward developers whose repos are utilized/cloned by others.")

        # --- 4. TECHNOLOGY STACK (3 Sliders) ---
        with st.expander("🛠️ Technology Stack Depth", expanded=False):
            alpha = st.slider("Alpha (α) [Breadth Value]", 1.0, 10.0, key="alpha", step=0.5,
                              help="INCREASE to heavily reward learning many different languages. DECREASE to de-emphasize tutorial-level exploration.")
            beta = st.slider("Beta (β) [Depth Log Multiplier]", 1.0, 10.0, key="beta", step=0.5,
                             help="INCREASE to heavily reward deep mastery of a few tools. DECREASE to stop rewarding repetitive commits in the same language.")
            breadth_ceiling = st.slider("Breadth Ceiling (Max Languages)", 3.0, 15.0, key="breadth_ceiling", step=1.0,
                                        help="INCREASE to allow points for 10+ languages. DECREASE to cap points early so developers must show depth instead of just making 20 'Hello World' repos.")

        # --- 5. MANAGEMENT & DOCS (3 Sliders) ---
        with st.expander("📝 Management & Docs", expanded=False):
            target_ratio = st.slider("README Target Ratio", 0.1, 1.0, key="target_ratio", step=0.05,
                                     help="DECREASE to let devs with mostly empty repos get a 100% score. INCREASE to demand a README on almost every single repo.")
            bio_bonus = st.slider("GitHub Bio Bonus", 0.0, 20.0, key="bio_bonus", step=1.0,
                                  help="INCREASE to weigh having a bio heavily. DECREASE to judge purely on code documentation.")
            name_bonus = st.slider("Real Name Bonus", 0.0, 20.0, key="name_bonus", step=1.0,
                                   help="INCREASE to reward professional transparency. DECREASE to ignore profile metadata.")

        # --- 6. ADVANCED CONTRIBUTIONS (2 Sliders) ---
        with st.expander("🚀 Advanced Open Source", expanded=False):
            gamma = st.slider("Gamma (γ) [Impact Multiplier]", 1.0, 20.0, key="gamma", step=1.0,
                              help="INCREASE to make every commit to a famous repo worth massive points. DECREASE to force the developer to push many commits to get a high score.")
            adv_target = st.slider("Target Active Repos", 1, 10, key="adv_target", step=1,
                                   help="INCREASE to demand contributions across many different famous repos. DECREASE to let a single famous repo give them a 100% score.")

    # Compile the final configuration object (All 20 variables mapped perfectly)
    engine_config = {
        "persona": st.session_state.persona,
        "weights": {
            "consistency": w_cons / total_weight, "community": w_comm / total_weight,
            "technology": w_tech / total_weight, "management": w_mgmt / total_weight, "advanced": w_adv / total_weight
        },
        "constants": {
            "epsilon": epsilon, "alpha": alpha, "beta": beta, "breadth_ceiling": breadth_ceiling,
            "gamma": gamma, "adv_target": adv_target,
            "sweet_spot_low": sweet_spot_low, "sweet_spot_high": sweet_spot_high, 
            "points_per_collab": points_per_collab, "partial_credit": partial_credit,
            "star_bonus": star_bonus, "fork_bonus": fork_bonus,
            "target_ratio": target_ratio, "bio_bonus": bio_bonus, "name_bonus": name_bonus
        }
    }
    
    return engine_config