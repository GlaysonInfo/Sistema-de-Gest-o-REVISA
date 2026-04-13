const state = {
  token: localStorage.getItem("revisa.gabinete.token") || "",
  cabinet: null,
  vereador: null,
  capture: null,
  person: null,
  demand: null,
  task: null,
  overview: null,
};

const $ = (id) => document.getElementById(id);

function apiBase() {
  return $("apiBase").value.replace(/\/$/, "");
}

function headers(json = true) {
  const base = {};
  if (json) base["Content-Type"] = "application/json";
  if (state.token) base.Authorization = `Bearer ${state.token}`;
  return base;
}

async function api(path, options = {}) {
  const response = await fetch(`${apiBase()}${path}`, {
    ...options,
    headers: {
      ...headers(options.body !== undefined),
      ...(options.headers || {}),
    },
  });
  const text = await response.text();
  const isJson = response.headers.get("content-type")?.includes("application/json");
  const data = text && isJson ? JSON.parse(text) : null;
  if (!response.ok) {
    const detail = data?.detail || response.statusText;
    if (response.status === 422 && Array.isArray(detail)) {
      throw new Error(formatValidationError(detail));
    }
    throw new Error(Array.isArray(detail) ? JSON.stringify(detail) : detail);
  }
  return data;
}

function toast(message) {
  $("toast").textContent = message;
  window.clearTimeout(window.__toastTimer);
  window.__toastTimer = window.setTimeout(() => {
    $("toast").textContent = "";
  }, 4200);
}

function escapeHtml(value) {
  return `${value ?? ""}`.replace(/[&<>"']/g, (char) => {
    const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
    return map[char];
  });
}

function formatValidationError(detail) {
  const first = detail[0];
  const field = Array.isArray(first?.loc) ? first.loc.filter((part) => part !== "body").join(".") : "campo";
  return `${field}: ${first?.msg || "valor invalido"}`;
}

function shortId(value) {
  return value ? `${value}`.slice(0, 8) : "nenhum";
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function toneByStatus(status) {
  if (["RESOLVED", "CLOSED", "COMPLETED", "CONVERTED_TO_DEMAND", "ACTIVE"].includes(status)) return "green";
  if (["HIGH", "OPEN", "NEW", "ASSIGNED", "IN_PROGRESS", "PLANNED"].includes(status)) return "yellow";
  if (["CANCELLED", "BLOCKED"].includes(status)) return "red";
  return "cyan";
}

function setSession() {
  $("sessionState").textContent = state.token ? "Sessao ativa" : "Sessao pendente";
}

function setSelected() {
  $("contextCabinet").textContent = state.cabinet?.name || "nenhum";
  $("contextVereador").textContent = state.vereador?.person?.full_name || shortId(state.vereador?.id);
  $("selectedCapture").textContent = state.capture ? `${shortId(state.capture.id)} - ${state.capture.full_name}` : "nenhum";
  $("selectedPerson").textContent = state.person ? `${shortId(state.person.id)} - ${state.person.full_name}` : "nenhuma";
  $("selectedDemand").textContent = state.demand ? `${shortId(state.demand.id)} - ${state.demand.status}` : "nenhuma";
  $("selectedTask").textContent = state.task ? `${shortId(state.task.id)} - ${state.task.status}` : "nenhuma";
}

function setMetrics() {
  const metrics = state.overview?.metrics;
  $("metricCarteira").textContent = metrics?.linked_people ?? 0;
  $("metricCaptacoes").textContent = metrics?.captures ?? 0;
  $("metricDemandas").textContent = metrics?.open_demands ?? 0;
  $("metricTarefas").textContent = metrics?.open_tasks ?? 0;
  $("metricAgenda").textContent = metrics?.planned_events ?? 0;
}

function renderEmpty(target, message) {
  target.innerHTML = `<p class="empty">${escapeHtml(message)}</p>`;
}

function renderItem(target, title, subtitle, body, tone = "cyan", onClick = null) {
  const node = document.createElement(onClick ? "button" : "article");
  node.className = "item";
  node.dataset.tone = tone;
  if (onClick) {
    node.type = "button";
    node.addEventListener("click", onClick);
  }
  node.innerHTML = `
    <strong>${escapeHtml(title)}</strong>
    <small>${escapeHtml(subtitle || "")}</small>
    ${body ? `<p>${escapeHtml(body)}</p>` : ""}
  `;
  target.appendChild(node);
}

function selectedCabinetIds() {
  return {
    organizationId: state.cabinet?.id || null,
    vereadorId: state.vereador?.id || null,
  };
}

function ensureCabinet() {
  if (!state.cabinet || !state.vereador) {
    throw new Error("Prepare ou carregue o Gabinete Toninho primeiro.");
  }
  return selectedCabinetIds();
}

function renderOverview(data) {
  state.overview = data;
  state.cabinet = data.cabinet.organization;
  state.vereador = data.cabinet.vereador;
  setSelected();
  setMetrics();

  const captures = $("capturesList");
  captures.innerHTML = "";
  if (!data.recent_captures.length) renderEmpty(captures, "Nenhum cadastro politico recente.");
  data.recent_captures.forEach((capture) => {
    renderItem(
      captures,
      capture.full_name,
      `${capture.classification} | ${capture.capture_status} | ${capture.phone || "sem telefone"}`,
      `${capture.district || "sem bairro"} | ${capture.notes || "sem registro"}`,
      toneByStatus(capture.capture_status),
      () => {
        state.capture = capture;
        if (capture.person_id) state.person = { id: capture.person_id, full_name: capture.full_name };
        setSelected();
      },
    );
  });

  const demands = $("demandsList");
  demands.innerHTML = "";
  if (!data.recent_demands.length) renderEmpty(demands, "Nenhuma demanda do gabinete.");
  data.recent_demands.forEach((demand) => {
    renderItem(
      demands,
      demand.title,
      `${demand.category} | ${demand.priority} | ${demand.status}`,
      demand.description,
      toneByStatus(demand.status),
      () => {
        state.demand = demand;
        if (demand.person_id) state.person = { id: demand.person_id, full_name: "Pessoa selecionada" };
        setSelected();
      },
    );
  });

  const tasks = $("tasksList");
  tasks.innerHTML = "";
  if (!data.recent_tasks.length) renderEmpty(tasks, "Nenhuma tarefa do gabinete.");
  data.recent_tasks.forEach((task) => {
    renderItem(
      tasks,
      task.title,
      `${task.task_type} | ${task.priority} | ${task.status}`,
      task.description,
      toneByStatus(task.status),
      () => {
        state.task = task;
        if (task.demand_id && !state.demand) state.demand = data.recent_demands.find((item) => `${item.id}` === `${task.demand_id}`) || null;
        if (task.person_id) state.person = { id: task.person_id, full_name: "Pessoa selecionada" };
        setSelected();
      },
    );
  });

  const events = $("eventsList");
  events.innerHTML = "";
  if (!data.field_events.length) renderEmpty(events, "Nenhuma acao de gabinete registrada.");
  data.field_events.forEach((event) => {
    renderItem(
      events,
      event.title,
      `${event.event_date} | ${event.event_type} | ${event.status}`,
      event.next_action || event.notes,
      toneByStatus(event.status),
    );
  });
}

async function checkHealth() {
  await api("/health", { headers: {} });
  toast("API online");
}

async function login() {
  const data = await api("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({
      username: $("username").value,
      password: $("password").value,
    }),
  });
  state.token = data.access_token;
  localStorage.setItem("revisa.gabinete.token", state.token);
  setSession();
  toast("Acesso liberado");
  await loadToninhoCabinet();
}

async function loadToninhoCabinet() {
  const cabinets = await api("/api/v1/cabinets");
  const found = cabinets.find((item) => {
    const name = `${item.organization?.name || ""} ${item.vereador?.person?.full_name || ""}`.toUpperCase();
    return name.includes("TONINHO") || name.includes("FARMACIA") || name.includes("FARMÁCIA");
  });
  if (!found) throw new Error("Gabinete Toninho ainda nao foi encontrado. Use Preparar Gabinete Toninho.");
  state.cabinet = found.organization;
  state.vereador = found.vereador;
  await refreshAll();
}

async function prepareToninhoCabinet() {
  if (!state.token) throw new Error("Entre no sistema antes de preparar o gabinete.");
  const cabinets = await api("/api/v1/cabinets");
  const existing = cabinets.find((item) => {
    const name = `${item.organization?.name || ""} ${item.vereador?.person?.full_name || ""}`.toUpperCase();
    return name.includes("TONINHO") || name.includes("FARMACIA") || name.includes("FARMÁCIA");
  });
  if (existing) {
    state.cabinet = existing.organization;
    state.vereador = existing.vereador;
    toast("Gabinete Toninho selecionado");
    await refreshAll();
    return;
  }

  const created = await api("/api/v1/cabinets", {
    method: "POST",
    body: JSON.stringify({
      name: "Gabinete Toninho da Farmacia",
      document_number: `GAB-TONINHO-${Date.now()}`,
      vereador_full_name: "Toninho da Farmacia",
      vereador_phone: "31999990000",
    }),
  });
  state.cabinet = created.organization;
  state.vereador = created.vereador;
  toast("Gabinete Toninho preparado");
  await refreshAll();
}

async function refreshAll() {
  if (!state.token) return;
  if (!state.cabinet) {
    await loadToninhoCabinet();
    return;
  }
  const data = await api(`/api/v1/cabinets/${state.cabinet.id}/overview`);
  renderOverview(data);
}

async function createProfile() {
  const { vereadorId } = ensureCabinet();
  const capture = await api("/api/v1/contacts-capture", {
    method: "POST",
    body: JSON.stringify({
      origin: "GABINETE_WEB",
      classification: $("profileType").value,
      vereador_id: vereadorId,
      full_name: $("profileName").value,
      phone: $("profilePhone").value || null,
      district: $("profileDistrict").value || null,
      priority_level: $("profilePriority").value,
      notes: $("profileNotes").value || null,
    }),
  });
  state.capture = capture;
  state.person = capture.person_id ? { id: capture.person_id, full_name: capture.full_name } : null;
  setSelected();
  toast("Cadastro politico registrado");
  await refreshAll();
}

async function convertCaptureToDemand() {
  ensureCabinet();
  if (!state.capture) throw new Error("Selecione ou cadastre um perfil politico.");
  const result = await api(`/api/v1/contacts-capture/${state.capture.id}/convert-demand`, {
    method: "POST",
    body: JSON.stringify({
      category: $("demandCategory").value,
      title: $("demandTitle").value || `Atendimento - ${state.capture.full_name}`,
      description: $("demandDescription").value || state.capture.notes,
      priority: $("demandPriority").value,
    }),
  });
  state.capture = result.capture;
  state.person = result.person;
  state.demand = result.demand;
  setSelected();
  toast("Demanda criada a partir do cadastro");
  await refreshAll();
  await loadTimeline();
}

async function createDemand() {
  const { organizationId, vereadorId } = ensureCabinet();
  const demand = await api("/api/v1/demands", {
    method: "POST",
    body: JSON.stringify({
      organization_id: organizationId,
      vereador_id: vereadorId,
      person_id: state.person?.id || null,
      capture_id: state.capture?.id || null,
      category: $("demandCategory").value,
      title: $("demandTitle").value,
      description: $("demandDescription").value || null,
      priority: $("demandPriority").value,
    }),
  });
  state.demand = demand;
  setSelected();
  toast("Demanda direta registrada");
  await refreshAll();
}

async function createTask() {
  ensureCabinet();
  if (!state.demand) throw new Error("Selecione ou crie uma demanda.");
  const task = await api(`/api/v1/demands/${state.demand.id}/tasks`, {
    method: "POST",
    body: JSON.stringify({
      task_type: "RETORNO_GABINETE",
      title: `Retorno - ${state.demand.title}`,
      description: $("demandDescription").value || state.demand.description,
      priority: state.demand.priority,
    }),
  });
  state.task = task;
  setSelected();
  toast("Tarefa criada para a equipe do gabinete");
  await refreshAll();
}

async function completeTask() {
  if (!state.task) throw new Error("Selecione ou crie uma tarefa.");
  const task = await api(`/api/v1/tasks/${state.task.id}/complete`, {
    method: "POST",
    body: JSON.stringify({
      resolution_notes: $("resolutionNotes").value || null,
      resolve_demand: true,
    }),
  });
  state.task = task;
  if (task.demand_id) {
    state.demand = await api(`/api/v1/demands/${task.demand_id}`);
  }
  setSelected();
  toast("Tarefa concluida e demanda atualizada");
  await refreshAll();
  if (state.person) await loadTimeline();
}

async function classifyProfile() {
  const { organizationId, vereadorId } = ensureCabinet();
  if (!state.person) throw new Error("Converta o cadastro em demanda ou selecione uma pessoa antes de classificar.");
  await api("/api/v1/relationships/classifications", {
    method: "POST",
    body: JSON.stringify({
      person_id: state.person.id,
      organization_id: organizationId,
      vereador_id: vereadorId,
      level: $("profileType").value,
      influence: $("profileInfluence").value,
      engagement: "EM_ACOMPANHAMENTO",
      vote_2028: "NAO_INFORMADO",
      priority: $("profilePriority").value,
      status: "ACTIVE",
      notes: $("profileNotes").value || null,
    }),
  });
  toast("Perfil politico classificado");
}

async function markLeadership() {
  const { organizationId, vereadorId } = ensureCabinet();
  if (!state.person) throw new Error("Converta o cadastro em demanda ou selecione uma pessoa antes de marcar lideranca.");
  await api("/api/v1/relationships/leaderships", {
    method: "POST",
    body: JSON.stringify({
      person_id: state.person.id,
      organization_id: organizationId,
      vereador_id: vereadorId,
      district: $("profileDistrict").value || null,
      leadership_type: $("profileType").value === "APOIADOR" ? "APOIADOR" : "LIDERANCA_COMUNITARIA",
      area_atuacao: "Base politica do gabinete",
      influence_count: 0,
      loyalty_level: $("profileInfluence").value,
      active: true,
      notes: $("profileNotes").value || null,
    }),
  });
  toast("Lideranca registrada na base politica");
}

async function createEvent() {
  const { organizationId } = ensureCabinet();
  const event = await api("/api/v1/relationships/field-events", {
    method: "POST",
    body: JSON.stringify({
      organization_id: organizationId,
      title: $("eventTitle").value,
      district: $("eventDistrict").value || null,
      event_type: $("eventType").value,
      event_date: $("eventDate").value || today(),
      status: "PLANNED",
      expected_people: Number($("eventExpected").value || 0),
      next_action: $("eventNextAction").value || null,
      notes: "Acao registrada pelo Modulo Gabinete.",
    }),
  });
  toast(`Acao registrada: ${event.title}`);
  await refreshAll();
}

function renderTimeline(data) {
  $("timelineSummary").innerHTML = `
    <p><strong>${escapeHtml(data.person.full_name)}</strong> - ${escapeHtml(data.summary.journey_status)}</p>
    <p class="muted">Demandas abertas: ${data.summary.open_demands} | Tarefas abertas: ${data.summary.open_tasks} | Polo: ${escapeHtml(data.summary.current_polo?.code || "sem vinculo")}</p>
  `;
  const list = $("timelineList");
  list.innerHTML = "";
  if (!data.items.length) {
    renderEmpty(list, "Sem eventos na jornada desta pessoa.");
    return;
  }
  data.items.forEach((entry) => {
    const node = document.createElement("article");
    node.className = "timeline-item";
    node.dataset.tone = toneByStatus(entry.status || entry.type);
    node.innerHTML = `
      <small>${escapeHtml(entry.occurred_at)} | ${escapeHtml(entry.type)}${entry.status ? ` | ${escapeHtml(entry.status)}` : ""}</small>
      <strong>${escapeHtml(entry.title)}</strong>
      ${entry.description ? `<p>${escapeHtml(entry.description)}</p>` : ""}
    `;
    list.appendChild(node);
  });
}

async function loadTimeline() {
  if (!state.person) throw new Error("Selecione uma pessoa para carregar a jornada.");
  const data = await api(`/api/v1/persons/${state.person.id}/timeline`);
  renderTimeline(data);
  toast("Jornada carregada");
}

function bind(id, handler) {
  $(id).addEventListener("click", async () => {
    try {
      await handler();
    } catch (error) {
      toast(error.message);
    }
  });
}

bind("healthBtn", checkHealth);
bind("loginBtn", login);
bind("prepareCabinetBtn", prepareToninhoCabinet);
bind("refreshBtn", refreshAll);
bind("createProfileBtn", createProfile);
bind("convertDemandBtn", convertCaptureToDemand);
bind("createDemandBtn", createDemand);
bind("createTaskBtn", createTask);
bind("completeTaskBtn", completeTask);
bind("classifyProfileBtn", classifyProfile);
bind("leadershipBtn", markLeadership);
bind("createEventBtn", createEvent);
bind("timelineBtn", loadTimeline);

$("eventDate").value = today();
setSession();
setSelected();
setMetrics();
if (state.token) {
  loadToninhoCabinet().catch(() => {});
}
