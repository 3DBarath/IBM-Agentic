// Instant reactive controller adhering to minimalist-ui and modern web guidelines
let currentEvaluationData = null;
let activeRoundKey = "round1";

const SAMPLE_SENIOR_JD = `Role: Senior Agentic AI & Systems Engineer
Requirements:
- 4+ years building production applications in Python, FastAPI, and asynchronous architectures.
- Deep hands-on experience with LangChain, LangGraph state machines, and Agentic RAG workflows.
- Strong knowledge of Vector databases (ChromaDB, FAISS), embeddings, and semantic chunking.
- Hands-on microservices deployment with Docker, Kubernetes, CI/CD, and Redis caching.
- Familiarity with LLM deployment, prompt engineering, and tool calling under low latency constraints.`;

const SAMPLE_SENIOR_RESUME = `Alex Chen - Senior Software Engineer
Email: alex.chen@example.com | GitHub: github.com/alexchen-dev

PROFESSIONAL SUMMARY
Senior Software Engineer with 5 years of experience architecting distributed backend services and Agentic AI applications in Python. Expert in LangChain, FastAPI, Docker, and Vector retrieval systems.

EXPERIENCE
Lead Backend Engineer | Nova Systems (2022 - Present)
- Architected multi-agent customer routing workflow using LangChain and LangGraph, cutting ticket resolution time by 38%.
- Built high-throughput semantic RAG pipeline using ChromaDB, processing 150k documents daily with sub-second retrieval.
- Developed asynchronous microservices in Python and FastAPI, containerized with Docker and orchestrated via Kubernetes.
- Integrated Redis cluster for low-latency session caching and distributed state management.

Software Engineer | Apex Cloud Technologies (2019 - 2022)
- Built RESTful APIs using Python, Flask, and PostgreSQL for enterprise analytics.
- Automated CI/CD deployment pipelines on GitHub Actions, reducing release cycle time by 45%.
- Implemented unit and integration test suites using PyTest with 90%+ code coverage.

SKILLS
Languages & Frameworks: Python, FastAPI, Flask, SQL, Bash
AI & Agents: LangChain, LangGraph, RAG, ChromaDB, HuggingFace, OpenAI API
Infrastructure: Docker, Kubernetes, Git, GitHub Actions, Redis, PostgreSQL, Linux`;

const SAMPLE_JUNIOR_JD = `Role: Junior Python Backend Developer
Requirements:
- 1-2 years experience with Python and REST APIs.
- Experience with databases like PostgreSQL or MySQL.
- Basic understanding of Docker, Git, and unit testing.
- Willingness to learn AI frameworks and microservice design.`;

const SAMPLE_JUNIOR_RESUME = `Priya Sharma - Junior Python Developer
Email: priya.s@example.com | Portfolio: priyasharma.dev

EDUCATION: B.Tech Computer Science, Anna University (2024)

TECHNICAL SKILLS:
Languages: Python, JavaScript, SQL
Frameworks: Django, Flask, Pandas
Tools: Git, GitHub, SQLite, Postman, Linux

PROJECTS:
1. Inventory Management API: Built REST API using Flask and SQLite, implemented JWT authentication.
2. College Notice Aggregator: Scraped university portal using BeautifulSoup and Python.`;

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("evaluationForm");
  const dropArea = document.getElementById("dropArea");
  const fileInput = document.getElementById("resumePdf");
  const dropText = document.getElementById("dropText");
  const btnSubmit = document.getElementById("btnSubmit");
  const resultsContent = document.getElementById("resultsContent");
  const emptyState = document.getElementById("emptyState");
  const btnCopyDossier = document.getElementById("btnCopyDossier");
  
  // Theme Switching: Editorial Light vs Editorial Dark
  const themeBtnLight = document.getElementById("themeBtnLight");
  const themeBtnDark = document.getElementById("themeBtnDark");

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("recruitment_editorial_theme", theme);
    if (theme === "editorial-dark") {
      themeBtnDark.classList.add("active");
      themeBtnLight.classList.remove("active");
    } else {
      themeBtnLight.classList.add("active");
      themeBtnDark.classList.remove("active");
    }
  }

  // Restore saved theme or default to editorial-light
  const savedTheme = localStorage.getItem("recruitment_editorial_theme") || "editorial-light";
  setTheme(savedTheme);

  themeBtnLight.addEventListener("click", () => setTheme("editorial-light"));
  themeBtnDark.addEventListener("click", () => setTheme("editorial-dark"));

  // Sample Presets (<5ms instant response)
  document.getElementById("btnPrefillFullstack").addEventListener("click", () => {
    document.getElementById("candidateName").value = "Alex Chen";
    document.getElementById("targetRole").value = "Lead AI Systems Engineer";
    document.getElementById("jobDescription").value = SAMPLE_SENIOR_JD;
    document.getElementById("resumeText").value = SAMPLE_SENIOR_RESUME;
    fileInput.value = "";
    dropText.innerHTML = "<strong>Select PDF file</strong> or drag & drop resume";
  });

  document.getElementById("btnPrefillJunior").addEventListener("click", () => {
    document.getElementById("candidateName").value = "Priya Sharma";
    document.getElementById("targetRole").value = "Junior Python Developer";
    document.getElementById("jobDescription").value = SAMPLE_JUNIOR_JD;
    document.getElementById("resumeText").value = SAMPLE_JUNIOR_RESUME;
    fileInput.value = "";
    dropText.innerHTML = "<strong>Select PDF file</strong> or drag & drop resume";
  });

  // Dropzone file picking
  dropArea.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      dropText.innerHTML = `Loaded: <strong>${fileInput.files[0].name}</strong> (${Math.round(fileInput.files[0].size / 1024)} KB)`;
    }
  });

  ["dragenter", "dragover"].forEach(event => {
    dropArea.addEventListener(event, (e) => {
      e.preventDefault();
      dropArea.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach(event => {
    dropArea.addEventListener(event, (e) => {
      e.preventDefault();
      dropArea.classList.remove("dragover");
    });
  });

  dropArea.addEventListener("drop", (e) => {
    if (e.dataTransfer.files.length > 0) {
      fileInput.files = e.dataTransfer.files;
      dropText.innerHTML = `Loaded: <strong>${e.dataTransfer.files[0].name}</strong>`;
    }
  });

  // Tab switching (<5ms DOM update)
  document.querySelectorAll(".tab-link").forEach(button => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab-link").forEach(b => b.classList.remove("active"));
      button.classList.add("active");
      activeRoundKey = button.dataset.round;
      renderActiveRoundQuestions();
    });
  });

  // Copy Dossier Markdown
  btnCopyDossier.addEventListener("click", () => {
    if (currentEvaluationData && currentEvaluationData.dossier_markdown) {
      navigator.clipboard.writeText(currentEvaluationData.dossier_markdown);
      const originalText = btnCopyDossier.textContent;
      btnCopyDossier.textContent = "Copied";
      setTimeout(() => {
        btnCopyDossier.textContent = originalText;
      }, 1500);
    }
  });

  // Form Submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    btnSubmit.disabled = true;
    btnSubmit.textContent = "Evaluating Workflow...";

    resetPipelineSteps();
    setStepState("step1", "active");

    const timer1 = setTimeout(() => { setStepState("step1", "done"); setStepState("step2", "active"); }, 800);
    const timer2 = setTimeout(() => { setStepState("step2", "done"); setStepState("step3", "active"); }, 1800);
    const timer3 = setTimeout(() => { setStepState("step3", "done"); setStepState("step4", "active"); }, 3000);

    try {
      const response = await fetch("/api/evaluate", {
        method: "POST",
        body: formData
      });

      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Evaluation request failed");
      }

      const data = await response.json();
      currentEvaluationData = data;

      for (let i = 1; i <= 5; i++) {
        setStepState(`step${i}`, "done");
      }

      renderResults(data);
    } catch (err) {
      alert(`Workflow Error: ${err.message}`);
      resetPipelineSteps();
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        Execute LangGraph Workflow
      `;
    }
  });
});

function resetPipelineSteps() {
  for (let i = 1; i <= 5; i++) {
    const el = document.getElementById(`step${i}`);
    if (el) el.className = "pipeline-step";
  }
}

function setStepState(stepId, state) {
  const el = document.getElementById(stepId);
  if (!el) return;
  el.className = `pipeline-step ${state}`;
}

function renderResults(data) {
  const emptyState = document.getElementById("emptyState");
  const resultsContent = document.getElementById("resultsContent");
  const btnCopyDossier = document.getElementById("btnCopyDossier");

  emptyState.style.display = "none";
  resultsContent.style.display = "flex";
  btnCopyDossier.style.display = "inline-flex";

  const metrics = data.metrics || {};
  const score = metrics.overall_score || 0;

  // Score Number
  const scoreValEl = document.getElementById("scoreValue");
  scoreValEl.textContent = `${score}%`;

  // Recommendation & Summary
  document.getElementById("recBanner").textContent = `Recommendation: ${metrics.recommendation || "Review Required"}`;
  document.getElementById("candidateSummaryText").textContent = data.candidate_summary || "";

  // Tag pills (muted pastels)
  const matchedRow = document.getElementById("matchedSkillsRow");
  matchedRow.innerHTML = "";
  (metrics.matched_skills || []).forEach(skill => {
    const span = document.createElement("span");
    span.className = "tag-pill tag-matched";
    span.textContent = skill;
    matchedRow.appendChild(span);
  });
  if (!metrics.matched_skills || metrics.matched_skills.length === 0) {
    matchedRow.innerHTML = "<span style='font-size:0.75rem;color:var(--text-subtle);'>None explicit</span>";
  }

  const missingRow = document.getElementById("missingSkillsRow");
  missingRow.innerHTML = "";
  (metrics.missing_skills || []).forEach(skill => {
    const span = document.createElement("span");
    span.className = "tag-pill tag-missing";
    span.textContent = skill;
    missingRow.appendChild(span);
  });
  if (!metrics.missing_skills || metrics.missing_skills.length === 0) {
    missingRow.innerHTML = "<span class='tag-pill tag-matched'>Full Coverage</span>";
  }

  renderActiveRoundQuestions();
}

function renderActiveRoundQuestions() {
  if (!currentEvaluationData || !currentEvaluationData.rounds) return;

  const container = document.getElementById("questionsContainer");
  container.innerHTML = "";

  const roundMap = {
    "round1": "round1_screening",
    "round2": "round2_technical",
    "round3": "round3_system_design",
    "round4": "round4_behavioral"
  };

  const questions = currentEvaluationData.rounds[roundMap[activeRoundKey]] || [];

  if (questions.length === 0) {
    container.innerHTML = "<div style='color:var(--text-muted);font-size:0.85rem;padding:12px;'>No questions generated for this round.</div>";
    return;
  }

  questions.forEach((q, idx) => {
    const box = document.createElement("div");
    box.className = "question-box";

    box.innerHTML = `
      <div class="q-header">
        <span class="q-title">Q${idx + 1}: ${escapeHtml(q.question)}</span>
        <span class="q-focus">${escapeHtml(q.focus || "Core")}</span>
      </div>
      <div class="q-rubric">
        <strong>Evaluation Rubric:</strong> ${escapeHtml(q.rubric || "Evaluate clarity, depth, and practical reasoning.")}
      </div>
    `;

    container.appendChild(box);
  });
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
