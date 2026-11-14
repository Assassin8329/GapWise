/**
 * GapWise - AI-Powered Learning Platform & Adaptive Career Navigator
 * Client Controller & Reactive State Store
 * Zero fake/mock data. Pure real user data & clean empty states.
 */

const STATE = {
  activeTab: 'dashboard',
  user: null,
  allUsers: [],
  roadmap: null,
  selectedCourse: null,
  currentTestQuestion: null,
  selectedTestOption: null,
  currentInterviewQuestion: null,
  currentPracticeChallenge: null,
  voiceRecognition: null,
  voiceRecording: false,
  voiceStartedAt: null,
  voiceLastResultAt: null,
  voicePauses: [],
  connectors: {},
  activeOAuthFlow: null,
  sandboxLanguage: 'python',
  theme: 'system',
  googleConfig: null,
  authMode: 'login',
  modelMode: 'offline',
  providerCatalog: null,
  aiStatus: null,
  chatHistory: []
};

// The app must be served by the backend so session cookies and API requests
// share an origin. If someone double-clicks index.html, send them to the live
// server instead of allowing every auth/model request to fail from file://.
const GAPWISE_BACKEND_ORIGIN = 'http://127.0.0.1:8000';
if (window.location.protocol === 'file:') {
  window.location.replace(`${GAPWISE_BACKEND_ORIGIN}/`);
}

document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  await fetchUsersList();
  await fetchUserData();
  await refreshActiveTab();
  await initStartupGate();
});

async function apiCall(endpoint, method = 'GET', data = null) {
  try {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' }
    };
    if (data) opts.body = JSON.stringify(data);
    const requestURL = endpoint.startsWith('http') ? endpoint : `${window.location.protocol === 'file:' ? GAPWISE_BACKEND_ORIGIN : ''}${endpoint}`;
    const res = await fetch(requestURL, opts);
    const payload = await res.json().catch(() => ({}));
    if (!res.ok) return { error: payload.error || `Request failed (${res.status})`, status: res.status };
    return payload;
  } catch (err) {
    console.error(`API Call failed on ${endpoint}:`, err);
    return { error: err.message };
  }
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));
}

function initTheme() {
  const savedTheme = localStorage.getItem('gapwise-theme') || 'system';
  applyTheme(savedTheme);
  const media = window.matchMedia('(prefers-color-scheme: dark)');
  if (media.addEventListener) media.addEventListener('change', () => {
    if (STATE.theme === 'system') applyTheme('system');
  });
}

function applyTheme(theme) {
  const allowed = ['system', 'light', 'dark'];
  STATE.theme = allowed.includes(theme) ? theme : 'system';
  document.documentElement.dataset.theme = STATE.theme;
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  document.body.classList.toggle('dark-theme', STATE.theme === 'dark' || (STATE.theme === 'system' && prefersDark));
  const label = STATE.theme[0].toUpperCase() + STATE.theme.slice(1);
  const toggle = document.getElementById('theme-toggle');
  const toggleLabel = document.getElementById('theme-toggle-label');
  const toggleIcon = document.getElementById('theme-toggle-icon');
  if (toggle) toggle.setAttribute('aria-label', `Theme: ${label}. Switch theme`);
  if (toggleLabel) toggleLabel.textContent = label;
  if (toggleIcon) toggleIcon.textContent = STATE.theme === 'dark' ? '☾' : STATE.theme === 'light' ? '☀' : '◐';
}

function cycleTheme() {
  const order = ['system', 'light', 'dark'];
  const next = order[(order.indexOf(STATE.theme) + 1) % order.length];
  localStorage.setItem('gapwise-theme', next);
  applyTheme(next);
}

async function initStartupGate() {
  const [config, aiStatus, providers] = await Promise.all([
    apiCall('/api/auth/config'), apiCall('/api/ai/status'), apiCall('/api/ai/providers')
  ]);
  STATE.googleConfig = config;
  STATE.aiStatus = aiStatus;
  STATE.providerCatalog = providers;
  updateModelStatusPill();
  populateProviderChoices(providers);
  const authReady = Boolean(STATE.user?.id);
  const modelReady = Boolean(aiStatus?.configured);
  if (!authReady || !modelReady) openStartupModal();
  else closeStartupModal();
  updateStartupReadiness();
}

function openStartupModal() {
  document.getElementById('modal-startup')?.classList.remove('hidden');
  loadOllamaModels();
}

function closeStartupModal() {
  document.getElementById('modal-startup')?.classList.add('hidden');
}

function setStartupAuthMode(mode) {
  STATE.authMode = mode;
  const register = mode === 'register';
  document.getElementById('startup-login-tab').classList.toggle('active', !register);
  document.getElementById('startup-register-tab').classList.toggle('active', register);
  document.getElementById('startup-name-label').classList.toggle('hidden', !register);
  document.getElementById('startup-name').classList.toggle('hidden', !register);
  document.getElementById('startup-profile-fields').classList.toggle('hidden', !register);
  document.getElementById('startup-password').setAttribute('autocomplete', register ? 'new-password' : 'current-password');
  document.getElementById('startup-auth-submit').textContent = register ? 'Create account' : 'Sign in';
  document.getElementById('startup-auth-status').textContent = '';
}

function setModelMode(mode) {
  STATE.modelMode = mode;
  const online = mode === 'online';
  document.getElementById('startup-offline-tab').classList.toggle('active', !online);
  document.getElementById('startup-online-tab').classList.toggle('active', online);
  document.getElementById('offline-model-fields').classList.toggle('hidden', online);
  document.getElementById('online-model-fields').classList.toggle('hidden', !online);
}

function populateProviderChoices(catalog) {
  const select = document.getElementById('online-provider');
  if (!select || !catalog?.online) return;
  select.innerHTML = Object.entries(catalog.online).map(([id, info]) => `<option value="${escapeHtml(id)}">${escapeHtml(info.label)}</option>`).join('');
  applyProviderPreset();
}

function applyProviderPreset() {
  const provider = document.getElementById('online-provider')?.value;
  const preset = STATE.providerCatalog?.online?.[provider];
  if (!preset) return;
  const base = document.getElementById('online-base-url');
  if (base && !base.value) base.value = preset.base_url || '';
  const model = document.getElementById('online-model');
  if (model && !model.value && preset.models?.length) model.value = preset.models[0];
}

async function loadOllamaModels() {
  const result = await apiCall('/api/ai/ollama/models');
  const list = document.getElementById('ollama-model-list');
  if (list && Array.isArray(result?.models)) list.innerHTML = result.models.map(model => `<option value="${escapeHtml(model)}"></option>`).join('');
  const status = document.getElementById('startup-ai-status');
  if (status && result?.error && STATE.modelMode === 'offline') status.textContent = result.error;
}

async function submitStartupAuth() {
  const email = document.getElementById('startup-email').value.trim();
  const password = document.getElementById('startup-password').value;
  const endpoint = STATE.authMode === 'register' ? '/api/auth/register' : '/api/auth/login';
  const payload = { email, password };
  if (STATE.authMode === 'register') {
    payload.name = document.getElementById('startup-name').value.trim();
    payload.goal_domain = document.getElementById('startup-domain').value.trim();
    payload.target_outcome = document.getElementById('startup-outcome').value.trim();
    payload.experience_level = document.getElementById('startup-experience').value.trim();
    payload.preferred_learning_style = document.getElementById('startup-learning-style').value.trim();
    payload.target_role = payload.target_outcome;
  }
  const status = document.getElementById('startup-auth-status');
  status.className = 'setup-status';
  status.textContent = 'Checking account…';
  const result = await apiCall(endpoint, 'POST', payload);
  if (result?.user) {
    handleAuthSuccess(result.user);
    status.className = 'setup-status success';
    status.textContent = 'Account connected. Progress will sync to this email.';
    updateStartupReadiness();
  } else {
    status.className = 'setup-status error';
    status.textContent = result?.error || 'Could not authenticate.';
  }
}

function beginGoogleOAuth() {
  if (!STATE.googleConfig?.google_ready) {
    document.getElementById('startup-auth-status').textContent = 'Google OAuth needs GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and a matching redirect URI on the server.';
    return;
  }
  window.location.href = `${window.location.protocol === 'file:' ? GAPWISE_BACKEND_ORIGIN : ''}/api/auth/google/start`;
}

async function configureStartupAI() {
  const payload = {
    mode: STATE.modelMode,
    context_window: Number(document.getElementById('ai-context-window').value || 30720)
  };
  if (STATE.modelMode === 'offline') {
    payload.model = document.getElementById('ollama-model').value.trim() || 'mimo-v2.6:9b';
    payload.host = document.getElementById('ollama-host').value.trim();
  } else {
    payload.provider = document.getElementById('online-provider').value;
    payload.api_key = document.getElementById('online-api-key').value.trim();
    payload.base_url = document.getElementById('online-base-url').value.trim();
    payload.model = document.getElementById('online-model').value.trim();
  }
  const status = document.getElementById('startup-ai-status');
  status.className = 'setup-status';
  status.textContent = 'Connecting to model…';
  const result = await apiCall('/api/ai/config', 'POST', payload);
  if (result?.configured) {
    STATE.aiStatus = result;
    updateModelStatusPill();
    status.className = 'setup-status success';
    status.textContent = `${result.provider || 'Ollama'} / ${result.model} is ready. API keys remain in server memory only.`;
    updateStartupReadiness();
  } else {
    status.className = 'setup-status error';
    status.textContent = result?.error || 'Could not connect to the model.';
  }
}

function updateModelStatusPill() {
  const pill = document.getElementById('model-status-pill');
  const label = document.getElementById('model-status-label');
  if (!pill || !label) return;
  if (STATE.aiStatus?.configured) {
    pill.classList.add('ready');
    label.textContent = `${STATE.aiStatus.provider || 'ollama'} · ${STATE.aiStatus.model}`;
  } else {
    pill.classList.remove('ready');
    label.textContent = 'AI setup';
  }
}

function updateStartupReadiness() {
  const ready = Boolean(STATE.user?.id && STATE.aiStatus?.configured);
  const button = document.getElementById('startup-enter-btn');
  const label = document.getElementById('startup-ready-status');
  if (button) button.disabled = !ready;
  if (label) label.textContent = ready ? 'Everything is ready. Your data and model choice are connected.' : 'Complete account and AI setup to enter GapWise.';
}

function finishStartupSetup() {
  if (STATE.user?.id && STATE.aiStatus?.configured) {
    sessionStorage.setItem('gapwise-startup-complete', '1');
    closeStartupModal();
    refreshActiveTab();
  }
}

async function fetchUsersList() {
  const users = await apiCall('/api/users_list');
  if (Array.isArray(users)) {
    STATE.allUsers = users;
    const select = document.getElementById('user-select');
    if (select) {
      if (users.length === 0) {
        select.innerHTML = '<option value="">No Registered Profiles</option>';
      } else {
        select.innerHTML = users.map(u => `
          <option value="${u.id}">${u.name} (${u.user_type})</option>
        `).join('');
      }
    }
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
  document.getElementById('header-streak').textContent = `${user.streak_days || 0} Days`;
  document.getElementById('header-xp').textContent = `${(user.xp || 0).toLocaleString()} XP`;

  const btnLabel = document.getElementById('auth-btn-label');
  if (user && user.id) {
    btnLabel.textContent = user.name;
    const select = document.getElementById('user-select');
    if (select) select.value = user.id;
  } else {
    btnLabel.textContent = 'Sign in / setup';
  }
}

// --- USER MANAGEMENT & SWITCHING ---
async function switchUser(userId) {
  if (!userId) return;
  const res = await apiCall('/api/user/switch', 'POST', { user_id: userId });
  if (res && res.success) {
    STATE.user = res.active_user;
    renderHeaderProfile(STATE.user);
    await refreshActiveTab();
  }
}

function openGoogleAuthModal() {
  openStartupModal();
}
function closeGoogleAuthModal() {
  // Kept as a compatibility hook for existing bookmarks; startup owns auth now.
}
function openProfileModal() {
  openGoogleAuthModal();
}

function handleAuthSuccess(user) {
  closeGoogleAuthModal();
  STATE.user = user;
  updateStartupReadiness();
  fetchUsersList().then(() => {
    renderHeaderProfile(STATE.user);
    refreshActiveTab();
  });
}

// --- TAB SWITCHER ---
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

  const userType = (STATE.user && STATE.user.user_type) ? STATE.user.user_type.toUpperCase() : 'LEARNER';
  document.getElementById('dash-user-type').textContent = `${userType} PROFILE`;

  // Goal banner & match gauge. Never expose a benchmark fallback when no goal is declared.
  if (matchData && !matchData.error) {
    const goalParts = [STATE.user?.goal_domain, STATE.user?.target_outcome].filter(Boolean).map(value => value.trim());
    const declaredDirection = goalParts.join(' · ');
    const hasGoal = Boolean(declaredDirection);
    const hasBenchmark = Boolean(matchData.match_available);
    document.getElementById('dash-target-role').textContent = declaredDirection || 'Not selected';
    document.getElementById('dash-role-desc').textContent = hasGoal
      ? `Your roadmap and practice are being tailored to ${declaredDirection}. Readiness will be based on evidence you create here.`
      : 'Declare an area and outcome during setup to make GapWise personal to you.';
    document.getElementById('dash-salary').textContent = hasBenchmark ? (matchData.salary_range || 'Not available') : 'Not selected';
    document.getElementById('dash-growth').textContent = hasBenchmark ? (matchData.demand_growth || 'Not available') : 'Not selected';
    document.getElementById('dash-weeks').textContent = hasBenchmark && matchData.estimated_weeks_to_ready
      ? `~${matchData.estimated_weeks_to_ready} weeks` : 'Not selected';

    const matchPct = hasGoal && hasBenchmark ? Math.round(matchData.match_percent || 0) : 0;
    document.getElementById('dash-match-percent').textContent = `${matchPct}%`;
    document.getElementById('dash-gauge-fill').setAttribute('stroke-dasharray', `${matchPct}, 100`);

    const gapExplanation = document.getElementById('dash-gap-explanation');

    if (!hasGoal) {
      gapExplanation.textContent = 'Choose a growth domain and desired outcome to start a personalized evidence trail.';
    } else if (!hasBenchmark) {
      gapExplanation.textContent = 'Your direction is saved. Add skills or generate model-backed practice to build evidence; no benchmark is available for this direction yet.';
    } else if (!matchData.has_skills) {
      gapExplanation.innerHTML = `No skills added to your profile yet. Add current competencies to calculate evidence against <strong>${escapeHtml(matchData.target_role)}</strong>.`;
    } else {
      const missing = matchData.missing_skills || [];
      const missingTags = missing.map(m => `<span class="tag-missing">${escapeHtml(m.skill)}</span>`).join(' ');
      gapExplanation.innerHTML = `Based on your profile skills, readiness for <strong>${escapeHtml(matchData.target_role)}</strong> is ${matchPct}%. High priority gaps: ${missingTags || '<strong class="text-success">Zero missing gaps! Ready for role.</strong>'}`;
    }
  }

  // Confidence Meter List (or Empty State)
  const confList = document.getElementById('confidence-meter-list');
  if (Array.isArray(confData) && confData.length > 0) {
    confList.innerHTML = confData.slice(0, 5).map(item => {
      let flagHtml = '';
      if (item.flag === 'DUNNING_KRUGER_RISK') {
        flagHtml = `<div class="cm-flag-banner cm-flag-warning">⚠️ Overconfidence Warning: Self-rating exceeds test score by ${Math.round(item.discrepancy)}%</div>`;
      } else if (item.flag === 'IMPOSTER_SYNDROME') {
        flagHtml = `<div class="cm-flag-banner cm-flag-boost">✨ Imposter Syndrome Detected: Assessed ${Math.abs(Math.round(item.discrepancy))}% higher than self-rating!</div>`;
      } else if (item.flag === 'CALIBRATED') {
        flagHtml = `<div class="cm-flag-banner cm-flag-success">✓ Calibrated: Perception matches test performance</div>`;
      } else if (item.flag === 'UNTESTED') {
        flagHtml = `<div class="cm-flag-banner" style="background: rgba(255,255,255,0.04); color: var(--text-muted);">Take an adaptive test to verify your self-rating</div>`;
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
  } else {
    confList.innerHTML = `
      <div style="text-align: center; padding: 2rem 1rem; color: var(--text-muted);">
        <p style="font-size: 0.9rem; margin-bottom: 0.75rem;">No skills tracked in Confidence Meter yet.</p>
        <button class="btn btn-primary btn-sm" onclick="openAddSkillModal()">+ Add Your First Skill</button>
      </div>
    `;
  }

  // Learning Twin Telemetry
  if (twinData && !twinData.error) {
    const twinHasGoal = Boolean(twinData.has_goal);
    const twinHasData = Boolean(twinData.has_data);
    document.getElementById('twin-status').textContent = twinHasData ? 'ACTIVE' : 'WAITING';
    document.getElementById('twin-velocity').textContent = twinHasData ? `${twinData.study_velocity_xp_per_day} XP/day` : 'Not available';
    document.getElementById('twin-retention').textContent = twinHasData ? `${Math.round(twinData.retention_stability_factor * 100)}% Stability` : 'Not available';
    document.getElementById('twin-peak').textContent = twinHasGoal ? twinData.peak_focus_hours : 'Not selected';
    document.getElementById('twin-predicted').textContent = twinHasData && twinData.predicted_weeks_remaining > 0
      ? `In ${twinData.predicted_weeks_remaining} weeks` : (twinHasGoal ? 'Awaiting activity' : 'Not selected');
    document.getElementById('twin-modality').textContent = twinData.preferred_format || 'Not selected';
  }

  // Quests List
  if (gamifyData && gamifyData.quests) {
    document.getElementById('level-title-badge').textContent = gamifyData.level_info.title;
    const questsList = document.getElementById('quests-container');
    questsList.innerHTML = gamifyData.quests.length ? gamifyData.quests.map(q => `
      <div class="quest-item">
        <div class="quest-left">
          <span class="quest-icon">${q.completed ? '✅' : '🎯'}</span>
          <div>
            <div class="quest-title">${escapeHtml(q.title)}</div>
            <div class="quest-desc">${escapeHtml(q.description)}</div>
          </div>
        </div>
        <span class="badge-xp text-accent">+${escapeHtml(q.xp_reward)} XP</span>
      </div>
    `).join('') : '<div class="empty-state-card"><div class="empty-state-title">No quests yet</div><div class="empty-state-desc">Declare a goal to receive personalized quests.</div></div>';
  }
}

// ==========================================
// 2. ROADMAP & VISUAL DAG
// ==========================================
async function renderRoadmap() {
  const roadmap = await apiCall('/api/roadmap');
  const container = document.getElementById('dag-container');
  if (!roadmap || roadmap.error || !roadmap.nodes || roadmap.nodes.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
        <h3>No Roadmap Generated</h3>
        <p style="margin: 0.5rem 0 1rem;">Complete your growth domain and desired outcome, then connect a model to generate an evidence-based roadmap.</p>
        <button class="btn btn-primary" onclick="openStartupModal()">Open profile and AI setup</button>
      </div>
    `;
    return;
  }
  STATE.roadmap = roadmap;
  container.innerHTML = '';

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
        <div class="node-description">${escapeHtml(node.description || node.why_this_pick || '')}</div>
        <div class="node-instructions">${(node.instructions || []).map(step => `<div>• ${escapeHtml(step)}</div>`).join('')}</div>
        <div class="node-evidence"><strong>Evidence:</strong> ${escapeHtml(node.evidence || node.practical_exercise || 'Declare completion evidence with the AI mentor.')}</div>
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
  const list = document.getElementById('skills-editor-list');

  if (analysis && analysis.all_skills && analysis.all_skills.length > 0) {
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
          <div style="display: flex; align-items: center; gap: 1rem;">
            <div class="skill-stars" title="Click to self-rate">${stars}</div>
            <button class="btn btn-ghost btn-sm" style="color: var(--accent-rose);" onclick="deleteSkill('${s.skill}')">✕</button>
          </div>
        </div>
      `;
    }).join('');
  } else {
    list.innerHTML = `
      <div style="text-align: center; padding: 2rem 1rem; color: var(--text-muted);">
        <p style="font-size: 0.9rem; margin-bottom: 0.75rem;">No skills in your profile matrix yet.</p>
        <button class="btn btn-primary btn-sm" onclick="openAddSkillModal()">+ Add Your First Skill</button>
      </div>
    `;
  }

  const select = document.getElementById('pivot-role-select');
  if (select) runCareerPivot(select.value);
}

function openAddSkillModal() {
  document.getElementById('modal-add-skill').classList.remove('hidden');
}
function closeAddSkillModal() {
  document.getElementById('modal-add-skill').classList.add('hidden');
}

async function submitAddSkill() {
  const skillName = document.getElementById('new-skill-name').value.trim();
  const rating = parseFloat(document.getElementById('new-skill-rating').value) || 3.0;

  if (!skillName) {
    alert('Please enter a skill name.');
    return;
  }

  if (!STATE.user || !STATE.user.id) {
    // If not signed in, prompt Google Sign in first
    alert('Please sign in with Google or create a learner profile first.');
    closeAddSkillModal();
    openGoogleAuthModal();
    return;
  }

  const res = await apiCall('/api/user/skill_add', 'POST', { skill: skillName, rating });
  closeAddSkillModal();
  document.getElementById('new-skill-name').value = '';

  if (res && res.success) {
    await fetchUserData();
    await renderDashboard();
    await renderSkillsAndPivot();
  }
}

async function setSkillRating(skill, rating) {
  const res = await apiCall('/api/user/skill_rate', 'POST', { skill, rating });
  if (res && res.success) {
    await fetchUserData();
    await renderSkillsAndPivot();
  }
}

async function deleteSkill(skill) {
  if (!confirm(`Remove ${skill} from your profile?`)) return;
  const res = await apiCall('/api/user/skill_delete', 'POST', { skill });
  if (res && res.success) {
    await fetchUserData();
    await renderSkillsAndPivot();
  }
}

async function runCareerPivot(targetRole) {
  const res = await apiCall('/api/career_pivot', 'POST', { new_role: targetRole });
  if (!res || res.error) return;

  const container = document.getElementById('pivot-results-container');
  const transferred = (res.transferred_skills || []).map(s => `
    <div class="cm-bar-row">
      <span style="width: 140px;">${s.skill}</span>
      <div class="cm-progress-track">
        <div class="cm-fill-assessed" style="width: ${s.current_score}%;"></div>
      </div>
      <span class="text-success" style="font-size: 0.75rem;">${s.current_score}% (${s.transfer_efficiency} TRANSFER)</span>
    </div>
  `).join('');

  const newNeeded = (res.new_skills_needed || []).map(s => `
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
        <h4 style="font-size: 0.85rem; margin-bottom: 0.5rem;">Transferred Competencies:</h4>
        <div class="confidence-list">${transferred || '<p class="text-muted" style="font-size: 0.8rem;">Add your profile skills to view transferred competencies.</p>'}</div>
      </div>

      <div style="margin-top: 0.75rem;">
        <h4 style="font-size: 0.85rem; margin-bottom: 0.5rem;">New Skills Required for ${res.new_role}:</h4>
        <div>${newNeeded}</div>
      </div>

      <button class="btn btn-primary btn-sm" style="margin-top: 1rem;" onclick="applyCareerPivot('${res.new_role}')">
        Set ${res.new_role} as Active Target Goal
      </button>
    </div>
  `;
}

async function applyCareerPivot(newRole) {
  const res = await apiCall('/api/career_pivot/apply', 'POST', { new_role: newRole });
  if (res && res.success) {
    alert(`Career target updated to ${newRole}! GapWise has dynamically recalibrated your roadmap.`);
    await fetchUserData();
    setTab('dashboard');
  }
}

// ==========================================
// 4. ADAPTIVE CHECKS & PRACTICE
// ==========================================
async function loadNextQuestion() {
  const data = await apiCall('/api/test/next');
  if (!data || data.error) {
    const question = document.getElementById('test-question-text');
    const options = document.getElementById('test-options-container');
    if (question) question.textContent = data?.error || 'Sign in and connect a model to generate a live question.';
    if (options) options.innerHTML = `<button class="btn btn-primary" onclick="openStartupModal()">Open setup</button>`;
    return;
  }

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

  const scaffoldBox = document.getElementById('test-scaffolding-box');
  if (data.show_scaffolding && data.scaffolding_hint) {
    document.getElementById('test-hint-text').textContent = data.scaffolding_hint;
    scaffoldBox.classList.remove('hidden');
  } else {
    scaffoldBox.classList.add('hidden');
  }

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
    fbBox.innerHTML = `<strong>✓ Correct! (+${res.xp_awarded} XP)</strong><p>${res.explanation}</p><small>Adaptive ability rating updated from θ ${res.previous_theta} → ${res.new_theta}</small>`;
  } else {
    fbBox.className = 'feedback-box feedback-wrong';
    fbBox.innerHTML = `<strong>✕ Incorrect</strong><p>${res.explanation}</p><small>Adaptive ability rating updated from θ ${res.previous_theta} → ${res.new_theta}</small>`;
  }

  document.getElementById('btn-submit-answer').classList.add('hidden');
  document.getElementById('btn-next-question').classList.remove('hidden');
  await fetchUserData();
}

async function generatePracticeChallenge() {
  const domain = document.getElementById('practice-domain').value.trim();
  const language = document.getElementById('practice-language').value.trim();
  const format = document.getElementById('practice-format').value;
  const empty = document.getElementById('practice-empty');
  const content = document.getElementById('practice-challenge-content');
  if (!domain || !language) {
    empty.textContent = 'Choose both a domain and a language or medium before generating a challenge.';
    return;
  }
  empty.textContent = 'Generating a challenge from your profile…';
  content.classList.add('hidden');
  const query = new URLSearchParams({ domain, language, format });
  const res = await apiCall(`/api/practice/challenge?${query.toString()}`);
  if (!res || res.error) {
    empty.textContent = res?.error || 'The practice agent could not generate a challenge.';
    return;
  }
  STATE.currentPracticeChallenge = res;
  document.getElementById('practice-challenge-title').textContent = `${res.title} · ${res.language}`;
  document.getElementById('practice-challenge-prompt').textContent = res.prompt;
  document.getElementById('practice-challenge-instructions').innerHTML = (res.instructions || []).map(item => `<li>${escapeHtml(item)}</li>`).join('');
  document.getElementById('practice-response').value = res.starter || '';
  document.getElementById('practice-feedback').classList.add('hidden');
  empty.classList.add('hidden');
  content.classList.remove('hidden');
}

async function evaluatePracticeChallenge() {
  const challenge = STATE.currentPracticeChallenge;
  const answer = document.getElementById('practice-response').value.trim();
  const feedback = document.getElementById('practice-feedback');
  if (!challenge || !answer) {
    feedback.className = 'feedback-box feedback-wrong';
    feedback.textContent = 'Write a response before evaluating it.';
    feedback.classList.remove('hidden');
    return;
  }
  feedback.className = 'feedback-box';
  feedback.textContent = 'Evaluating observed evidence…';
  feedback.classList.remove('hidden');
  const res = await apiCall('/api/practice/evaluate', 'POST', { challenge_id: challenge.id, answer });
  if (!res || res.error) {
    feedback.className = 'feedback-box feedback-wrong';
    feedback.textContent = res?.error || 'Evaluation failed.';
    return;
  }
  feedback.className = 'feedback-box feedback-correct';
  feedback.innerHTML = `<strong>${escapeHtml(res.score)}/100 · ${escapeHtml(res.verdict)}</strong><p><b>Strengths:</b> ${(res.strengths || []).map(escapeHtml).join(' · ') || 'None declared'}</p><p><b>Next steps:</b> ${(res.improvements || []).map(escapeHtml).join(' · ') || 'None declared'}</p><small>Evidence observed: ${(res.evidence_observed || []).map(escapeHtml).join(' · ') || 'No external validation was claimed'} · +${res.xp_awarded || 0} XP</small>`;
  await fetchUserData();
}

// ==========================================
// 5. MOCK INTERVIEW AGENT
// ==========================================
async function renderInterviewArena() {
  const data = await apiCall('/api/mock_interview');
  if (!data || data.error || !data.questions) {
    document.getElementById('interview-q-text').textContent = data?.error || 'Sign in and connect a model to generate an interview question.';
    return;
  }

  const q = data.questions[0];
  STATE.currentInterviewQuestion = q;

  document.getElementById('interview-role-label').textContent = data.target_role || STATE.user?.target_outcome || STATE.user?.goal_domain || 'your chosen outcome';
  document.getElementById('interview-q-category').textContent = q.category;
  document.getElementById('interview-q-text').textContent = `"${q.question}"`;
}

function toggleInterviewVoice() {
  if (STATE.voiceRecording) {
    stopInterviewVoice();
    return;
  }
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const status = document.getElementById('interview-voice-status');
  if (!Recognition) {
    status.textContent = 'This browser does not expose speech recognition. You can still type your answer.';
    status.className = 'setup-status error';
    return;
  }
  const recognition = new Recognition();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = navigator.language || 'en-US';
  STATE.voiceRecognition = recognition;
  STATE.voiceRecording = true;
  STATE.voiceStartedAt = performance.now();
  STATE.voiceLastResultAt = performance.now();
  STATE.voicePauses = [];
  document.getElementById('interview-voice-btn').textContent = '⏹ Stop voice input';
  status.textContent = `Listening in ${recognition.lang}… speak naturally; pauses over 1.2 seconds are measured.`;
  status.className = 'setup-status success';
  recognition.onresult = event => {
    const now = performance.now();
    if (STATE.voiceLastResultAt && now - STATE.voiceLastResultAt > 1200) STATE.voicePauses.push((now - STATE.voiceLastResultAt) / 1000);
    STATE.voiceLastResultAt = now;
    let transcript = '';
    for (let i = 0; i < event.results.length; i++) transcript += event.results[i][0].transcript;
    document.getElementById('interview-answer-input').value = transcript;
  };
  recognition.onerror = event => {
    status.textContent = `Voice input error: ${event.error}. You can continue by typing.`;
    status.className = 'setup-status error';
    stopInterviewVoice(true);
  };
  recognition.onend = () => {
    if (STATE.voiceRecording) {
      try { recognition.start(); } catch (_) { stopInterviewVoice(true); }
    }
  };
  recognition.start();
}

function stopInterviewVoice(silent = false) {
  const recognition = STATE.voiceRecognition;
  if (recognition) {
    recognition.onend = null;
    try { recognition.stop(); } catch (_) { /* already stopped */ }
  }
  STATE.voiceRecording = false;
  const duration = STATE.voiceStartedAt ? (performance.now() - STATE.voiceStartedAt) / 1000 : 0;
  const longest = STATE.voicePauses.length ? Math.max(...STATE.voicePauses) : 0;
  const answer = document.getElementById('interview-answer-input').value;
  const fillers = (answer.toLowerCase().match(/\b(um|uh|like|you know|actually|basically)\b/g) || []).length;
  const metrics = document.getElementById('interview-voice-metrics');
  metrics.textContent = `${Math.round(duration)}s · ${fillers} filler words · ${STATE.voicePauses.length} thinking pauses · longest ${longest.toFixed(1)}s`;
  metrics.classList.remove('hidden');
  document.getElementById('interview-voice-btn').textContent = '🎙 Start voice input';
  if (!silent) {
    const status = document.getElementById('interview-voice-status');
    status.textContent = 'Voice capture stopped. Review the transcript before submitting.';
    status.className = 'setup-status';
  }
}

async function submitInterviewAnswer() {
  if (STATE.voiceRecording) stopInterviewVoice();
  const answer = document.getElementById('interview-answer-input').value;
  if (!answer.trim()) {
    alert('Please enter your response before submitting.');
    return;
  }

  const q = STATE.currentInterviewQuestion;
  const voiceText = document.getElementById('interview-voice-metrics').textContent || '';
  const res = await apiCall('/api/mock_interview/submit', 'POST', {
    question_id: q.id,
    answer,
    voice_metrics: {
      summary: voiceText,
      filler_word_count: (answer.toLowerCase().match(/\b(um|uh|like|you know|actually|basically)\b/g) || []).length,
      pause_count: STATE.voicePauses.length,
      longest_pause_seconds: STATE.voicePauses.length ? Math.max(...STATE.voicePauses) : 0
    }
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
          <p class="card-sub">AI-scored performance across four core dimensions</p>
        </div>
        <div style="font-size: 1.5rem; font-weight: 800; color: var(--accent-cyan);">${res.composite_score}/100</div>
      </div>

      <div class="rubric-grid">
        <div class="rubric-score-box">
          <div class="rsb-num">${rb.technical_depth}%</div>
          <div class="rsb-label">Subject Depth</div>
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
        ${res.delivery_feedback?.length ? `<strong class="text-accent">Delivery feedback:</strong><ul style="margin: 0.4rem 0 0.8rem 1.25rem; font-size: 0.85rem;">${res.delivery_feedback.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : ''}
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
    container.innerHTML = `<div class="chat-empty-state"><strong>Ada is ready when you are.</strong><p>Your first message will be sent to the configured ${escapeHtml(STATE.aiStatus?.provider || 'AI')} model with your authenticated profile context.</p></div>`;
  }
}

async function sendMentorMessage(e) {
  e.preventDefault();
  const input = document.getElementById('chat-user-input');
  const msg = input.value.trim();
  if (!msg) return;

  const container = document.getElementById('chat-messages-container');
  const empty = container.querySelector('.chat-empty-state');
  if (empty) empty.remove();
  container.insertAdjacentHTML('beforeend', `<div class="chat-msg msg-user chat-bubble-row"><span class="chat-bubble user-bubble">${escapeHtml(msg)}</span></div>`);
  input.value = '';
  input.disabled = true;
  const sendButton = e.submitter || document.querySelector('.chat-input-bar button[type="submit"]');
  if (sendButton) sendButton.disabled = true;
  const typingId = `typing-${Date.now()}`;
  container.insertAdjacentHTML('beforeend', `<div id="${typingId}" class="chat-msg msg-mentor chat-bubble-row"><span class="chat-bubble mentor-bubble typing-bubble" role="status" aria-live="polite"><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-label">Ada is thinking…</span></span></div>`);
  container.scrollTop = container.scrollHeight;

  STATE.chatHistory.push({ role: 'user', content: msg });
  try {
    const res = await apiCall('/api/ai/chat', 'POST', { message: msg, history: STATE.chatHistory.slice(-12) });
    document.getElementById(typingId)?.remove();
    if (res && res.reply) {
      STATE.chatHistory.push({ role: 'assistant', content: res.reply });
      container.insertAdjacentHTML('beforeend', `<div class="chat-msg msg-mentor chat-bubble-row"><span class="chat-bubble mentor-bubble"><strong>Ada · AI Mentor</strong><span class="chat-reply">${escapeHtml(res.reply)}</span><small class="text-muted">${escapeHtml(res.model?.provider || 'local model')} · ${escapeHtml(res.model?.model || '')}</small></span></div>`);
    } else if (res?.error) {
      container.insertAdjacentHTML('beforeend', `<div class="chat-msg msg-error chat-bubble-row"><span class="chat-bubble error-bubble">${escapeHtml(res.error)}</span></div>`);
    }
  } finally {
    input.disabled = false;
    if (sendButton) sendButton.disabled = false;
    input.focus();
    container.scrollTop = container.scrollHeight;
  }
}

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

async function submitExplainBack() {
  const concept = document.getElementById('explain-back-concept').value.trim();
  const explanation = document.getElementById('explain-back-text').value;
  if (!concept) {
    alert('Choose a concept, skill, or topic first.');
    return;
  }
  if (!explanation.trim()) {
    alert('Please write an explanation first.');
    return;
  }

  const res = await apiCall('/api/ai_mentor/explain_back', 'POST', { concept, explanation });
  if (!res || res.error) return;

  const box = document.getElementById('explain-back-feedback');
  box.classList.remove('hidden');
  box.innerHTML = `
    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 8px; padding: 1rem; margin-top: 1rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
        <strong>Explain-back score: ${res.composite_score}/100</strong>
        <span class="badge-xp text-success">+${res.xp_earned} XP</span>
      </div>
      <p style="font-size: 0.85rem; margin-bottom: 0.5rem;">"${escapeHtml(res.explain_back_verdict || '')}"</p>
      <div style="display: flex; gap: 1rem; font-size: 0.8rem; color: var(--text-muted);">
        <span>Accuracy: ${res.accuracy_score}%</span>
        <span>Clarity: ${res.clarity_score}%</span>
        <span>Depth: ${res.depth_score}%</span>
      </div>
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
  document.getElementById('oauth-scopes-list').innerHTML = `<p class="text-muted" style="font-size: 0.8rem;">${conn.pat_instruction || 'Enter personal token.'}</p>`;
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
    code: 'user_auth_code_pkce'
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
    filename: `${provider}_credentials.csv`,
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

  // Struggles (or empty state)
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
    stContainer.innerHTML = `<p class="text-muted" style="font-size: 0.85rem;">No repeated struggle patterns detected across recent assessments.</p>`;
  }

  // Skill Decay (or empty state)
  const decayList = document.getElementById('skill-decay-list');
  if (Array.isArray(decay) && decay.length > 0) {
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
  } else {
    decayList.innerHTML = `<p class="text-muted" style="font-size: 0.85rem;">No assessed skills to monitor for retention decay yet. Take an assessment to activate spaced repetition.</p>`;
  }

  // Peer Pairing (or empty state)
  const peersList = document.getElementById('peer-pairing-list');
  if (Array.isArray(peers) && peers.length > 0) {
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
  } else {
    peersList.innerHTML = `<p class="text-muted" style="font-size: 0.85rem;">No peer matches in cohort yet. Matches will appear as other real learners join the platform.</p>`;
  }

  // Skill Passport Preview
  if (passport && !passport.error) {
    const preview = document.getElementById('passport-preview');
    const skillsBadge = passport.verified_skills.length > 0
      ? passport.verified_skills.map(s => `<span class="chip chip-accent" style="margin: 0.15rem; font-size: 0.7rem;">${s.skill} (${s.score}%)</span>`).join(' ')
      : '<span class="text-muted" style="font-size: 0.8rem;">No verified skills yet. Complete assessments to earn verified badges.</span>';

    preview.innerHTML = `
      <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 8px; padding: 1rem;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
          <strong>${passport.passport_id} • ${passport.holder_name}</strong>
          <span class="text-success" style="font-size: 0.75rem;">● ${passport.verification_status}</span>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
          ${skillsBadge}
        </p>
        <div style="font-size: 0.7rem; color: var(--text-muted); font-family: var(--font-mono);">
          SHA-256 Digest: ${passport.signature_hash}
        </div>
      </div>
    `;
  }

  // Cohort Heatmap (or empty state)
  const hmContainer = document.getElementById('cohort-heatmap-container');
  if (heatmap && heatmap.students && heatmap.students.length > 0) {
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
  } else {
    hmContainer.innerHTML = `<p class="text-muted" style="font-size: 0.85rem; padding: 1.5rem 0; text-align: center;">No cohort data yet. Invite team or class members to populate the matrix heatmap.</p>`;
  }

  // Time Scheduler Timeline
  if (sched && sched.timeline) {
    const tlContainer = document.getElementById('schedule-timeline-container');
    tlContainer.innerHTML = sched.timeline.slice(0, 6).map(w => `
      <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border-subtle); padding: 0.65rem 0.85rem; border-radius: 6px; margin-bottom: 0.4rem;">
        <div>
          <strong style="font-size: 0.8rem;">Week ${w.week}: ${w.planned_hours} Hours</strong>
          <small class="text-muted" style="display: block; font-size: 0.7rem;">${w.note}</small>
        </div>
        <span class="chip ${w.status === 'EXAM_CRUNCH_MODE' ? 'chip-warning' : 'chip-blue'}" style="font-size: 0.65rem;">
          ${w.status === 'EXAM_CRUNCH_MODE' ? 'EXAM SOFTENING' : 'STANDARD'}
        </span>
      </div>
    `).join('');
  }
}

function copyPassportLink() {
  const url = (STATE.user && STATE.user.id) ? `https://gapwise.dev/passport/${STATE.user.id}` : 'https://gapwise.dev/passport/me';
  navigator.clipboard.writeText(url);
  alert(`GapWise Skill Passport link copied to clipboard!\n${url}`);
}

async function updateScheduleBudget(val) {
  await apiCall('/api/time_schedule/update', 'POST', { weekly_hours_budget: parseInt(val) });
  await renderAnalyticsHub();
}

async function toggleExamBlock() {
  const current = (STATE.user && STATE.user.exam_crunch_blocks) || [];
  const updated = current.length > 0 ? [] : [{ name: "Midterm Exam Week", start_week: 3, reduction_percent: 60 }];
  await apiCall('/api/time_schedule/update', 'POST', { exam_crunch_blocks: updated });
  await fetchUserData();
  await renderAnalyticsHub();
}
