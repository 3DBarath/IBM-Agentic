"""
LangGraph stateful workflow for candidate evaluation, Agentic RAG,
and multi-round enterprise interview kit generation.
"""
import json
import logging
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from src.tools import extract_skills_from_text, calculate_match_metrics
from src.rag import chunk_text, LocalSemanticRAGStore
from src.llm import llm_client

logger = logging.getLogger("recruitment_assistant.graph")

class CandidateState(TypedDict):
    # Inputs
    resume_text: str
    job_description: str
    candidate_name: str
    target_role: str
    
    # Internal Artifacts
    resume_chunks: List[Dict[str, Any]]
    retrieved_evidence: List[Dict[str, Any]]
    jd_skills: List[str]
    resume_skills: List[str]
    metrics: Dict[str, Any]
    
    # Outputs
    candidate_summary: str
    skill_gap_analysis: str
    round1_screening: List[Dict[str, str]]
    round2_technical: List[Dict[str, str]]
    round3_system_design: List[Dict[str, str]]
    round4_behavioral: List[Dict[str, str]]
    hiring_recommendation: str
    full_dossier_markdown: str
    error: Optional[str]


# -------------------------------------------------------------
# Node 1: Ingestion & Parsing Node
# -------------------------------------------------------------
def parse_and_chunk_node(state: CandidateState) -> Dict[str, Any]:
    """Parse resume sections, identify candidate info, and produce overlapping text chunks."""
    resume_text = state["resume_text"]
    jd_text = state["job_description"]
    
    # Chunk resume
    chunks = chunk_text(resume_text, chunk_size=250, overlap=50)
    
    # Extract technical skills
    jd_skills = extract_skills_from_text(jd_text)
    resume_skills = extract_skills_from_text(resume_text)
    
    return {
        "resume_chunks": chunks,
        "jd_skills": jd_skills,
        "resume_skills": resume_skills
    }


# -------------------------------------------------------------
# Node 2: Agentic RAG Retrieval Node
# -------------------------------------------------------------
def rag_retrieval_node(state: CandidateState) -> Dict[str, Any]:
    """Build semantic vector index from candidate chunks and query against core JD requirements."""
    chunks = state["resume_chunks"]
    jd_text = state["job_description"]
    
    rag_store = LocalSemanticRAGStore()
    rag_store.index_documents(chunks)
    
    # Retrieve evidence matching the JD
    top_matches = rag_store.search(jd_text, top_k=5)
    
    # Compute average relevance score
    if top_matches:
        avg_relevance = sum(m["score"] for m in top_matches) / len(top_matches)
    else:
        avg_relevance = 0.3
        
    metrics = calculate_match_metrics(
        jd_skills=state["jd_skills"],
        resume_skills=state["resume_skills"],
        semantic_score=avg_relevance
    )
    
    return {
        "retrieved_evidence": top_matches,
        "metrics": metrics
    }


# -------------------------------------------------------------
# Node 3: Candidate Summary & Gap Analysis Node
# -------------------------------------------------------------
def analyze_candidate_node(state: CandidateState) -> Dict[str, Any]:
    """Generate structured summary and identify strengths and critical skill gaps."""
    jd = state["job_description"]
    resume = state["resume_text"][:3000]
    metrics = state["metrics"]
    
    prompt = f"""You are a Senior Technical Recruiter and Engineering Manager.
Analyze the following Candidate Resume against the Job Description.

Job Description:
{jd[:1500]}

Candidate Resume (Excerpt):
{resume}

Extracted Match Data:
- Overall Compatibility Score: {metrics['overall_score']}/100
- Matched Skills: {', '.join(metrics['matched_skills']) if metrics['matched_skills'] else 'None explicit'}
- Missing / Gap Skills: {', '.join(metrics['missing_skills']) if metrics['missing_skills'] else 'None detected'}

Generate a crisp JSON object with these two fields:
1. "candidate_summary": 2-3 concise sentences summarizing the candidate's core background, years of experience, and strongest domain.
2. "gap_analysis": 2-3 bullet points highlighting where the candidate might face challenges relative to the JD requirements.

Respond ONLY with valid JSON. Do not include markdown codeblock backticks if possible, or wrap in standard ```json.
"""
    try:
        raw_res = llm_client.invoke(prompt)
        cleaned = raw_res.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        data = json.loads(cleaned.strip())
        return {
            "candidate_summary": data.get("candidate_summary", "Candidate exhibits relevant experience matching key technical areas."),
            "skill_gap_analysis": data.get("gap_analysis", "Candidate may require onboarding ramp-up on target domain frameworks.")
        }
    except Exception as e:
        logger.error(f"Analysis node fallback triggered: {e}")
        return {
            "candidate_summary": f"Candidate demonstrates skills in {', '.join(metrics['matched_skills'][:4]) or 'general software development'}.",
            "skill_gap_analysis": f"Potential skill gaps observed in {', '.join(metrics['missing_skills'][:3]) or 'specialized tooling'}."
        }


# -------------------------------------------------------------
# Node 4: Multi-Round Interview Kit Generator Node (Concurrent Threads)
# -------------------------------------------------------------
from concurrent.futures import ThreadPoolExecutor

def _fetch_round1_screening(jd: str, resume: str, metrics: Dict[str, Any], gaps: str) -> List[Dict[str, str]]:
    """Worker Thread 1: Initial Recruiter Screening."""
    prompt = f"""You are a Lead Technical Recruiter.
Generate Round 1 (Initial Screening) questions for this candidate.
Target Role & JD: {jd}
Candidate Profile: {resume}
Gaps: {gaps}

Generate exactly 2-3 screening questions focusing on background, career trajectory, and role alignment.
Return a valid JSON array only:
[
  {{"question": "...", "focus": "Motivation / Background / Logistics", "rubric": "Expected candidate response indicators"}}
]
Respond ONLY with the JSON array. Do not include extra text.
"""
    try:
        raw = llm_client.invoke(prompt)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(cleaned)
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"Thread 1 error: {e}")
        primary = metrics["matched_skills"][0] if metrics["matched_skills"] else "Software Engineering"
        return [
            {"question": f"Can you walk us through your experience with {primary} and what motivated you to pursue this role?", "focus": "Motivation & Background", "rubric": "Clear career narrative and genuine role alignment."},
            {"question": "What engineering team culture allows you to do your best work?", "focus": "Workplace Expectations", "rubric": "Alignment with collaborative ownership and fast delivery."}
        ]

def _fetch_round2_technical(jd: str, resume: str, metrics: Dict[str, Any], gaps: str) -> List[Dict[str, str]]:
    """Worker Thread 2: Core Technical & DSA / Coding Screen."""
    prompt = f"""You are a Senior Engineering Interviewer.
Generate Round 2 (Technical & Coding Screen) questions for this candidate.
Target Role & JD: {jd}
Candidate Profile: {resume}
Missing Requirements: {', '.join(metrics.get('missing_skills', []))}

Generate exactly 2-3 specific technical/coding questions probing claimed skills and missing gaps.
Return a valid JSON array only:
[
  {{"question": "...", "focus": "Core Language / DSA / Framework", "rubric": "Expected code efficiency, syntax depth, and edge cases"}}
]
Respond ONLY with the JSON array. Do not include extra text.
"""
    try:
        raw = llm_client.invoke(prompt)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(cleaned)
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"Thread 2 error: {e}")
        primary = metrics["matched_skills"][0] if metrics["matched_skills"] else "Python"
        missing = metrics["missing_skills"][0] if metrics["missing_skills"] else "distributed systems"
        return [
            {"question": f"How do you manage memory allocation, concurrency, and performance bottlenecks when building services in {primary}?", "focus": "Core Language & Profiling", "rubric": "Understands profiling tools, async runtime, and algorithmic complexity."},
            {"question": f"This role requires {missing}. How have you approached quickly gaining mastery over new technologies in past projects?", "focus": "Technical Adaptability", "rubric": "Demonstrates structured learning, sandbox prototyping, and fast comprehension."}
        ]

def _fetch_round3_system_design(jd: str, resume: str, metrics: Dict[str, Any], gaps: str) -> List[Dict[str, str]]:
    """Worker Thread 3: System Design & Architecture."""
    prompt = f"""You are a Principal Software Architect.
Generate Round 3 (System Architecture & Scalability) scenario questions for this candidate.
Target Role & JD: {jd}
Candidate Profile: {resume}

Generate exactly 2 high-impact architecture and scalability scenarios relevant to the JD.
Return a valid JSON array only:
[
  {{"question": "...", "focus": "Scalability & Resilience Trade-offs", "rubric": "Component breakdown, storage choice, caching, and failover strategy"}}
]
Respond ONLY with the JSON array. Do not include extra text.
"""
    try:
        raw = llm_client.invoke(prompt)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(cleaned)
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"Thread 3 error: {e}")
        return [
            {"question": "Design an asynchronous processing pipeline capable of ingesting 50,000 events/sec while guaranteeing zero message loss during worker crashes.", "focus": "Distributed Queues & Idempotency", "rubric": "Covers message brokers (Kafka/RabbitMQ), consumer groups, dead-letter queues, and at-least-once delivery."},
            {"question": "How would you design the data storage and caching tier for a high-concurrency read-heavy microservice?", "focus": "Data Architecture & Cache Invalidation", "rubric": "Discusses Redis cache-aside vs write-through, DB read-replicas, and consistency trade-offs (CAP theorem)."}
        ]

def _fetch_round4_behavioral(jd: str, resume: str, metrics: Dict[str, Any], gaps: str) -> List[Dict[str, str]]:
    """Worker Thread 4: Behavioral & Culture Fit (STAR Framework)."""
    prompt = f"""You are an Engineering Director evaluating culture fit.
Generate Round 4 (Behavioral / STAR Method) questions for this candidate.
Target Role & JD: {jd}
Candidate Profile: {resume}

Generate exactly 2 behavioral questions using the STAR framework (Situation, Task, Action, Result).
Return a valid JSON array only:
[
  {{"question": "...", "focus": "STAR: Ownership / Collaboration / Pressure", "rubric": "Candidate describes quantifiable action, constructive reflection, and team alignment"}}
]
Respond ONLY with the JSON array. Do not include extra text.
"""
    try:
        raw = llm_client.invoke(prompt)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(cleaned)
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"Thread 4 error: {e}")
        return [
            {"question": "Describe a project where you faced a tight production deadline and ambiguous requirements. How did you prioritize tasks and deliver?", "focus": "STAR: Execution & Ambiguity", "rubric": "Candidate describes proactive stakeholder communication, iterative delivery, and measurable outcomes."},
            {"question": "Tell us about a technical disagreement you had with a team member. How did you resolve it?", "focus": "STAR: Empathy & Team Consensus", "rubric": "Focuses on benchmarks and shared goals rather than ego; shows collaborative leadership."}
        ]

def generate_interview_kit_node(state: CandidateState) -> Dict[str, Any]:
    """
    Simultaneously execute 4 independent worker threads for the 4 interview rounds.
    Reduces total question generation latency by up to ~4x.
    """
    jd = state["job_description"][:1200]
    resume = state["resume_text"][:2500]
    metrics = state["metrics"]
    gaps = state.get("skill_gap_analysis", "")

    # Run 4 workers in parallel threads
    with ThreadPoolExecutor(max_workers=4) as executor:
        f_r1 = executor.submit(_fetch_round1_screening, jd, resume, metrics, gaps)
        f_r2 = executor.submit(_fetch_round2_technical, jd, resume, metrics, gaps)
        f_r3 = executor.submit(_fetch_round3_system_design, jd, resume, metrics, gaps)
        f_r4 = executor.submit(_fetch_round4_behavioral, jd, resume, metrics, gaps)

        r1 = f_r1.result()
        r2 = f_r2.result()
        r3 = f_r3.result()
        r4 = f_r4.result()

    return {
        "round1_screening": r1,
        "round2_technical": r2,
        "round3_system_design": r3,
        "round4_behavioral": r4
    }


# -------------------------------------------------------------
# Node 5: Executive Candidate Dossier Synthesizer Node
# -------------------------------------------------------------
def synthesize_dossier_node(state: CandidateState) -> Dict[str, Any]:
    """Synthesize all metrics, gaps, and rounds into a formal candidate evaluation dossier."""
    name = state.get("candidate_name") or "Candidate"
    metrics = state["metrics"]
    summary = state.get("candidate_summary", "")
    gaps = state.get("skill_gap_analysis", "")
    rec = metrics.get("recommendation", "Review Required")
    score = metrics.get("overall_score", 0)
    
    dossier = f"""# Executive Candidate Evaluation Dossier

**Candidate Name:** {name}  
**Overall Alignment Score:** {score} / 100 ({metrics.get('fit_level', 'Medium')} Fit)  
**Recommendation:** {rec}  

---

## 1. Executive Summary
{summary}

## 2. Skill Matrix Analysis
- **Key Matched Skills:** {', '.join(metrics['matched_skills']) if metrics['matched_skills'] else 'None detected'}
- **Missing / Target Requirements:** {', '.join(metrics['missing_skills']) if metrics['missing_skills'] else 'None detected'}
- **Additional Candidate Strengths:** {', '.join(metrics['additional_skills']) if metrics['additional_skills'] else 'None'}

## 3. Skill Gap & Risk Assessment
{gaps}

## 4. Suggested Multi-Round Interview Track
- **Round 1 (Screening):** {len(state.get('round1_screening', []))} questions prepared
- **Round 2 (Technical Screen):** {len(state.get('round2_technical', []))} questions prepared
- **Round 3 (System Architecture):** {len(state.get('round3_system_design', []))} questions prepared
- **Round 4 (Behavioral / Culture Fit):** {len(state.get('round4_behavioral', []))} questions prepared

*Report generated by IBM Agentic AI Talent Assistant.*
"""
    return {
        "hiring_recommendation": rec,
        "full_dossier_markdown": dossier
    }


# -------------------------------------------------------------
# Build & Compile the LangGraph
# -------------------------------------------------------------
def create_recruitment_agent():
    """Build the compiled LangGraph workflow state machine."""
    workflow = StateGraph(CandidateState)
    
    # Register nodes
    workflow.add_node("parse_and_chunk", parse_and_chunk_node)
    workflow.add_node("rag_retrieval", rag_retrieval_node)
    workflow.add_node("analyze_candidate", analyze_candidate_node)
    workflow.add_node("generate_interview_kit", generate_interview_kit_node)
    workflow.add_node("synthesize_dossier", synthesize_dossier_node)
    
    # Connect sequential flow with state passing
    workflow.set_entry_point("parse_and_chunk")
    workflow.add_edge("parse_and_chunk", "rag_retrieval")
    workflow.add_edge("rag_retrieval", "analyze_candidate")
    workflow.add_edge("analyze_candidate", "generate_interview_kit")
    workflow.add_edge("generate_interview_kit", "synthesize_dossier")
    workflow.add_edge("synthesize_dossier", END)
    
    return workflow.compile()

# Global compiled agent instance
recruitment_agent = create_recruitment_agent()
