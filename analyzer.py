# analyzer.py

import re
import PyPDF2
import nltk
from nltk.corpus import stopwords

# Load spaCy model once at the top
# en_core_web_sm is the small English model
nlp = spacy.load("en_core_web_sm")

# ── SKILLS DATABASE ───────────────────────────────────────────────
# Multi-word skills now work correctly because spaCy
# processes the full text as phrases, not just single words
SKILLS = [
    # Programming
    "python", "sql", "java", "c++", "javascript", "bash",

    # Databases
    "mysql", "postgresql", "mongodb", "sqlite",

    # Data & ML Libraries
    "pandas", "numpy", "matplotlib", "seaborn",
    "scikit-learn", "tensorflow", "pytorch", "keras",
    "opencv", "spacy", "nltk",

    # Web & API
    "streamlit", "flask", "fastapi", "django", "rest api",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes",
    "linux", "git", "github",

    # Data Engineering (your target field)
    "spark", "kafka", "airflow", "hadoop", "hive",
    "etl", "data pipeline", "data warehouse",

    # BI & Visualization
    "power bi", "tableau", "excel",

    # Concepts (multi-word — this is where spaCy helps)
    "machine learning", "deep learning",
    "data analysis", "data engineering",
    "natural language processing", "computer vision",
    "shell scripting", "data visualization",
    "statistical analysis", "data cleaning",
]

# ── SUGGESTIONS DATABASE ──────────────────────────────────────────
SUGGESTIONS = {
    "aws":                      "Add AWS to skills — start with S3 and Lambda on free tier",
    "spark":                    "Learn Apache Spark basics on Databricks community edition (free)",
    "airflow":                  "Explore Apache Airflow for pipeline scheduling — 1 weekend",
    "docker":                   "Containerise your JD Analyzer project using Docker",
    "kafka":                    "Kafka is advanced — focus on this after AWS and Spark",
    "machine learning":         "Add ML projects or highlight scikit-learn usage",
    "deep learning":            "Your Lunar project uses deep learning — highlight it more",
    "tableau":                  "You have Power BI — mention it prominently as an alternative",
    "postgresql":               "You know MySQL — PostgreSQL is similar, 2 days to learn",
    "flask":                    "Wrap your JD Analyzer in a Flask API — 1 day task",
    "data pipeline":            "Build the weather ETL pipeline project from your roadmap",
    "data warehouse":           "Learn basic data warehouse concepts — free on Coursera",
    "etl":                      "Your pipeline project directly demonstrates ETL — add it",
    "natural language processing": "Your JD Analyzer uses NLP — add it to your skills section",
    "git":                      "Make your GitHub profile public and push all projects",
    "shell scripting":          "Learn basic bash scripting — 3 days, very useful for DE roles",
}


# ── EXTRACT TEXT FROM PDF ─────────────────────────────────────────
def extract_text_from_pdf(uploaded_file):
    """Read uploaded PDF and return all text as a string."""
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


# ── CLEAN TEXT WITH SPACY ─────────────────────────────────────────
def clean_text(text):
    """
    Use spaCy to clean text.
    - Removes stopwords (the, and, is...)
    - Removes punctuation
    - Lemmatizes words (running → run, skills → skill)
    - Keeps only meaningful tokens
    """
    doc = nlp(text.lower())
    tokens = [
        token.lemma_           # lemma = base form of word
        for token in doc
        if not token.is_stop   # remove stopwords
        and not token.is_punct # remove punctuation
        and not token.is_space # remove whitespace
        and len(token.text) > 1 # remove single characters
    ]
    return " ".join(tokens)


# ── EXTRACT SKILLS USING SPACY ────────────────────────────────────
def extract_skills(text):
    """
    Find which skills from SKILLS list appear in the text.
    spaCy handles multi-word phrases like 'machine learning' correctly.
    """
    text_lower = text.lower()

    # Process text with spaCy for lemmatization
    doc = nlp(text_lower)
    lemmatized = " ".join([token.lemma_ for token in doc])

    found_skills = set()

    for skill in SKILLS:
        # Check original text first (for exact phrases like "power bi")
        if skill in text_lower:
            found_skills.add(skill)
        # Also check lemmatized text (catches "Python skills" → "python skill")
        elif skill in lemmatized:
            found_skills.add(skill)

    return found_skills


# ── MAIN ANALYZE FUNCTION ─────────────────────────────────────────
def analyze(resume_text, jd_text):
    """
    Core function.
    Input : resume text (string), jd text (string)
    Output: dict with score, matched, missing, suggestions
    """
    # Extract skills from both texts
    resume_skills = extract_skills(resume_text)
    jd_skills     = extract_skills(jd_text)

    # Set operations — this is the heart of the analyzer
    matched = jd_skills & resume_skills   # skills in BOTH
    missing = jd_skills - resume_skills   # skills in JD but NOT resume
    extra   = resume_skills - jd_skills   # skills in resume but NOT JD

    # Calculate match score
    if len(jd_skills) == 0:
        score = 0
    else:
        score = round((len(matched) / len(jd_skills)) * 100, 1)

    # Build suggestions only for missing skills
    suggestions = []
    for skill in sorted(missing):
        if skill in SUGGESTIONS:
            suggestions.append(f"{skill.upper()}: {SUGGESTIONS[skill]}")
        else:
            suggestions.append(
                f"{skill.upper()}: Consider adding this to your resume or projects"
            )

    return {
        "score":       score,
        "matched":     sorted(matched),
        "missing":     sorted(missing),
        "extra":       sorted(extra),
        "suggestions": suggestions,
        "jd_skills":   jd_skills,
    }