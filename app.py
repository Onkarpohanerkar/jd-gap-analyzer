# app.py

import streamlit as st
from analyzer import analyze, extract_text_from_pdf

# ── Page Setup ────────────────────────────────────────────────────
st.set_page_config(
    page_title="JD Skill Gap Analyzer",
    page_icon="🎯",
    layout="wide"
)

# ── Custom CSS for compact skill badges ───────────────────────────
st.markdown("""
<style>
    .skill-matched {
        display: inline-block;
        background-color: #1a472a;
        color: #4ade80;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 3px;
        font-size: 13px;
        border: 1px solid #4ade80;
    }
    .skill-missing {
        display: inline-block;
        background-color: #450a0a;
        color: #f87171;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 3px;
        font-size: 13px;
        border: 1px solid #f87171;
    }
    .skill-bonus {
        display: inline-block;
        background-color: #1e3a5f;
        color: #60a5fa;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 3px;
        font-size: 13px;
        border: 1px solid #60a5fa;
    }
    .suggestion-item {
        background-color: #1c1a05;
        border-left: 3px solid #fcd34d;
        padding: 8px 12px;
        margin: 6px 0;
        border-radius: 4px;
        font-size: 13px;
        color: #fcd34d;
    }
    .summary-box {
        background-color: #1e293b;
        padding: 16px;
        border-radius: 8px;
        margin: 10px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Title ─────────────────────────────────────────────────────────
st.title("🎯 JD Skill Gap Analyzer")
st.markdown("Upload your resume and paste a Job Description — get your match score instantly.")
st.markdown("---")

# ── Input Section ─────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume")
    uploaded_file = st.file_uploader("Upload PDF resume", type=["pdf"])
    resume_paste  = st.text_area(
        "Or paste resume text here",
        height=200,
        placeholder="Paste your resume text here if not uploading PDF..."
    )

with col2:
    st.subheader("💼 Job Description")
    jd_text = st.text_area(
        "Paste the full Job Description here",
        height=270,
        placeholder="Paste the complete job description here..."
    )

st.markdown("---")

# ── Analyze Button ────────────────────────────────────────────────
col_btn = st.columns([2, 1, 2])
with col_btn[1]:
    analyze_btn = st.button(
        "🔍 Analyze Now",
        type="primary",
        use_container_width=True
    )

# ── Run Analysis ──────────────────────────────────────────────────
if analyze_btn:

    # Validate inputs
    if uploaded_file is not None:
        with st.spinner("Reading your PDF..."):
            resume_text = extract_text_from_pdf(uploaded_file)
    elif resume_paste.strip():
        resume_text = resume_paste
    else:
        st.error("Please upload a PDF or paste your resume text.")
        st.stop()

    if not jd_text.strip():
        st.error("Please paste a Job Description.")
        st.stop()

    # Run the analyzer
    with st.spinner("Analyzing with spaCy NLP..."):
        result = analyze(resume_text, jd_text)

    st.markdown("---")

    # ── Score Section ─────────────────────────────────────────────
    score = result["score"]

    if score >= 70:
        score_color = "green"
        score_msg   = "Strong Match 🟢"
        bar_color   = "normal"
    elif score >= 40:
        score_color = "orange"
        score_msg   = "Moderate Match 🟡"
        bar_color   = "normal"
    else:
        score_color = "red"
        score_msg   = "Weak Match 🔴"
        bar_color   = "normal"

    # Summary row — 4 metric cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Match Score",    f"{score}%")
    m2.metric("JD Skills",      len(result["jd_skills"]))
    m3.metric("✅ Matched",     len(result["matched"]))
    m4.metric("❌ Missing",     len(result["missing"]))

    st.markdown(f"### {score_msg} — {score}%")
    st.progress(int(score))
    st.markdown("---")

    # ── Results: 3 columns ────────────────────────────────────────
    r1, r2, r3 = st.columns([1, 1, 1.2])

    with r1:
        st.markdown(f"### ✅ Matched Skills")
        st.caption(f"{len(result['matched'])} skills found in both")
        st.markdown(" ".join([
            f'<span class="skill-matched">✓ {s.title()}</span>'
            for s in result["matched"]
        ]), unsafe_allow_html=True)

    with r2:
        st.markdown(f"### ❌ Missing Skills")
        st.caption(f"{len(result['missing'])} skills to work on")
        st.markdown(" ".join([
            f'<span class="skill-missing">✗ {s.title()}</span>'
            for s in result["missing"]
        ]), unsafe_allow_html=True)

    with r3:
        st.markdown("### 💡 Suggestions")
        st.caption("How to close the gap")

        # Show only top 5 suggestions by default
        top_5 = result["suggestions"][:5]
        rest  = result["suggestions"][5:]

        for s in top_5:
            st.markdown(
                f'<div class="suggestion-item">{s}</div>',
                unsafe_allow_html=True
            )

        # Hide remaining in expander
        if rest:
            with st.expander(f"Show {len(rest)} more suggestions"):
                for s in rest:
                    st.markdown(
                        f'<div class="suggestion-item">{s}</div>',
                        unsafe_allow_html=True
                    )

    # ── Bonus Skills ──────────────────────────────────────────────
    if result["extra"]:
        st.markdown("---")
        st.markdown("### 🎁 Bonus Skills on Your Resume")
        st.caption("On your resume but not required by this JD")
        st.markdown(" ".join([
            f'<span class="skill-bonus">{s.title()}</span>'
            for s in result["extra"]
        ]), unsafe_allow_html=True)