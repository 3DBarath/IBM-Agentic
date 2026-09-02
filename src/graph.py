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
# Node 4: Multi-Round Interview Kit Generator Node
# -------------------------------------------------------------
def generate_interview_kit_node(state: CandidateState) -> Dict[str, Any]:
    """
    Generate questions for 4 industry-standard tech interview rounds:
    Round 1: Recruiter Screening
    Round 2: Technical & Coding
    Round 3: System Design & Architecture
    Round 4: Behavioral (STAR)
    """
    jd = state["job_description"][:1200]
    resume = state["resume_text"][:2500]
    metrics = state["metrics"]
    gaps = state.get("skill_gap_analysis", "")
    
    prompt = f"""You are a Lead Hiring Architect and Talent Evaluator.
Design a specialized, high-impact multi-round interview kit specifically tailored for this candidate and target role.

Target Role & JD:
{jd}

Candidate Profile & Experience:
{resume}

Identified Skill Gaps:
{gaps}

Missing Requirements:
{', '.join(metrics['missing_skills'])}

Generate exactly 4 rounds in valid JSON format:
{{
  "round1_screening": [
    {{"question": "Question text", "focus": "Motivation / Background / Logistics", "rubric": "What to look for in the candidate's answer"}},
    {{"question": "Question text", "focus": "Role Alignment", "rubric": "Expected response criteria"}}
  ],
  "round2_technical": [
    {{"question": "Specific technical / coding question probing their claimed skills or gaps", "focus": "Core Language / DSA / Framework", "rubric": "Strong answer indicators and code efficiency expectations"}},
    {{"question": "Technical problem solving question", "focus": "Debugging / Problem Solving", "rubric": "Evaluation criteria"}}
  ],
  "round3_system_design": [
    {{"question": "System design scenario relevant to the JD", "focus": "Scalability & Architecture Tradeoffs", "rubric": "Expected component breakdown and handling of constraints"}},
    {{"question": "Data modeling or API design question", "focus": "Reliability & Data Flow", "rubric": "Key architectural considerations"}}
  ],
  "round4_behavioral": [
    {{"question": "Behavioral question using the STAR method (Situation, Task, Action, Result)", "focus": "Ownership & Delivery under pressure", "rubric": "Clear ownership, quantifiable outcome, and constructive reflection"}},
    {{"question": "Conflict resolution or technical disagreement question", "focus": "Collaboration & Communication", "rubric": "Empathetic, data-driven alignment"}}
  ]
}}

Ensure each round has 2-3 highly specific, non-generic questions.
Respond ONLY with the JSON object.
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
        kit = json.loads(cleaned.strip())
        
        return {
            "round1_screening": kit.get("round1_screening", []),
            "round2_technical": kit.get("round2_technical", []),
            "round3_system_design": kit.get("round3_system_design", []),
            "round4_behavioral": kit.get("round4_behavioral", [])
        }
    except Exception as e:
        logger.error(f"Interview kit fallback triggered: {e}")
        # Deterministic rich fallback
        primary_skill = metrics["matched_skills"][0] if metrics["matched_skills"] else "Software Engineering"
        missing_skill = metrics["missing_skills"][0] if metrics["missing_skills"] else "production cloud systems"
        
        return {
            "round1_screening": [
                {
                    "question": f"Can you walk us through the evolution of your work with {primary_skill} and how it prepared you for this role?",
                    "focus": "Career Trajectory & Technical Breadth",
                    "rubric": "Clear articulation of projects, ownership level, and motivation for the role."
                },
                {
                    "question": "What is your target work environment and what types of engineering challenges keep you most engaged?",
                    "focus": "Role Fit & Expectations",
                    "rubric": "Alignment with team pace, autonomy, and technology stack."
                }
            ],
            "round2_technical": [
                {
                    "question": f"How do you handle performance bottlenecks, state management, and memory overhead when implementing solutions in {primary_skill}?",
                    "focus": "Deep Domain Knowledge",
                    "rubric": "Understands profiling, async execution, caching strategies, and clean code principles."
                },
                {
                    "question": f"We noticed our role emphasizes {missing_skill}. How have you approached quickly ramping up on unfamiliar tools or frameworks in past roles?",
                    "focus": "Adaptability & Skill Gap Closure",
                    "rubric": "Evidence of rapid self-directed learning, prototype building, and conceptual transfer."
                }
            ],
            "round3_system_design": [
                {
                    "question": "Design an asynchronous background processing pipeline that can handle sudden 10x traffic spikes without losing incoming transactions.",
                    "focus": "Scalability & Resilience",
                    "rubric": "Mentions message queues (Kafka/RabbitMQ), idempotency, worker auto-scaling, and dead-letter queues."
                },
                {
                    "question": "How would you design the data model and caching strategy for high-concurrency read-heavy microservices?",
                    "focus": "Data Architecture & Trade-offs",
                    "rubric": "Discusses cache invalidation, Redis vs DB replication, and consistency trade-offs (CAP theorem)."
                }
            ],
            "round4_behavioral": [
                {
                    "question": "Describe a project where you faced tight deadlines and incomplete requirements. How did you prioritize tasks and deliver?",
                    "focus": "STAR: Ownership & Ambiguity",
                    "rubric": "Candidate describes proactive stakeholder alignment, incremental delivery, and concrete results."
                },
                {
                    "question": "Tell us about a technical disagreement you had with a teammate. How did you resolve it?",
                    "focus": "STAR: Collaboration & Empathy",
                    "rubric": "Focuses on objective data/benchmarks rather than ego; shows constructive team-first attitude."
                }
            ]
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
