const state = {
  token: localStorage.getItem("revisa.gabinete.token") || "",
  cabinet: null,
  vereador: null,
  capture: null,
  person: null,
  demand: null,
  task: null,
  overview: null,
  reportRows: [],
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

  renderCabinetReports();
}

function reportDate(value) {
  return value ? `${value}`.slice(0, 10) : "";
}

function userLabel(userId) {
  if (!userId) return "Nao informado";
  return `${userId}`.slice(0, 8);
}

function csvCell(value) {
  return `"${`${value ?? ""}`.replace(/"/g, '""')}"`;
}

function downloadText(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function buildCabinetReportRows() {
  const overview = state.overview || {};
  const rows = [];
  const add = (row) => rows.push({
    tipo: row.tipo,
    titulo: row.titulo,
    status: row.status || "",
    categoria: row.categoria || "",
    bairro: row.bairro || "",
    data: reportDate(row.data),
    observacao: row.observacao || "",
  });
  (overview.recent_captures || []).forEach((capture) => add({
    tipo: "captures",
    titulo: capture.full_name,
    status: capture.capture_status,
    categoria: capture.classification,
    bairro: capture.district,
    data: capture.created_at,
    observacao: capture.notes || capture.phone,
  }));
  (overview.recent_demands || []).forEach((demand) => add({
    tipo: "demands",
    titulo: demand.title,
    status: demand.status,
    categoria: demand.category,
    data: demand.created_at,
    observacao: `${demand.priority} | ${demand.description || ""}`,
  }));
  (overview.recent_tasks || []).forEach((task) => add({
    tipo: "tasks",
    titulo: task.title,
    status: task.status,
    categoria: task.task_type,
    data: task.created_at,
    observacao: `${task.priority} | ${task.description || ""}`,
  }));
  (overview.field_events || []).forEach((event) => add({
    tipo: "events",
    titulo: event.title,
    status: event.status,
    categoria: event.event_type,
    bairro: event.district,
    data: event.event_date,
    observacao: event.next_action || event.notes,
  }));
  const productivity = {};
  const countFor = (userId, field) => {
    const key = userLabel(userId);
    productivity[key] = productivity[key] || { captures: 0, demands: 0, tasks: 0, completed: 0, events: 0 };
    productivity[key][field] += 1;
  };
  (overview.recent_captures || []).forEach((capture) => countFor(capture.captured_by_user_id, "captures"));
  (overview.recent_demands || []).forEach((demand) => countFor(demand.opened_by_user_id, "demands"));
  (overview.recent_tasks || []).forEach((task) => {
    countFor(task.created_by_user_id, "tasks");
    if (task.status === "COMPLETED") countFor(task.assigned_to_user_id || task.created_by_user_id, "completed");
  });
  (overview.field_events || []).forEach((event) => countFor(event.created_by_user_id, "events"));
  Object.entries(productivity).forEach(([user, total]) => add({
    tipo: "productivity",
    titulo: `Usuario ${user}`,
    status: "CONSOLIDADO",
    categoria: "Produtividade",
    observacao: `${total.captures} cadastros | ${total.demands} demandas | ${total.tasks} tarefas | ${total.completed} concluidas | ${total.events} acoes`,
  }));
  const territory = {};
  const countDistrict = (district, field) => {
    const key = district || "Sem bairro";
    territory[key] = territory[key] || { captures: 0, demands: 0, events: 0, leaders: 0 };
    territory[key][field] += 1;
  };
  (overview.recent_captures || []).forEach((capture) => countDistrict(capture.district, "captures"));
  (overview.recent_demands || []).forEach((demand) => {
    const capture = (overview.recent_captures || []).find((item) => `${item.id}` === `${demand.capture_id}`);
    countDistrict(capture?.district, "demands");
  });
  (overview.field_events || []).forEach((event) => countDistrict(event.district, "events"));
  Object.entries(territory).forEach(([district, total]) => add({
    tipo: "territory",
    titulo: district,
    status: "CONSOLIDADO",
    categoria: "Mapa territorial",
    bairro: district,
    observacao: `${total.captures} cadastros | ${total.demands} demandas | ${total.events} acoes`,
  }));
  return rows;
}

function setCabinetReportStatusOptions(rows) {
  const current = $("cabinetReportStatus").value;
  const statuses = [...new Set(rows.map((row) => row.status).filter(Boolean))].sort();
  $("cabinetReportStatus").innerHTML = '<option value="">Todos</option>' + statuses
    .map((status) => `<option value="${escapeHtml(status)}">${escapeHtml(status)}</option>`)
    .join("");
  if (statuses.includes(current)) $("cabinetReportStatus").value = current;
}

function filteredCabinetReportRows() {
  const rows = buildCabinetReportRows();
  setCabinetReportStatusOptions(rows);
  const type = $("cabinetReportType").value;
  const status = $("cabinetReportStatus").value;
  const district = $("cabinetReportDistrict").value.trim().toLowerCase();
  const start = $("cabinetReportStart").value;
  const end = $("cabinetReportEnd").value;
  return rows.filter((row) => {
    if (type !== "all" && row.tipo !== type) return false;
    if (status && row.status !== status) return false;
    if (district && !`${row.bairro}`.toLowerCase().includes(district)) return false;
    if (start && row.data && row.data < start) return false;
    if (end && row.data && row.data > end) return false;
    return true;
  });
}

function renderCabinetReports() {
  const rows = filteredCabinetReportRows();
  state.reportRows = rows;
  $("cabinetReportSummary").innerHTML = `
    <div class="report-kpis">
      <article><strong>${rows.length}</strong><span>Registros</span></article>
      <article><strong>${state.overview?.metrics?.captures || 0}</strong><span>Cadastros</span></article>
      <article><strong>${state.overview?.metrics?.open_demands || 0}</strong><span>Demandas abertas</span></article>
      <article><strong>${state.overview?.metrics?.open_tasks || 0}</strong><span>Tarefas abertas</span></article>
    </div>
  `;
  if (!rows.length) {
    $("cabinetReportTable").innerHTML = '<p class="muted">Sem registros para os filtros selecionados.</p>';
    return;
  }
  $("cabinetReportTable").innerHTML = `
    <table>
      <thead><tr><th>Relatorio</th><th>Titulo</th><th>Status</th><th>Categoria</th><th>Bairro</th><th>Periodo</th><th>Observacao</th></tr></thead>
      <tbody>
        ${rows.map((row) => `<tr><td>${escapeHtml(row.tipo)}</td><td>${escapeHtml(row.titulo)}</td><td>${escapeHtml(row.status)}</td><td>${escapeHtml(row.categoria)}</td><td>${escapeHtml(row.bairro || "-")}</td><td>${escapeHtml(row.data || "-")}</td><td>${escapeHtml(row.observacao || "-")}</td></tr>`).join("")}
      </tbody>
    </table>
  `;
}

function exportCabinetReportCsv() {
  if (!state.reportRows.length) throw new Error("Aplique filtros com registros antes de exportar.");
  const header = ["relatorio", "titulo", "status", "categoria", "bairro", "periodo", "observacao"];
  const lines = state.reportRows.map((row) => [row.tipo, row.titulo, row.status, row.categoria, row.bairro, row.data, row.observacao].map(csvCell).join(";"));
  downloadText([header.map(csvCell).join(";"), ...lines].join("\n"), "relatorio-gabinete.csv", "text/csv;charset=utf-8");
  toast("CSV do Gabinete exportado");
}

function printCabinetReportPdf() {
  if (!state.reportRows.length) throw new Error("Aplique filtros com registros antes de gerar PDF.");
  const popup = window.open("", "_blank");
  if (!popup) throw new Error("Permita pop-ups para gerar o PDF.");
  popup.document.write(`
    <!doctype html><html lang="pt-BR"><head><meta charset="utf-8" /><title>Relatorio do Gabinete</title>
    <style>body{font-family:Arial,Helvetica,sans-serif;color:#17201b;margin:24px}table{width:100%;border-collapse:collapse;font-size:12px}th,td{border:1px solid #d7dfd9;padding:6px;text-align:left;vertical-align:top}th{background:#f2f7f5}</style></head>
    <body><h1>Relatorio do Gabinete</h1><p>${escapeHtml(state.cabinet?.name || "Gabinete")} | ${state.reportRows.length} registros | ${new Date().toLocaleString("pt-BR")}</p>
    <table><thead><tr><th>Relatorio</th><th>Titulo</th><th>Status</th><th>Categoria</th><th>Bairro</th><th>Periodo</th><th>Observacao</th></tr></thead>
    <tbody>${state.reportRows.map((row) => `<tr><td>${escapeHtml(row.tipo)}</td><td>${escapeHtml(row.titulo)}</td><td>${escapeHtml(row.status)}</td><td>${escapeHtml(row.categoria)}</td><td>${escapeHtml(row.bairro)}</td><td>${escapeHtml(row.data)}</td><td>${escapeHtml(row.observacao)}</td></tr>`).join("")}</tbody></table></body></html>
  `);
  popup.document.close();
  popup.focus();
  popup.print();
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
bind("cabinetReportRunBtn", renderCabinetReports);
bind("cabinetReportCsvBtn", exportCabinetReportCsv);
bind("cabinetReportPdfBtn", printCabinetReportPdf);

["cabinetReportType", "cabinetReportStatus", "cabinetReportDistrict", "cabinetReportStart", "cabinetReportEnd"].forEach((id) => {
  const eventName = id === "cabinetReportDistrict" ? "input" : "change";
  $(id).addEventListener(eventName, renderCabinetReports);
});

$("eventDate").value = today();
setSession();
setSelected();
setMetrics();
renderCabinetReports();
if (state.token) {
  loadToninhoCabinet().catch(() => {});
}
