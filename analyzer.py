import re
import PyPDF2
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

SKILLS = [
    "python", "sql", "java", "c++", "javascript", "bash",
    "mysql", "postgresql", "mongodb", "sqlite",
    "pandas", "numpy", "matplotlib", "seaborn",
    "scikit-learn", "tensorflow", "pytorch", "keras",
    "opencv", "spacy", "nltk", "streamlit", "flask",
    "fastapi", "django", "rest api", "aws", "azure",
    "gcp", "docker", "kubernetes", "linux", "git", "github",
    "spark", "kafka", "airflow", "hadoop", "hive",
    "etl", "data pipeline", "data warehouse",
    "power bi", "tableau", "excel",
    "machine learning", "deep learning",
    "data analysis", "data engineering",
    "natural language processing", "computer vision",
    "shell scripting", "data visualization",
    "statistical analysis", "data cleaning",
]

SUGGESTIONS = {
    "aws":               "Add AWS to skills — start with S3 and Lambda on free tier",
    "spark":             "Learn Apache Spark basics on Databricks community edition (free)",
    "airflow":           "Explore Apache Airflow for pipeline scheduling — 1 weekend",
    "docker":            "Containerise your JD Analyzer project using Docker",
    "kafka":             "Kafka is advanced — focus on this after AWS and Spark",
    "machine learning":  "Add ML projects or highlight scikit-learn usage",
    "deep learning":     "Your Lunar project uses deep learning — highlight it more",
    "tableau":           "You have Power BI — mention it prominently as an alternative",
    "postgresql":        "You know MySQL — PostgreSQL is similar, 2 days to learn",
    "flask":             "Wrap your JD Analyzer in a Flask API — 1 day task",
    "data pipeline":     "Build the weather ETL pipeline project from your roadmap",
    "data warehouse":    "Learn basic data warehouse concepts — free on Coursera",
    "etl":               "Your pipeline project directly demonstrates ETL — add it",
    "natural language processing": "Your JD Analyzer uses NLP — add it to your skills section",
    "git":               "Make your GitHub profile public and push all projects",
    "shell scripting":   "Learn basic bash scripting — 3 days, very useful for DE roles",
}


def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    stop_words = set(stopwords.words('english'))
    words = [w for w in text.split() if w not in stop_words]
    return ' '.join(words)


def extract_skills(text):
    text_lower = text.lower()
    found = set()
    for skill in SKILLS:
        if skill in text_lower:
            found.add(skill)
    return found


def analyze(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    jd_skills     = extract_skills(jd_text)

    matched = jd_skills & resume_skills
    missing = jd_skills - resume_skills
    extra   = resume_skills - jd_skills

    if len(jd_skills) == 0:
        score = 0
    else:
        score = round((len(matched) / len(jd_skills)) * 100, 1)

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