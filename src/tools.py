"""Candidate analysis tools and calculation utilities."""
import re
import json
from typing import Dict, List, Any

# Catalog of standardized tech skills for cross-referencing
TECH_SKILL_CATALOG = {
    # Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang", "rust", "ruby", "sql", "bash", "shell",
    # Frameworks & Libs
    "fastapi", "django", "flask", "react", "next.js", "vue", "angular", "node.js", "express", "spring", "spring boot",
    "langchain", "langgraph", "llamaindex", "huggingface", "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy",
    # Databases & Caching
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb", "chroma", "chromadb", "faiss",
    # Cloud & DevOps
    "docker", "kubernetes", "k8s", "aws", "azure", "gcp", "ci/cd", "git", "github", "terraform", "ansible", "linux", "nginx",
    # Architecture & Concepts
    "microservices", "rest api", "rest", "graphql", "rag", "agentic ai", "system design", "distributed systems", "kafka", "rabbitmq"
}

def extract_skills_from_text(text: str) -> List[str]:
    """Extract known technical skills and tools from arbitrary text."""
    lowered = text.lower()
    found = set()
    for skill in TECH_SKILL_CATALOG:
        # Match whole word or exact term
        pattern = r'(?:\b|\W)' + re.escape(skill) + r'(?:\b|\W)'
        if re.search(pattern, lowered):
            found.add(skill.title() if len(skill) > 3 else skill.upper())
    return sorted(list(found))

def calculate_match_metrics(jd_skills: List[str], resume_skills: List[str], semantic_score: float) -> Dict[str, Any]:
    """
    Deterministic score calculation combining:
    1. Direct Skill Overlap (45%)
    2. Semantic RAG Relevance (40%)
    3. Experience / Breadth Factor (15%)
    """
    jd_set = set(s.lower() for s in jd_skills)
    res_set = set(s.lower() for s in resume_skills)
    
    if not jd_set:
        skill_match_ratio = 0.5
        matched_skills = []
        missing_skills = []
    else:
        matched = jd_set.intersection(res_set)
        missing = jd_set.difference(res_set)
        skill_match_ratio = len(matched) / len(jd_set)
        matched_skills = sorted([s.title() for s in matched])
        missing_skills = sorted([s.title() for s in missing])
        
    # Extra bonus skills present in resume
    additional_skills = sorted([s.title() for s in res_set.difference(jd_set)])
    
    # Combined score
    raw_score = (skill_match_ratio * 45) + (min(semantic_score * 1.5, 1.0) * 40) + (min(len(res_set) / 10, 1.0) * 15)
    overall_score = max(5, min(98, int(round(raw_score))))
    
    # Categorization
    if overall_score >= 80:
        recommendation = "Strong Hire / Fast Track"
        fit_level = "High"
    elif overall_score >= 60:
        recommendation = "Interview / Potential Match"
        fit_level = "Medium"
    else:
        recommendation = "Review Required / Low Alignment"
        fit_level = "Low"

    return {
        "overall_score": overall_score,
        "fit_level": fit_level,
        "recommendation": recommendation,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_skills": additional_skills[:8],
        "skill_match_percent": int(round(skill_match_ratio * 100))
    }
