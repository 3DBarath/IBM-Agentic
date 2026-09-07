// Instant reactive controller adhering to minimalist-ui and modern web guidelines
let currentEvaluationData = null;
let activeRoundKey = "round1";

const BARATH_JD = `Role: Full-Stack Android & Distributed Backend Systems Engineer
Requirements:
- Strong hands-on proficiency in Kotlin, Kotlin Multiplatform (KMP), and modern Android (Jetpack Compose, Clean Architecture, Hilt, Coroutines).
- Experience building high-performance backends with Spring Boot, Spring Security, PostgreSQL, and Flyway.
- Deep understanding of distributed state transitions, atomic locks (e.g. ShedLock), in-memory caching (Caffeine), and rate limiting (Bucket4j).
- Proven ability to design custom networking protocols (TCP/binary streaming, parallel sockets, mDNS discovery).
- Solid DevOps foundation: Linux, Docker, Bash scripting, GitHub Actions CI/CD pipelines, and multi-platform packaging (.deb, .aab, .msi).`;

const BARATH_RESUME = `BARATH B
Android Engineer · Kotlin Multiplatform · Full-Stack Backend
barathjack77@gmail.com · Trichy · github.com/3DBarath · linkedin.com/in/3dbarath

SUMMARY
Built and shipped 3 production apps — Android, Desktop, and backend — as a solo engineer still in college. Specializes in Kotlin Multiplatform and full-stack Android systems, from custom TCP protocols to distributed Spring Boot backends serving 1,200 daily users.

EDUCATION
B.E Computer Science Engineering (Expected 2027)
Government College of Engineering Srirangam, Trichy · CGPA: 7.6
Relevant coursework: Operating Systems, Data Structures, Algorithms, DPCO

SKILLS
Mobile: Jetpack Compose · MVVM/MVI · Clean Architecture · Hilt/Dagger · Coroutines & Flow · Room · Retrofit · DataStore · KMP · Compose Multiplatform · Firebase
Backend: Spring Boot 3.5 · Spring Security · PostgreSQL · Flyway · JPA/Hibernate · JWT · ShedLock · Bucket4j · Caffeine Cache · Docker
DevOps & Tooling: Git · Fastlane · GitHub Actions · AUR packaging · Bash · SQLite · jarsigner · ADB
Languages: Kotlin · C++ · Python

PROJECTS
1. GCES Hostel Management System (Android · Spring Boot · PostgreSQL · Firebase | Jan 2026 – Mar 2026)
- End-to-end institutional app serving 1,200 DAU on Google Play Store.
- Multi-module Clean Architecture (:app Android, :server Spring Boot, :common shared DTOs) with Hilt DI.
- Predictive meal engine; ShedLock distributed JDBC locks guarantee atomic midnight state transitions across server instances — zero race conditions at scale.
- Caffeine in-memory cache + Bucket4j token-bucket rate limiting absorb rush-hour bursts, holding API response under sub-100ms at peak load.
- JWT stateless auth + Spring Security; PostgreSQL with Flyway versioned migrations; deployed on Render and HuggingFace Spaces (Docker).

2. ConnectLnx (Kotlin Multiplatform · Compose Multiplatform · mDNS · ML Kit | Dec 2025 – Jan 2026)
- Ships to Android, Linux, and Windows from a single codebase with no cloud, no account, no limits.
- Custom binary TCP protocol with parallel multi-socket streaming — files chunked across up to 5 concurrent connections for maximum LAN throughput.
- Zero-config discovery via mDNS on Android (NsdManager) and Desktop (jmDNS); QR code pairing as network-restriction fallback.
- Single codebase → 4 distribution targets: Play Store (.aab), Linux (.deb), Windows (.msi via GitHub Actions), AUR (connectlnx-bin).

3. Aztrox Release (Bash · SQLite · Fastlane · GitHub Actions · jarsigner · gh CLI | Apr 2026)
- Custom CI/CD engine managing 3 live projects across 6 distribution targets.
- Unified CLI handling build → sign → distribute lifecycle across Google Play, GitHub Releases, AUR, Render, HuggingFace Spaces, and Firebase.
- LIFO atomic rollback registry — pipeline failures auto-revert version bumps, gradle.properties, and git tags without manual intervention.
- Preflight health system validates dependencies, keystore passwords, .env vars; releases logged to SQLite with auto-generated HTML audit reports.`;

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
  function loadBarathPreset() {
    document.getElementById("candidateName").value = "Barath B";
    document.getElementById("targetRole").value = "Full-Stack Android & Backend Systems Engineer";
    document.getElementById("jobDescription").value = BARATH_JD;
    document.getElementById("resumeText").value = BARATH_RESUME;
    fileInput.value = "";
    dropText.innerHTML = "<strong>Select PDF file</strong> or drag & drop resume";
  }

  document.getElementById("btnPrefillFullstack").addEventListener("click", loadBarathPreset);

  // Auto-populate with Barath B on initial page load
  loadBarathPreset();

  document.getElementById("btnPrefillJunior").addEventListener("click", () => {
    document.getElementById("candidateName").value = "Priya Sharma";
    document.getElementById("targetRole").value = "Junior Python Developer";
    document.getElementById("jobDescription").value = SAMPLE_JUNIOR_JD;
    document.getElementById("resumeText").value = SAMPLE_JUNIOR_RESUME;
    dropText.innerHTML = "<strong>Select PDF file</strong> or drag & drop resume";
  });

  function clearForm() {
    document.getElementById("candidateName").value = "";
    document.getElementById("targetRole").value = "";
    document.getElementById("jobDescription").value = "";
    document.getElementById("resumeText").value = "";
    fileInput.value = "";
    dropText.innerHTML = "<strong>Select PDF file</strong> or drag & drop resume";
    document.getElementById("candidateName").focus();
  }

  const btnClearForm = document.getElementById("btnClearForm");
  if (btnClearForm) {
    btnClearForm.addEventListener("click", clearForm);
  }

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

    // Trigger smooth layout morph: expand from center to dual pane
    const appContainer = document.getElementById("appContainer");
    if (appContainer && appContainer.classList.contains("state-initial")) {
      appContainer.classList.remove("state-initial");
      appContainer.classList.add("state-evaluated");
    }

    // Animate Pipeline tracker
    resetPipelineSteps();
    setStepState("step1", "active");

    const badge = document.getElementById("pipelineStatusBadge");
    if (badge) badge.textContent = "Running";

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

      if (badge) badge.textContent = "Completed";

      renderResults(data);
    } catch (err) {
      alert(`Workflow Error: ${err.message}`);
      resetPipelineSteps();
      if (badge) badge.textContent = "Failed";
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

  if (emptyState) emptyState.style.display = "none";
  if (resultsContent) resultsContent.style.display = "flex";
  if (btnCopyDossier) btnCopyDossier.style.display = "inline-flex";

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
