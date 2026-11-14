/**
 * GapWise - AI-Powered Learning Platform & Adaptive Career Navigator
 * Core Client Application Controller & State Store
 */

const STATE = {
  activeTab: 'dashboard',
  user: null,
  roadmap: null,
  selectedCourse: null,
  currentTestQuestion: null,
  selectedTestOption: null,
  currentInterviewQuestion: null,
  connectors: {},
  activeOAuthFlow: null,
  sandboxLanguage: 'python'
};

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', async () => {
  await fetchUserData();
  await refreshActiveTab();
  initCodeSandboxDefault();
});

async function apiCall(endpoint, method = 'GET', data = null) {
  try {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' }
    };
    if (data) opts.body = JSON.stringify(data);
    const res = await fetch(endpoint, opts);
    return await res.json();
  } catch (err) {
    console.error(`API Call failed on ${endpoint}:`, err);
    return { error: err.message };
  }
}

async function fetchUserData() {
  const user = await apiCall('/api/user');
  if (user && !user.error) {
    STATE.user = user;
    renderHeaderProfile(user);
  }
}

function renderHeaderProfile(user) {
  document.getElementById('header-streak').textContent = `${user.streak_days || 1} Days`;
  document.getElementById('header-xp').textContent = `${(user.xp || 0).toLocaleString()} XP`;
  
  const initials = user.name.split(' ').map(n => n[0]).join('').substring(0, 2);
  document.getElementById('header-avatar').textContent = initials;
  
  const select = document.getElementById('user-select');
  if (select) select.value = user.id;
}

// --- USER SWITCHER ---
async function switchUser(userId) {
  const res = await apiCall('/api/user/switch', 'POST', { user_id: userId });
  if (res && res.success) {
    STATE.user = res.active_user;
    renderHeaderProfile(STATE.user);
    await refreshActiveTab();
  }
}

// --- NAVIGATION & TABS ---
function setTab(tabName) {
  STATE.activeTab = tabName;
  document.querySelectorAll('.nav-tab').forEach(t => {
    t.classList.toggle('active', t.getAttribute('data-tab') === tabName);
  });
  document.querySelectorAll('.tab-pane').forEach(p => {
    p.classList.toggle('active', p.id === `tab-${tabName}`);
  });
  refreshActiveTab();
}

async function refreshActiveTab() {
  switch (STATE.activeTab) {
    case 'dashboard':
      await renderDashboard();
      break;
    case 'roadmap':
      await renderRoadmap();
      break;
    case 'skills':
      await renderSkillsAndPivot();
      break;
    case 'tests':
      await loadNextQuestion();
      break;
    case 'interview':
      await renderInterviewArena();
      break;
    case 'mentor':
      await renderMentorChat();
      break;
    case 'connectors':
      await renderConnectors();
      break;
    case 'analytics':
      await renderAnalyticsHub();
      break;
  }
}

// ==========================================
// 1. DASHBOARD COMPONENT
// ==========================================
async function renderDashboard() {
  const [matchData, confData, twinData, gamifyData] = await Promise.all([
    apiCall('/api/career_match'),
    apiCall('/api/confidence_meter'),
    apiCall('/api/learning_twin'),
    apiCall('/api/gamification')
  ]);

  // Career Banner
  if (matchData && !matchData.error) {
    document.getElementById('dash-user-type').textContent = `${(STATE.user.user_type || 'student').toUpperCase()} PROFILE`;
    document.getElementById('dash-target-role').textContent = matchData.target_role;
    document.getElementById('dash-role-desc').textContent = matchData.description;
    document.getElementById('dash-salary').textContent = matchData.salary_range || '$110k+';
    document.getElementById('dash-growth').textContent = matchData.demand_growth || '+20% YoY';
    document.getElementById('dash-weeks').textContent = `${matchData.estimated_weeks_to_ready} Weeks`;

    const matchPct = Math.round(matchData.match_percent);
    document.getElementById('dash-match-percent').textContent = `${matchPct}%`;
    document.getElementById('dash-gauge-fill').setAttribute('stroke-dasharray', `${matchPct}, 100`);

    // Missing skills alert
    const missing = matchData.missing_skills || [];
    const missingTags = missing.map(m => `<span class="tag-missing">${m.skill}</span>`).join(' ');
    document.getElementById('dash-gap-explanation').innerHTML = 
      `Your verified strengths give you a solid baseline. To reach full readiness for <strong>${matchData.target_role}</strong>, priority gaps are: ${missingTags || 'None! You are job ready.'}`;
  }

  // Confidence Meter
  if (Array.isArray(confData)) {
    const list = document.getElementById('confidence-meter-list');
    list.innerHTML = confData.slice(0, 5).map(item => {
      let flagHtml = '';
      if (item.flag === 'DUNNING_KRUGER_RISK') {
        flagHtml = `<div class="cm-flag-banner cm-flag-warning">⚠️ Overconfidence Warning: Self-rating exceeds test score by ${Math.round(item.discrepancy)}%</div>`;
      } else if (item.flag === 'IMPOSTER_SYNDROME') {
        flagHtml = `<div class="cm-flag-banner cm-flag-boost">✨ Imposter Syndrome Detected: You tested ${Math.abs(Math.round(item.discrepancy))}% higher than your self-rating!</div>`;
      } else if (item.flag === 'CALIBRATED') {
        flagHtml = `<div class="cm-flag-banner cm-flag-success">✓ Well Calibrated: Self-perception matches test performance</div>`;
      }

      return `
        <div class="cm-item">
          <div class="cm-header">
            <span class="cm-skill-name">${item.skill}</span>
            <small class="text-muted">Self: ${Math.round(item.self_rating)}% | Assessed: ${Math.round(item.assessed_rating)}%</small>
          </div>
          <div class="cm-bars">
            <div class="cm-bar-row">
              <span class="cm-bar-label">Self-Rated:</span>
              <div class="cm-progress-track">
                <div class="cm-fill-self" style="width: ${item.self_rating}%;"></div>
              </div>
            </div>
            <div class="cm-bar-row">
              <span class="cm-bar-label">Assessed:</span>
              <div class="cm-progress-track">
                <div class="cm-fill-assessed" style="width: ${item.assessed_rating}%;"></div>
              </div>
            </div>
          </div>
          ${flagHtml}
        </div>
      `;
    }).join('');
  }

  // Learning Twin
  if (twinData && !twinData.error) {
    document.getElementById('twin-velocity').textContent = `${twinData.study_velocity_xp_per_day} XP/day`;
    document.getElementById('twin-retention').textContent = `${Math.round(twinData.retention_stability_factor * 100)}% Stability`;
    document.getElementById('twin-peak').textContent = twinData.peak_focus_hours;
    document.getElementById('twin-predicted').textContent = `In ${twinData.predicted_weeks_remaining} Weeks`;
    document.getElementById('twin-modality').textContent = twinData.preferred_format;
  }

  // Quests
  if (gamifyData && gamifyData.quests) {
    document.getElementById('level-title-badge').textContent = gamifyData.level_info.title;
    const questsList = document.getElementById('quests-container');
    questsList.innerHTML = gamifyData.quests.map(q => `
      <div class="quest-item">
        <div class="quest-left">
          <span class="quest-icon">${q.completed ? '✅' : '🎯'}</span>
          <div>
            <div class="quest-title">${q.title}</div>
            <div class="quest-desc">${q.description}</div>
          </div>
        </div>
        <span class="badge-xp text-accent">+${q.xp_reward} XP</span>
      </div>
    `).join('');
  }
}

// ==========================================
// 2. ROADMAP & VISUAL DAG
// ==========================================
async function renderRoadmap() {
  const roadmap = await apiCall('/api/roadmap');
  if (!roadmap || roadmap.error) return;
  STATE.roadmap = roadmap;

  const container = document.getElementById('dag-container');
  container.innerHTML = '';

  // Group nodes into tiers (Foundational -> Intermediate -> Capstone)
  const tiers = {
    'Foundations & Core': [],
    'Advanced Architecture': [],
    'Capstone & Production': []
  };

  roadmap.nodes.forEach(node => {
    if (node.difficulty === 'Foundational' || node.prerequisites.length <= 1) {
      tiers['Foundations & Core'].push(node);
    } else if (node.unlocks && node.unlocks.length === 0) {
      tiers['Capstone & Production'].push(node);
    } else {
      tiers['Advanced Architecture'].push(node);
    }
  });

  for (const [tierName, nodes] of Object.entries(tiers)) {
    if (nodes.length === 0) continue;

    const tierRow = document.createElement('div');
    tierRow.className = 'dag-tier-row';

    nodes.forEach(node => {
      const nodeEl = document.createElement('div');
      nodeEl.className = `dag-node node-${node.status.toLowerCase()}`;
      
      let statusIcon = '🔓';
      let statusBadge = '<span class="text-accent">UNLOCKED</span>';
      if (node.status === 'COMPLETED') {
        statusIcon = '✅';
        statusBadge = '<span class="text-success">COMPLETED</span>';
      } else if (node.status === 'LOCKED') {
        statusIcon = '🔒';
        statusBadge = '<span class="text-muted">LOCKED</span>';
      }

      nodeEl.innerHTML = `
        <div class="node-status-bar">
          <span>${statusIcon} ${node.category}</span>
          ${statusBadge}
        </div>
        <div class="node-title">${node.title}</div>
        <div class="node-meta">
          <span>⏱ ${node.duration_hours}h</span>
          <span class="text-accent">+${node.xp_reward} XP</span>
        </div>
      `;

      nodeEl.onclick = () => openCourseDrawer(node);
      tierRow.appendChild(nodeEl);
    });

    container.appendChild(tierRow);
  }
}

function openCourseDrawer(node) {
  STATE.selectedCourse = node;
  document.getElementById('drawer-category').textContent = node.category.toUpperCase();
  document.getElementById('drawer-title').textContent = node.title;
  document.getElementById('drawer-why').textContent = node.why_this_pick;
  document.getElementById('drawer-provider').textContent = node.provider;
  document.getElementById('drawer-duration').textContent = `${node.duration_hours} Hours`;
  document.getElementById('drawer-difficulty').textContent = node.difficulty;
  document.getElementById('drawer-xp').textContent = `+${node.xp_reward} XP`;
  document.getElementById('drawer-exercise').textContent = node.practical_exercise;

  const btn = document.getElementById('drawer-action-btn');
  if (node.status === 'COMPLETED') {
    btn.textContent = '✓ Module Already Completed';
    btn.disabled = true;
    btn.className = 'btn btn-secondary';
  } else if (node.status === 'LOCKED') {
    btn.textContent = `🔒 Prerequisite Required: ${node.missing_prerequisites.join(', ')}`;
    btn.disabled = true;
    btn.className = 'btn btn-secondary';
  } else {
    btn.textContent = 'Mark Module Completed & Unlock Next (+350 XP)';
    btn.disabled = false;
    btn.className = 'btn btn-primary';
  }

  document.getElementById('course-detail-drawer').classList.remove('hidden');
}

function closeDrawer() {
  document.getElementById('course-detail-drawer').classList.add('hidden');
}

async function markCurrentCourseCompleted() {
  if (!STATE.selectedCourse) return;
  const res = await apiCall('/api/roadmap/complete_course', 'POST', { course_id: STATE.selectedCourse.id });
  if (res && res.success) {
    closeDrawer();
    await fetchUserData();
    await renderRoadmap();
  }
}

// ==========================================
// 3. SKILL ANALYSIS & CAREER PIVOT
// ==========================================
async function renderSkillsAndPivot() {
  const analysis = await apiCall('/api/skill_analysis');
  if (analysis && analysis.all_skills) {
    const list = document.getElementById('skills-editor-list');
    list.innerHTML = analysis.all_skills.map(s => {
      const stars = [1, 2, 3, 4, 5].map(star => `
        <span onclick="setSkillRating('${s.skill}', ${star})">${star <= s.self_rating_stars ? '★' : '☆'}</span>
      `).join('');

      return `
        <div class="skill-edit-row">
          <div>
            <strong>${s.skill}</strong>
            <small class="text-muted" style="display:block;">Assessed Score: ${s.assessed_rating}% ${s.verified ? '• <span class="text-success">Verified</span>' : ''}</small>
          </div>
          <div class="skill-stars" title="Click to self-rate">${stars}</div>
        </div>
      `;
    }).join('');
  }

  // Pre-run pivot simulator
  const select = document.getElementById('pivot-role-select');
  if (select) runCareerPivot(select.value);
}

async function setSkillRating(skill, rating) {
  const res = await apiCall('/api/user/skill_rate', 'POST', { skill, rating });
  if (res && res.success) {
    await renderSkillsAndPivot();
  }
}

async function runCareerPivot(targetRole) {
  const res = await apiCall('/api/career_pivot', 'POST', { new_role: targetRole });
  if (!res || res.error) return;

  const container = document.getElementById('pivot-results-container');
  const transferred = res.transferred_skills.map(s => `
    <div class="cm-bar-row">
      <span style="width: 140px;">${s.skill}</span>
      <div class="cm-progress-track">
        <div class="cm-fill-assessed" style="width: ${s.current_score}%;"></div>
      </div>
      <span class="text-success" style="font-size: 0.75rem;">${s.current_score}% (${s.transfer_efficiency} TRANSFER)</span>
    </div>
  `).join('');

  const newNeeded = res.new_skills_needed.map(s => `
    <span class="tag-missing" style="margin-right: 0.4rem; margin-bottom: 0.4rem; display: inline-block;">+ ${s.skill}</span>
  `).join('');

  container.innerHTML = `
    <div class="pivot-diff-box">
      <div class="pivot-summary-pills">
        <div class="pill-stat">Skill Overlap: <strong class="text-accent">${res.overlap_percent}%</strong></div>
        <div class="pill-stat">Pivot Viability: <strong class="text-success">${res.pivot_viability}</strong></div>
        <div class="pill-stat">Market Salary: <strong>${res.new_salary_range}</strong></div>
      </div>

      <div>
        <h4 style="font-size: 0.85rem; margin-bottom: 0.5rem;">Transferred Competencies (Carried Over):</h4>
        <div class="confidence-list">${transferred || '<p class="text-muted">None</p>'}</div>
      </div>

      <div style="margin-top: 0.75rem;">
        <h4 style="font-size: 0.85rem; margin-bottom: 0.5rem;">New Skills Required for ${res.new_role}:</h4>
        <div>${newNeeded}</div>
      </div>

      <button class="btn btn-primary btn-sm" style="margin-top: 1rem;" onclick="applyCareerPivot('${res.new_role}')">
        Apply ${res.new_role} as Active Target Goal
      </button>
    </div>
  `;
}

async function applyCareerPivot(newRole) {
  const res = await apiCall('/api/career_pivot/apply', 'POST', { new_role: newRole });
  if (res && res.success) {
    alert(`Career target successfully updated to ${newRole}! Roadmaps and matching have been dynamically adapted.`);
    await fetchUserData();
    setTab('dashboard');
  }
}

// ==========================================
// 4. ADAPTIVE TESTS & LIVE CODE SANDBOX
// ==========================================
async function loadNextQuestion() {
  const data = await apiCall('/api/test/next');
  if (!data || data.error) return;

  STATE.currentTestQuestion = data.question;
  STATE.selectedTestOption = null;

  document.getElementById('test-difficulty-chip').textContent = `DIFFICULTY: LEVEL ${data.target_difficulty}`;
  document.getElementById('test-theta-badge').textContent = `Ability θ: ${data.current_theta >= 0 ? '+' : ''}${data.current_theta}`;
  document.getElementById('test-topic-title').textContent = `${data.question.skill} • ${data.question.topic}`;
  document.getElementById('test-question-text').textContent = data.question.question;

  const codeSnippet = document.getElementById('test-code-snippet');
  if (data.question.code_snippet) {
    codeSnippet.querySelector('code').textContent = data.question.code_snippet;
    codeSnippet.classList.remove('hidden');
  } else {
    codeSnippet.classList.add('hidden');
  }

  // Scaffolding hint for slow learners
  const scaffoldBox = document.getElementById('test-scaffolding-box');
  if (data.show_scaffolding && data.scaffolding_hint) {
    document.getElementById('test-hint-text').textContent = data.scaffolding_hint;
    scaffoldBox.classList.remove('hidden');
  } else {
    scaffoldBox.classList.add('hidden');
  }

  // Render options
  const optsContainer = document.getElementById('test-options-container');
  optsContainer.innerHTML = data.question.options.map((opt, idx) => `
    <button class="test-option-btn" id="opt-btn-${idx}" onclick="selectTestOption(${idx})">${opt}</button>
  `).join('');

  document.getElementById('btn-submit-answer').classList.remove('hidden');
  document.getElementById('btn-next-question').classList.add('hidden');
  document.getElementById('test-feedback-box').classList.add('hidden');
}

function selectTestOption(idx) {
  STATE.selectedTestOption = idx;
  document.querySelectorAll('.test-option-btn').forEach((btn, i) => {
    btn.classList.toggle('selected', i === idx);
  });
}

async function submitTestAnswer() {
  if (STATE.selectedTestOption === null) {
    alert('Please select an answer first.');
    return;
  }

  const q = STATE.currentTestQuestion;
  const res = await apiCall('/api/test/submit', 'POST', {
    question_id: q.id,
    answer: STATE.selectedTestOption
  });

  if (!res || res.error) return;

  const fbBox = document.getElementById('test-feedback-box');
  fbBox.classList.remove('hidden');
  if (res.is_correct) {
    fbBox.className = 'feedback-box feedback-correct';
    fbBox.innerHTML = `<strong>✓ Correct! (+${res.xp_awarded} XP)</strong><p>${res.explanation}</p><small>Ability rating adjusted from θ ${res.previous_theta} → ${res.new_theta}</small>`;
  } else {
    fbBox.className = 'feedback-box feedback-wrong';
    fbBox.innerHTML = `<strong>✕ Incorrect</strong><p>${res.explanation}</p><small>Ability rating adjusted from θ ${res.previous_theta} → ${res.new_theta}</small>`;
  }

  document.getElementById('btn-submit-answer').classList.add('hidden');
  document.getElementById('btn-next-question').classList.remove('hidden');
  await fetchUserData();
}

function initCodeSandboxDefault() {
  const pyDefault = (
    "# Python 3 Code Sandbox - Live Execution Engine\n"
    "def calculate_event_loop_throughput(tasks, worker_threads):\n"
    "    return sum(tasks) / max(1, worker_threads)\n\n"
    "throughput = calculate_event_loop_throughput([120, 80, 200, 150], 4)\n"
    "print(f'Computed Worker Throughput: {throughput:.2f} ops/sec')\n"
  );
  const editor = document.getElementById('sandbox-code-editor');
  if (editor && !editor.value) {
    editor.value = pyDefault;
  }
}

function setSandboxLang(lang) {
  STATE.sandboxLanguage = lang;
  document.querySelectorAll('.btn-lang').forEach(b => {
    b.classList.toggle('active', b.textContent.toLowerCase().includes(lang));
  });

  const editor = document.getElementById('sandbox-code-editor');
  if (lang === 'python') {
    initCodeSandboxDefault();
  } else {
    editor.value = (
      "// JavaScript (ES6) Sandbox\n"
      "const fibonacci = (n) => n <= 1 ? n : fibonacci(n - 1) + fibonacci(n - 2);\n"
      "console.log('Fibonacci sequence term 8:', fibonacci(8));\n"
    );
  }
}

async function runSandboxCode() {
  const code = document.getElementById('sandbox-code-editor').value;
  const term = document.getElementById('sandbox-terminal-out');
  term.textContent = 'Running test execution pipeline...';

  const res = await apiCall('/api/test/code_sandbox', 'POST', {
    language: STATE.sandboxLanguage,
    code
  });

  if (res && res.success) {
    const tests = (res.test_results || []).map(t => `  ✓ ${t.test_name}: ${t.detail}`).join('\n');
    term.textContent = `[STDOUT]\n${res.output}\n\n[TEST HARNESS ASSIGNMENT - ${res.execution_time_ms}ms]\n${tests}\n\n✓ All assertions passed. +${res.xp_earned || 60} XP awarded!`;
    await fetchUserData();
  } else {
    term.textContent = `[EXECUTION ERROR]\n${res.error || 'Syntax or runtime evaluation failed.'}`;
  }
}

async function loadMicroQuizCode() {
  const quiz = await apiCall('/api/test/micro_quiz');
  if (quiz && quiz.code_template) {
    const editor = document.getElementById('sandbox-code-editor');
    editor.value = quiz.code_template;
    const term = document.getElementById('sandbox-terminal-out');
    term.textContent = `[MICRO-QUIZ IN CODE ACTIVATED]\nQuestion: ${quiz.challenge_question}\nHint: ${quiz.hint}\n\nInspect the code editor and fix the commented hook.`;
  }
}

// ==========================================
// 5. MOCK INTERVIEW AGENT
// ==========================================
async function renderInterviewArena() {
  const data = await apiCall('/api/mock_interview');
  if (!data || !data.questions) return;

  const q = data.questions[0];
  STATE.currentInterviewQuestion = q;

  document.getElementById('interview-role-label').textContent = data.target_role;
  document.getElementById('interview-q-category').textContent = q.category;
  document.getElementById('interview-q-text').textContent = `"${q.question}"`;
}

function fillSampleInterviewAnswer() {
  if (STATE.currentInterviewQuestion && STATE.currentInterviewQuestion.sample_good_answer) {
    document.getElementById('interview-answer-input').value = STATE.currentInterviewQuestion.sample_good_answer;
  }
}

async function submitInterviewAnswer() {
  const answer = document.getElementById('interview-answer-input').value;
  if (!answer.trim()) {
    alert('Please enter your response before submitting.');
    return;
  }

  const q = STATE.currentInterviewQuestion;
  const res = await apiCall('/api/mock_interview/submit', 'POST', {
    question_id: q.id,
    answer
  });

  if (!res || res.error) return;

  const panel = document.getElementById('interview-results-panel');
  panel.classList.remove('hidden');

  const rb = res.rubric_breakdown;
  panel.innerHTML = `
    <div class="card" style="margin-top: 1rem; border-color: var(--accent-purple);">
      <div class="card-header">
        <div>
          <h3 class="card-title">Interview Rubric Evaluation</h3>
          <p class="card-sub">AI Scored Performance Across 4 Core Engineering Dimensions</p>
        </div>
        <div style="font-size: 1.5rem; font-weight: 800; color: var(--accent-cyan);">${res.composite_score}/100</div>
      </div>

      <div class="rubric-grid">
        <div class="rubric-score-box">
          <div class="rsb-num">${rb.technical_depth}%</div>
          <div class="rsb-label">Technical Depth</div>
        </div>
        <div class="rubric-score-box">
          <div class="rsb-num">${rb.clarity}%</div>
          <div class="rsb-label">Clarity</div>
        </div>
        <div class="rubric-score-box">
          <div class="rsb-num">${rb.problem_solving}%</div>
          <div class="rsb-label">Problem Solving</div>
        </div>
        <div class="rubric-score-box">
          <div class="rsb-num">${rb.communication}%</div>
          <div class="rsb-label">Communication</div>
        </div>
      </div>

      <div style="margin-top: 1rem;">
        <strong class="text-success">Strengths:</strong>
        <ul style="margin: 0.4rem 0 0.8rem 1.25rem; font-size: 0.85rem;">
          ${res.strengths.map(s => `<li>${s}</li>`).join('')}
        </ul>
        <strong class="text-accent">Areas for Polish:</strong>
        <ul style="margin: 0.4rem 0 0.8rem 1.25rem; font-size: 0.85rem;">
          ${res.improvements.map(i => `<li>${i}</li>`).join('')}
        </ul>
      </div>
      <div style="text-align: right; font-weight: 700; color: var(--accent-emerald);">+${res.xp_earned} XP Awarded</div>
    </div>
  `;
  await fetchUserData();
}

// ==========================================
// 6. AI MENTOR & CHECK-IN
// ==========================================
async function renderMentorChat() {
  const container = document.getElementById('chat-messages-container');
  if (!container.innerHTML.trim()) {
    container.innerHTML = `
      <div class="chat-msg msg-mentor">
        <strong>Ada • AI Mentor:</strong>
        <p>Welcome back, ${STATE.user ? STATE.user.name : 'Learner'}! I'm monitoring your skill gaps for <strong>${STATE.user ? STATE.user.target_role : 'Engineering'}</strong>. How can I assist you with your roadmap, code exercises, or study schedule today?</p>
      </div>
    `;
  }
}

async function sendMentorMessage(e) {
  e.preventDefault();
  const input = document.getElementById('chat-user-input');
  const msg = input.value.trim();
  if (!msg) return;

  const container = document.getElementById('chat-messages-container');
  container.innerHTML += `
    <div class="chat-msg msg-user" style="text-align: right; margin: 0.5rem 0;">
      <span style="background: rgba(99, 102, 241, 0.2); padding: 0.5rem 1rem; border-radius: 12px; display: inline-block;">
        ${msg}
      </span>
    </div>
  `;
  input.value = '';

  const res = await apiCall('/api/ai_mentor/chat', 'POST', { message: msg });
  if (res && res.reply) {
    container.innerHTML += `
      <div class="chat-msg msg-mentor" style="margin: 0.5rem 0;">
        <strong>Ada • AI Mentor:</strong>
        <p>${res.reply}</p>
        ${res.action_suggestion ? `<small class="text-accent" style="cursor: pointer;" onclick="alert('Navigating to suggested action: ${res.action_suggestion}')">👉 Suggested Action: ${res.action_suggestion}</small>` : ''}
      </div>
    `;
    container.scrollTop = container.scrollHeight;
  }
}

// Weekly Check-in Modal
function openCheckinModal() {
  document.getElementById('modal-checkin').classList.remove('hidden');
}
function closeCheckinModal() {
  document.getElementById('modal-checkin').classList.add('hidden');
}

async function submitWeeklyCheckin() {
  const hours = parseInt(document.getElementById('checkin-hours').value) || 10;
  const struggle = document.getElementById('checkin-struggle').value;
  const goalShifted = document.querySelector('input[name="checkin-goal"]:checked').value === 'yes';

  const res = await apiCall('/api/ai_mentor/weekly_checkin', 'POST', {
    hours_spent: hours,
    struggle_area: struggle,
    goal_shifted: goalShifted
  });

  closeCheckinModal();
  if (res && res.plan_adjustments) {
    alert(`Weekly Check-in Complete (+100 XP)!\n\nPlan Adjustments:\n${res.plan_adjustments.map(a => `• ${a}`).join('\n')}`);
    await fetchUserData();
    await renderDashboard();
  }
}

// Explain-Back Mode (Feynman Technique)
function fillSampleExplanation() {
  const concept = document.getElementById('feynman-concept-select').value;
  if (concept.includes('Event Loop')) {
    document.getElementById('feynman-text-input').value = 
      "The JavaScript event loop continuously monitors the call stack and message queues. Synchronous execution runs on the single main thread. Asynchronous callbacks like Promises queue into microtasks, while setTimeout goes into macrotasks. The event loop prioritizes draining all microtasks before picking the next macrotask.";
  } else {
    document.getElementById('feynman-text-input').value = 
      "A closure occurs when an inner function retains lexical access to variables declared in its enclosing parent scope, even after the parent function has finished executing.";
  }
}

async function submitExplainBack() {
  const concept = document.getElementById('feynman-concept-select').value;
  const explanation = document.getElementById('feynman-text-input').value;
  if (!explanation.trim()) {
    alert('Please write an explanation first.');
    return;
  }

  const res = await apiCall('/api/ai_mentor/explain_back', 'POST', { concept, explanation });
  if (!res || res.error) return;

  const box = document.getElementById('feynman-feedback-box');
  box.classList.remove('hidden');
  box.innerHTML = `
    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 8px; padding: 1rem; margin-top: 1rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
        <strong>Feynman Evaluation Score: ${res.composite_score}/100</strong>
        <span class="badge-xp text-success">+${res.xp_earned} XP</span>
      </div>
      <p style="font-size: 0.85rem; margin-bottom: 0.5rem;">"${res.feynman_verdict}"</p>
      <div style="display: flex; gap: 1rem; font-size: 0.8rem; color: var(--text-muted);">
        <span>Accuracy: ${res.accuracy_score}%</span>
        <span>Clarity: ${res.clarity_score}%</span>
        <span>Depth: ${res.depth_score}%</span>
      </div>
      ${res.misconceptions_flagged.length ? `
        <div style="margin-top: 0.6rem; color: #fda4af; font-size: 0.8rem;">
          <strong>Misconception Notice:</strong> ${res.misconceptions_flagged.join(', ')}
        </div>
      ` : ''}
    </div>
  `;
  await fetchUserData();
}

// ==========================================
// 7. ACCOUNTS & TOKEN VAULT
// ==========================================
async function renderConnectors() {
  const connectors = await apiCall('/api/connectors');
  if (!connectors || connectors.error) return;
  STATE.connectors = connectors;

  const grid = document.getElementById('connectors-grid');
  grid.innerHTML = Object.values(connectors).map(conn => {
    const isConn = conn.connection_status && conn.connection_status.connected;
    const masked = isConn ? conn.connection_status.masked_token : 'Not Connected';

    return `
      <div class="connector-card">
        <div>
          <div class="cc-header">
            <span class="chip chip-blue" style="font-size: 0.7rem;">${conn.category}</span>
            <span class="badge-status ${isConn ? 'text-success' : 'text-muted'}">
              ${isConn ? '● ACTIVE' : '○ DISCONNECTED'}
            </span>
          </div>
          <h3 class="cc-title" style="margin: 0.5rem 0 0.25rem;">${conn.name}</h3>
          <p class="cc-desc">${conn.description}</p>
        </div>

        <div>
          <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.75rem;">
            Vault Token: <code>${masked}</code>
          </div>
          <div style="display: flex; gap: 0.5rem;">
            ${isConn ? `
              <button class="btn btn-secondary btn-sm" onclick="disconnectProvider('${conn.id}')">Disconnect & Revoke</button>
              <button class="btn btn-ghost btn-sm" onclick="testProxyCall('${conn.id}')">Test Proxy API</button>
            ` : `
              <button class="btn btn-primary btn-sm" onclick="openOAuthConsentModal('${conn.id}')">Connect (PKCE)</button>
              ${conn.supports_pat ? `<button class="btn btn-secondary btn-sm" onclick="openPatModal('${conn.id}')">Paste PAT</button>` : ''}
            `}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

async function openOAuthConsentModal(providerId) {
  const flow = await apiCall('/api/connectors/initiate_oauth', 'POST', { provider_id: providerId });
  if (!flow || flow.error) return;
  STATE.activeOAuthFlow = flow;

  const conn = STATE.connectors[providerId];
  document.getElementById('oauth-modal-title').textContent = `Authorize ${conn.name}`;
  document.getElementById('oauth-modal-state').textContent = flow.state;

  const scopesList = document.getElementById('oauth-scopes-list');
  scopesList.innerHTML = Object.entries(flow.scope_descriptions || {}).map(([scope, desc]) => `
    <div style="margin-bottom: 0.5rem; font-size: 0.8rem;">
      <code class="text-accent">${scope}</code>
      <p style="color: var(--text-secondary); margin-top: 0.15rem;">${desc}</p>
    </div>
  `).join('');

  document.getElementById('pat-input-container').classList.add('hidden');
  document.getElementById('btn-confirm-connect').onclick = () => confirmOAuthConnect(providerId, flow.state);
  document.getElementById('modal-oauth').classList.remove('hidden');
}

function openPatModal(providerId) {
  const conn = STATE.connectors[providerId];
  document.getElementById('oauth-modal-title').textContent = `Paste ${conn.name} Personal Access Token`;
  document.getElementById('oauth-scopes-list').innerHTML = `<p class="text-muted" style="font-size: 0.8rem;">${conn.pat_instruction || 'Enter personal token with read access.'}</p>`;
  document.getElementById('pat-input-container').classList.remove('hidden');
  document.getElementById('btn-confirm-connect').onclick = () => confirmPatConnect(providerId);
  document.getElementById('modal-oauth').classList.remove('hidden');
}

function closeOAuthModal() {
  document.getElementById('modal-oauth').classList.add('hidden');
}

async function confirmOAuthConnect(providerId, state) {
  const res = await apiCall('/api/connectors/callback', 'POST', {
    provider_id: providerId,
    state: state,
    code: 'auth_code_simulated'
  });
  closeOAuthModal();
  if (res && res.connected) {
    alert(`Account connected and token vaulted with AES-256-GCM!\nMasked Token: ${res.masked_token}`);
    await renderConnectors();
  }
}

async function confirmPatConnect(providerId) {
  const pat = document.getElementById('pat-input').value.trim();
  if (!pat) {
    alert('Please enter a personal access token.');
    return;
  }
  const res = await apiCall('/api/connectors/connect_pat', 'POST', {
    provider_id: providerId,
    pat_token: pat
  });
  closeOAuthModal();
  if (res && res.connected) {
    alert(`PAT vaulted securely with AES-256-GCM!`);
    await renderConnectors();
  }
}

async function disconnectProvider(providerId) {
  if (!confirm(`Are you sure you want to disconnect ${providerId}? This will revoke access at the provider and purge your encrypted token from the vault.`)) return;
  const res = await apiCall('/api/connectors/disconnect', 'POST', { provider_id: providerId });
  if (res && res.purged_from_vault) {
    alert(`${providerId} disconnected. Token purged from vault.`);
    await renderConnectors();
  }
}

async function testProxyCall(providerId) {
  const res = await apiCall(`/api/proxy/${providerId}/user`);
  alert(`Server-Side Proxied Response for ${providerId}:\n${JSON.stringify(res, null, 2)}`);
}

function openManualImportModal() {
  document.getElementById('modal-import').classList.remove('hidden');
}
function closeManualImportModal() {
  document.getElementById('modal-import').classList.add('hidden');
}

async function submitManualImport() {
  const provider = document.getElementById('import-provider-select').value;
  const content = document.getElementById('import-content').value;
  if (!content.trim()) {
    alert('Please paste CSV or text content.');
    return;
  }
  const res = await apiCall('/api/connectors/manual_import', 'POST', {
    provider_id: provider,
    filename: `${provider}_manual_import.csv`,
    content: content
  });
  closeManualImportModal();
  if (res && res.records_imported) {
    alert(`Imported ${res.records_imported} credential records into your profile!`);
    await fetchUserData();
  }
}

// ==========================================
// 8. ADVANCED INTELLIGENCE & TWIN
// ==========================================
async function renderAnalyticsHub() {
  const [struggles, decay, peers, passport, heatmap, sched] = await Promise.all([
    apiCall('/api/struggle_detector'),
    apiCall('/api/skill_decay'),
    apiCall('/api/peer_pairing'),
    apiCall('/api/skill_passport'),
    apiCall('/api/cohort_heatmap'),
    apiCall('/api/time_schedule')
  ]);

  // Struggles
  const stContainer = document.getElementById('struggles-container');
  if (struggles && struggles.struggles && struggles.struggles.length > 0) {
    stContainer.innerHTML = struggles.struggles.map(s => `
      <div style="background: rgba(244, 63, 94, 0.08); border-left: 3px solid var(--accent-rose); padding: 0.85rem; border-radius: 6px; margin-bottom: 0.65rem;">
        <strong style="color: #fda4af;">Repeated Gap in: ${s.topic} (${s.repeated_misses} misses)</strong>
        <p style="font-size: 0.8rem; margin: 0.2rem 0; color: var(--text-secondary);">Root Cause: ${s.root_prerequisite}</p>
        <small class="text-accent">${s.remedial_action}</small>
      </div>
    `).join('');
  } else {
    stContainer.innerHTML = `<p class="text-muted" style="font-size: 0.85rem;">No struggle patterns detected across recent assessments. Excellent retention!</p>`;
  }

  // Skill Decay
  if (Array.isArray(decay)) {
    const decayList = document.getElementById('skill-decay-list');
    decayList.innerHTML = decay.map(d => `
      <div class="cm-bar-row" style="margin-bottom: 0.65rem;">
        <span style="width: 110px;">${d.skill}</span>
        <div class="cm-progress-track">
          <div class="cm-fill-assessed" style="width: ${d.retention_percent}%; background: ${d.needs_review ? 'var(--accent-amber)' : 'var(--accent-emerald)'};"></div>
        </div>
        <span style="font-size: 0.75rem; width: 65px;">${d.retention_percent}%</span>
        ${d.needs_review ? `<button class="btn btn-ghost btn-sm" onclick="setTab('tests')">Refresh (2m)</button>` : '<span class="text-success" style="font-size: 0.75rem;">Optimal</span>'}
      </div>
    `).join('');
  }

  // Peer Pairing
  if (Array.isArray(peers)) {
    const peersList = document.getElementById('peer-pairing-list');
    peersList.innerHTML = peers.map(p => `
      <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border-subtle); padding: 0.85rem; border-radius: 8px; margin-bottom: 0.65rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
          <strong>${p.peer_name} (${p.peer_type})</strong>
          <span class="chip chip-blue" style="font-size: 0.7rem;">${p.compatibility_score}% SYNERGY</span>
        </div>
        <div style="font-size: 0.75rem; color: var(--text-secondary);">
          <div>They can mentor you on: <strong class="text-accent">${p.they_teach_you.join(', ')}</strong></div>
          <div>You can mentor them on: <strong class="text-success">${p.you_teach_them.join(', ')}</strong></div>
        </div>
      </div>
    `).join('');
  }

  // Skill Passport
  if (passport && !passport.error) {
    const preview = document.getElementById('passport-preview');
    preview.innerHTML = `
      <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 8px; padding: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
          <strong>${passport.passport_id} • ${passport.holder_name}</strong>
          <span class="text-success" style="font-size: 0.75rem;">● VERIFIED PROOF</span>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
          Verified Credentials: ${passport.verified_skills.map(s => `<span class="chip chip-accent" style="margin: 0.15rem; font-size: 0.7rem;">${s.skill} (${s.score}%)</span>`).join(' ')}
        </p>
        <div style="font-size: 0.7rem; color: var(--text-muted); font-family: var(--font-mono);">
          SHA-256 Digest: ${passport.signature_hash}
        </div>
      </div>
    `;
  }

  // Cohort Heatmap
  if (heatmap && heatmap.students) {
    const hmContainer = document.getElementById('cohort-heatmap-container');
    const headerRow = `<tr><th style="padding: 0.4rem; text-align: left; font-size: 0.75rem;">Student</th>${heatmap.skills.map(s => `<th style="padding: 0.4rem; font-size: 0.75rem;">${s}</th>`).join('')}</tr>`;
    const studentRows = heatmap.students.map(st => {
      const cells = st.scores.map(sc => {
        let bg = 'rgba(16, 185, 129, 0.2)';
        if (sc < 45) bg = 'rgba(244, 63, 94, 0.25)';
        else if (sc < 70) bg = 'rgba(245, 158, 11, 0.25)';
        return `<td style="padding: 0.4rem; text-align: center; background: ${bg}; font-size: 0.75rem; border-radius: 4px;">${sc}%</td>`;
      }).join('');
      return `<tr><td style="padding: 0.4rem; font-size: 0.8rem; font-weight: 600;">${st.name}</td>${cells}</tr>`;
    }).join('');

    hmContainer.innerHTML = `<table style="width: 100%; border-collapse: separate; border-spacing: 4px;">${headerRow}${studentRows}</table>`;
  }

  // Time Scheduler
  if (sched && sched.timeline) {
    const tlContainer = document.getElementById('schedule-timeline-container');
    tlContainer.innerHTML = sched.timeline.slice(0, 6).map(w => `
      <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border-subtle); padding: 0.65rem 0.85rem; border-radius: 6px; margin-bottom: 0.4rem;">
        <div>
          <strong style="font-size: 0.8rem;">Week ${w.week}: ${w.planned_hours} Hours</strong>
          <small class="text-muted" style="display: block; font-size: 0.7rem;">${w.note}</small>
        </div>
        <span class="chip ${w.status === 'EXAM_CRUNCH_MODE' ? 'chip-warning' : 'chip-blue'}" style="font-size: 0.65rem;">
          ${w.status === 'EXAM_CRUNCH_MODE' ? 'EXAM SOFTENING' : 'FULL SPRINT'}
        </span>
      </div>
    `).join('');
  }
}

function copyPassportLink() {
  navigator.clipboard.writeText('https://learn.antigravity.dev/passport/alex-chen?sig=99A82FB14');
  alert('Public Skill Passport link copied to clipboard!');
}

async function updateScheduleBudget(val) {
  await apiCall('/api/time_schedule/update', 'POST', { weekly_hours_budget: parseInt(val) });
  await renderAnalyticsHub();
}

async function toggleExamBlock() {
  const current = STATE.user.exam_crunch_blocks || [];
  const updated = current.length > 0 ? [] : [{ name: "Midterm Exam Week", start_week: 3, reduction_percent: 60 }];
  await apiCall('/api/time_schedule/update', 'POST', { exam_crunch_blocks: updated });
  await fetchUserData();
  await renderAnalyticsHub();
}
