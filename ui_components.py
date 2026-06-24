import streamlit as st
import pandas as pd
import math

def apply_custom_css():
    """
    Injects custom CSS to guarantee stark contrast.
    Strictly enforces black text on white backgrounds as requested.
    """
    st.markdown("""
        <style>
        /* Main background */
        .main { background-color: #F8FAFC; }
        
        /* Metric Cards */
        .stMetric { 
            background-color: #FFFFFF !important; 
            padding: 15px !important; 
            border-radius: 10px !important; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important; 
        }
        div[data-testid="stMetricValue"] > div { color: #000000 !important; font-weight: 800 !important; }
        label[data-testid="stMetricLabel"] > div > p { color: #333333 !important; font-weight: 600 !important; }
        
        /* Glass Box Explainers */
        .math-explainer { 
            background-color: #FFFFFF !important; 
            color: #000000 !important; 
            border-left: 5px solid #3B82F6 !important; 
            padding: 20px !important; 
            border-radius: 5px !important; 
            margin-bottom: 15px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        }
        .math-explainer p, .math-explainer b, .math-explainer span, .math-explainer div { 
            color: #000000 !important; 
        }
        
        /* Report Viewer Box */
        .report-viewer {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            padding: 30px !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.02) !important;
        }
        .report-viewer h1, .report-viewer h2, .report-viewer h3, .report-viewer p, .report-viewer li {
            color: #000000 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def render_kpi_dashboard(metrics: dict, username: str):
    """Renders the top-level metric scorecards and progress bars."""
    cats = metrics["category_scores"]
    
    st.subheader(f"📊 Telemetry Metrics for {username}")
    col_main, _ = st.columns([1, 3])
    with col_main:
        st.metric(label="🏆 Final Agent Score", value=f"{metrics['final_score']} / 100")
    
    st.write(" ")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Consistency", f"{cats['consistency']}%")
        st.progress(cats['consistency'] / 100.0)
    with c2:
        st.metric("Community", f"{cats['community']}%")
        st.progress(cats['community'] / 100.0)
    with c3:
        st.metric("Tech Depth", f"{cats['technology']}%")
        st.progress(cats['technology'] / 100.0)
    with c4:
        st.metric("Management", f"{cats['management']}%")
        st.progress(cats['management'] / 100.0)
    with c5:
        st.metric("Advanced", f"{cats['advanced']}%")
        st.progress(cats['advanced'] / 100.0)

def render_math_explainers(breakdowns: dict, category_scores: dict):
    """Renders the 5 interactive mathematical explainers with Step-by-Step Logic, LaTeX, and Charts."""
    st.markdown("### 🔍 The Glass Box: Mathematical Audit Breakdown")
    
    # 1. CONSISTENCY
    with st.expander("1. Show Consistency Calculation"):
        d = breakdowns['consistency']
        st.markdown(f"""<div class='math-explainer'>
            <b>Goal:</b> Rewards steady, predictable commits over erratic bursting.<br><br>
            <b>Step 1: Logarithmic Dampening & Mean (μ)</b><br>
            To prevent massive hackathon spikes from unfairly ruining the score, we compress your raw commits ({d['total_commits']}) using a Base-2 Logarithm. Your Log-Mean is <b>{d['mu']}</b>.<br><br>
            <b>Step 2: Calculate Variance (σ²)</b><br>
            Average of the squared differences from the Log-Mean.<br><br>
            <b>Step 3: Calculate Standard Deviation (σ)</b><br>
            Square Root of Variance = <b>{d['sigma']}</b><br><br>
            <b>Step 4: Apply the Penalty Coefficient</b><br>
            We divide the Deviation ({d['sigma']}) by the Mean + Epsilon ({d['mu']} + {d['epsilon']}) and subtract from 1.
        </div>""", unsafe_allow_html=True)
        st.latex(r"S_{consistency} = \max\left(0, 100 \times \left(1 - \frac{\sigma}{\mu + \epsilon}\right)\right)")
        st.latex(rf"Score = 100 \times \left(1 - \frac{{{d['sigma']}}}{{{d['mu']} + {d['epsilon']}}}\right) = {category_scores['consistency']}")

    # 2. COMMUNITY
    with st.expander("2. Show Community Calculation"):
        d = breakdowns['community']
        eng_pts = round(d['engagement_sum'] * d['points_per_collab'], 2)
        star_pts = round(d['total_stars'] * d['star_bonus'], 2)
        fork_pts = round(d['total_forks'] * d['fork_bonus'], 2)
        st.markdown(f"""<div class='math-explainer'>
            <b>Goal:</b> Measures collaboration and integration in shared codebases.<br><br>
            <b>Step 1: Calculate Team Engagement Points</b><br>
            Engagement Multiplier ({d['engagement_sum']}) × Points Per Collab ({d['points_per_collab']}) = <b>{eng_pts} pts</b><br><br>
            <b>Step 2: Calculate Personal Star Bonus</b><br>
            Total Stars ({d['total_stars']}) × Star Bonus ({d['star_bonus']}) = <b>{star_pts} pts</b><br><br>
            <b>Step 3: Calculate Personal Fork Bonus</b><br>
            Total Forks ({d['total_forks']}) × Fork Bonus ({d['fork_bonus']}) = <b>{fork_pts} pts</b><br><br>
            <b>Step 4: Sum and Cap</b><br>
            {eng_pts} + {star_pts} + {fork_pts} = <b>{eng_pts + star_pts + fork_pts}</b> (Capped at 100 max)
        </div>""", unsafe_allow_html=True)
        st.latex(r"S_{community} = \min\left(100, (\text{Engagement} \times P_{collab}) + (\text{Stars} \times B_{star}) + (\text{Forks} \times B_{fork})\right)")
        st.latex(rf"Score = ({d['engagement_sum']} \times {d['points_per_collab']}) + ({d['total_stars']} \times {d['star_bonus']}) + ({d['total_forks']} \times {d['fork_bonus']}) = {category_scores['community']}")

    # 3. TECHNOLOGY (WITH CHART)
    with st.expander("3. Show Technology Calculation"):
        d = breakdowns['technology']
        breadth_pts = round(d['capped_L'] * d['alpha'], 2)
        depth_pts = round(d['log_sum'] * d['beta'], 2)
        st.markdown(f"""<div class='math-explainer'>
            <b>Goal:</b> Balances language breadth against logarithmic depth.<br><br>
            <b>Step 1: Calculate Breadth Points</b><br>
            You used {d['L']} languages. The ceiling caps this at {d['breadth_ceiling']}.<br>
            Capped Languages ({d['capped_L']}) × Alpha ({d['alpha']}) = <b>{breadth_pts} pts</b><br><br>
            <b>Step 2: Calculate Depth Points (Diminishing Returns)</b><br>
            We take the Base-2 Logarithm of your usage frequency (see curve below).<br>
            Logarithmic Sum ({d['log_sum']}) × Beta ({d['beta']}) = <b>{depth_pts} pts</b><br><br>
            <b>Step 3: Sum and Cap</b><br>
            {breadth_pts} + {depth_pts} = <b>{breadth_pts + depth_pts}</b> (Capped at 100 max)
        </div>""", unsafe_allow_html=True)
        
        # Generate Logarithmic Curve Data for visual explanation
        x_vals = list(range(0, 30))
        y_vals = [d['beta'] * math.log2(x + 1) for x in x_vals]
        chart_data = pd.DataFrame({"Repositories Configured": x_vals, "Yielded Depth Points": y_vals}).set_index("Repositories Configured")
        st.line_chart(chart_data)
        
        st.latex(r"S_{technology} = \min\left(100, (\alpha \cdot |L_{capped}|) + (\beta \cdot \sum \log_2(v_l + 1))\right)")
        st.latex(rf"Score = ({d['alpha']} \times {d['capped_L']}) + ({d['beta']} \times {d['log_sum']}) = {category_scores['technology']}")

    # 4. MANAGEMENT
    with st.expander("4. Show Management Calculation"):
        d = breakdowns['management']
        readme_max = round(100.0 - d['bio_bonus'] - d['name_bonus'], 2)
        safe_target = d['target_ratio'] if d['target_ratio'] > 0 else 0.01
        readme_multiplier = min(1.0, d['readme_ratio'] / safe_target)
        readme_pts = round(readme_multiplier * readme_max, 2)
        bio_pts = d['bio_bonus'] if d['has_bio'] else 0.0
        name_pts = d['name_bonus'] if d['has_name'] else 0.0
        
        st.markdown(f"""<div class='math-explainer'>
            <b>Goal:</b> Evaluates code maintainability via READMEs and Profile completion.<br><br>
            <b>Step 1: Determine Available README Points</b><br>
            100 total - Bio Bonus ({d['bio_bonus']}) - Name Bonus ({d['name_bonus']}) = <b>{readme_max} max points</b><br><br>
            <b>Step 2: Calculate README Score</b><br>
            (Actual Ratio {d['readme_ratio']} ÷ Target Ratio {d['target_ratio']}) × {readme_max} max points = <b>{readme_pts} pts</b><br><br>
            <b>Step 3: Apply Profile Bonuses</b><br>
            Has Bio: {d['has_bio']} = <b>+{bio_pts} pts</b><br>
            Has Name: {d['has_name']} = <b>+{name_pts} pts</b><br><br>
            <b>Step 4: Final Sum</b><br>
            {readme_pts} + {bio_pts} + {name_pts} = <b>{readme_pts + bio_pts + name_pts}</b>
        </div>""", unsafe_allow_html=True)
        st.latex(r"S_{management} = \min\left(100, \left(\min\left(1, \frac{R_{actual}}{R_{target}}\right) \times P_{max}\right) + B_{bio} + B_{name}\right)")
        st.latex(rf"Score = {category_scores['management']}")

    # 5. ADVANCED CONTRIBUTIONS
    # 5. ADVANCED CONTRIBUTIONS
# 5. ADVANCED CONTRIBUTIONS
    with st.expander("5. Show Advanced Calculation"):
        d = breakdowns['advanced']
        
        # Build the dynamic HTML to show the math for EACH repository
        repo_receipts_html = ""
        for i, repo in enumerate(d.get('repo_breakdowns', [])):
            repo_receipts_html += f"""<div style='background-color: #F1F5F9; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 4px solid #475569;'>
<b>Repo {i+1}: <code>{repo['name']}</code></b><br>
<span style='font-size: 0.9em; color: #333;'>Stars: {repo['stars']} | Forks: {repo['forks']} | Your Commits: {repo['commits']}</span><br>
<span style='font-size: 0.95em;'>
• <b>Base Impact:</b> log10({repo['stars']} + {repo['forks']} + 1) = <b>{repo['base_impact']}</b><br>
• <b>Raw Score:</b> Gamma ({d['gamma']}) × Impact ({repo['base_impact']}) × Commits ({repo['commits']}) = <b>{repo['raw_score']}</b><br>
• <b>Capped Score:</b> <b>{repo['capped_score']}</b> <i>(Maximum allowed per repo: {d['max_per_repo']})</i>
</span>
</div>"""
            
        # Fallback if no repos
        if not repo_receipts_html:
            repo_receipts_html = "<div style='color: #DC2626; font-weight: bold;'>No active commits pushed to forked upstream repositories found.</div>"

        # The master explainer box (Notice how the text inside the quotes has NO indentation)
        st.markdown(f"""<div class='math-explainer'>
<b>Goal:</b> Evaluates open-source footprint based on upstream repo popularity (Base-10 Log) and active pushes.<br><br>

<b>Step 1 & 2 & 3: Calculate & Cap Each Valid Repository</b><br>
{repo_receipts_html}
<br>

<b>Step 4: Sum all Capped Repos</b><br>
Total calculated impact across your <b>{d['active_forks']}</b> active forks = <b>{category_scores['advanced']}</b>
</div>""", unsafe_allow_html=True)
        
        st.latex(r"\text{Raw Repo Score} = \gamma \cdot u_j \cdot \log_{10}(S_j + K_j + 1)")
        st.latex(r"S_{advanced} = \min\left(100, \sum \min\left(\text{Raw Repo Score}, P_{max\_per\_repo}\right)\right)")
        st.latex(rf"\text{{Final Score}} = {category_scores['advanced']}")  
            
def render_markdown_viewer(md_string: str, username: str):
    """Renders a beautiful inline Markdown viewer and provides the download button."""
    st.markdown("---")
    st.subheader("📄 Formal Audit Report")
    st.write("Preview your formal audit below. The downloaded Markdown file can be printed directly to PDF via any browser (CTRL+P) for a perfect stark-white background.")
    
    # The Interactive Viewer Box
    st.markdown(f"<div class='report-viewer'>{md_string}</div>", unsafe_allow_html=True)
    
    st.write(" ")
    st.download_button(
        label="⬇️ Download Markdown Report (.md)",
        data=md_string,
        file_name=f"{username}_audit_report.md",
        mime="text/markdown",
        type="primary"
    )