const state = {
  token: localStorage.getItem("revisa.token") || "",
  currentUser: null,
  activeModule: "overview",
  capture: null,
  person: null,
  demand: null,
  task: null,
  organization: null,
  polo: null,
  beneficiary: null,
  cabinet: null,
  vereador: null,
  fundingSource: null,
  financialMovement: null,
  purchaseRequest: null,
  purchaseAlerts: null,
  fundingSources: [],
  budgetItems: [],
  purchaseRequests: [],
  staffContracts: [],
  permanentAssets: [],
  monthlyReports: [],
  actionPlans: [],
  staffContract: null,
  accountabilityReport: null,
  timeline: null,
  poloOverview: null,
  cabinetOverview: null,
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
  const base = apiBase();
  const url = `${base}${path}`;
  const response = await fetch(url, {
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
    if (response.status === 404 && text.includes("File not found")) {
      throw new Error("A caixa API esta apontando para o frontend. Use http://127.0.0.1:8001.");
    }
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

function shortId(value) {
  return value ? `${value}`.slice(0, 8) : "nenhum";
}

function isUuid(value) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(`${value}`.trim());
}

function requireUuid(value, label) {
  const clean = `${value || ""}`.trim();
  if (!isUuid(clean)) throw new Error(`${label} precisa ser um UUID valido. Use o botao Preparar demo para preencher automaticamente.`);
  return clean;
}

function formatValidationError(detail) {
  const first = detail[0];
  const field = Array.isArray(first?.loc) ? first.loc.filter((part) => part !== "body").join(".") : "campo";
  if (first?.type?.includes("uuid") || first?.msg?.toLowerCase().includes("uuid")) {
    return `${field} precisa ser um UUID valido. Use Preparar demo ou selecione um registro da lista.`;
  }
  return first?.msg || "Dados invalidos para esta operacao.";
}

function formatDate(value) {
  if (!value) return "sem data";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function setSession() {
  $("sessionState").textContent = state.token ? "Sessao ativa" : "Sessao pendente";
}

function setApiStatus(ok) {
  $("apiStatus").textContent = ok ? "online" : "offline";
  $("apiStatus").classList.toggle("ok", ok);
}

function roles() {
  return new Set(state.currentUser?.roles || []);
}

function permissions() {
  return new Set(state.currentUser?.permissions || []);
}

function hasRole(role) {
  return roles().has(role);
}

function hasPermission(permission) {
  return permissions().has(permission) || hasRole("ADM_GERAL_REVISA") || hasRole("ADM_REVISA");
}

function hasAnyPermission(list) {
  return list.some((permission) => hasPermission(permission));
}

function isRevisaAdmin() {
  return hasRole("ADM_GERAL_REVISA") || hasRole("ADM_REVISA");
}

function canAccessModule(module) {
  if (!state.currentUser) return module === "overview";
  if (module === "overview") return true;
  if (isRevisaAdmin()) return true;
  if (module === "finance") {
    return hasAnyPermission([
      "administration.read",
      "administration.manage_finance",
      "administration.manage_purchase",
      "administration.manage_staff",
      "administration.manage_contract",
    ]);
  }
  if (module === "polo") {
    return hasAnyPermission(["polo.read", "dashboard.polo.read", "purchase_request.read", "administration.read"]);
  }
  if (module === "cabinet") {
    return hasAnyPermission(["cabinet.read", "cabinet.action.read", "dashboard.cabinet.read"]);
  }
  if (module === "territory") {
    return hasAnyPermission(["person.read", "capture.read", "demand.read", "task.read", "event.read"]);
  }
  if (module === "monitoring") {
    return hasAnyPermission(["report.read", "report.export", "audit.read", "dashboard.admin.read", "dashboard.polo.read"]);
  }
  return false;
}

function accessProfile() {
  if (!state.currentUser) {
    return {
      name: "Aguardando login",
      description: "A visao do sistema sera montada conforme as permissoes do usuario.",
    };
  }
  if (isRevisaAdmin()) {
    return {
      name: "Administrador REVISA",
      description: "Acesso maximo: operacao de cadastramento, gabinete, Polos, gestao financeira, relatorios, edicao e acompanhamento integral.",
    };
  }
  if (hasRole("AUXILIAR_ADM_REVISA") || hasRole("COLABORADOR_REVISA")) {
    return {
      name: "Auxiliar administrativo REVISA",
      description: "Acesso operacional para acompanhamento das rotinas dos Polos, requisicoes, compras, relatorios mensais, ocorrencias e demandas.",
    };
  }
  if (hasRole("GESTOR_RH")) {
    return {
      name: "Gestor RH",
      description: "Acesso a pessoal, contratos, rotinas da REVISA e dos Polos, sem visualizacao do Modulo Gabinete.",
    };
  }
  if (hasRole("GESTOR_FINANCEIRO")) {
    return {
      name: "Gestor financeiro",
      description: "Acesso a captacoes, Plano de Trabalho, compras, patrimonio, prestacao de contas e rotinas dos Polos, sem visualizacao do Modulo Gabinete.",
    };
  }
  if (hasRole("ADM_POLO") || hasRole("COORDENADOR_POLO")) {
    return {
      name: "Gestao do Polo",
      description: "Acesso a beneficiarios, modalidades, frequencias, ocorrencias, requisicoes, relatorios mensais e Planos de Acao do Polo permitido.",
    };
  }
  if (hasRole("CHEFE_GABINETE") || hasRole("VEREADOR") || hasRole("COLABORADOR_GABINETE")) {
    return {
      name: "Gabinete",
      description: "Acesso restrito ao gabinete, carteira politica, cadastramento, demandas, tarefas, agenda e relatorios permitidos.",
    };
  }
  return {
    name: state.currentUser.username || "Usuario",
    description: "Acesso conforme permissoes atribuidas ao usuario.",
  };
}

function applyAccessControls() {
  if (!canAccessModule(state.activeModule)) state.activeModule = "overview";
  const profile = accessProfile();
  $("accessProfileName").textContent = profile.name;
  $("accessProfileDescription").textContent = profile.description;

  const availableModules = [
    ["finance", "Gestao financeira"],
    ["polo", "Polos"],
    ["territory", "Atendimento"],
    ["cabinet", "Gabinete"],
    ["monitoring", "Relatorios"],
  ].filter(([module]) => canAccessModule(module));
  const scopes = state.currentUser?.scopes || {};
  const scopeCount = Object.values(scopes).reduce((total, items) => total + items.length, 0);
  $("accessChips").innerHTML = state.currentUser
    ? [
        ...availableModules.map(([, label]) => `<span>${escapeHtml(label)}</span>`),
        `<span>${scopeCount ? `${scopeCount} escopo(s)` : "Escopo global ou nao informado"}</span>`,
      ].join("")
    : "<span>Sem sessao</span>";

  document.querySelectorAll("[data-module]").forEach((node) => {
    const module = node.dataset.module;
    node.classList.toggle("is-hidden", !canAccessModule(module) || module !== state.activeModule);
  });
  document.querySelectorAll("[data-nav-module]").forEach((node) => {
    node.classList.toggle("is-hidden", !canAccessModule(node.dataset.navModule));
  });
  document.querySelectorAll("[data-permission]").forEach((node) => {
    node.classList.toggle("is-hidden", !hasPermission(node.dataset.permission));
  });

  document.querySelectorAll(".side-menu a").forEach((node) => node.classList.remove("active"));
  const activeNav = document.querySelector(`.side-menu a[data-nav-module="${state.activeModule}"]:not(.is-hidden)`);
  if (activeNav) activeNav.classList.add("active");
}

function setSelected() {
  $("selectedCapture").textContent = state.capture ? `${shortId(state.capture.id)} - ${state.capture.full_name}` : "nenhuma";
  $("selectedDemand").textContent = state.demand ? `${shortId(state.demand.id)} - ${state.demand.status}` : "nenhuma";
  $("selectedTask").textContent = state.task ? `${shortId(state.task.id)} - ${state.task.status}` : "nenhuma";
  $("selectedFunding").textContent = state.fundingSource ? `${shortId(state.fundingSource.id)} - ${state.fundingSource.name}` : "nenhuma";
  $("selectedMovement").textContent = state.financialMovement ? `${shortId(state.financialMovement.id)} - ${state.financialMovement.movement_type}` : "nenhum";
  $("selectedPurchase").textContent = state.purchaseRequest ? `${shortId(state.purchaseRequest.id)} - ${state.purchaseRequest.status}` : "nenhuma";
  $("selectedStaff").textContent = state.staffContract ? `${shortId(state.staffContract.id)} - ${state.staffContract.status}` : "nenhum";

  if (state.person) $("poloPersonId").value = state.person.id;
  if (state.polo) $("poloId").value = state.polo.id;
  if (state.organization) $("poloOrganizationId").value = state.organization.id;
  if (state.vereador) $("poloVereadorId").value = state.vereador.id;
}

function setPersonFromRow(row) {
  if (row?.person_id) {
    state.person = {
      id: row.person_id,
      full_name: row.full_name || row.title || "Pessoa selecionada",
    };
  }
}

function item(title, subtitle, status, onClick) {
  const node = document.createElement("button");
  node.type = "button";
  node.className = "item";
  node.dataset.status = status || "";
  node.innerHTML = `<strong>${escapeHtml(title)}</strong><small>${escapeHtml(subtitle || "")}</small>`;
  node.addEventListener("click", onClick);
  return node;
}

function escapeHtml(value) {
  return `${value ?? ""}`.replace(/[&<>"']/g, (char) => {
    const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
    return map[char];
  });
}

function renderList(id, rows, build) {
  const target = $(id);
  target.innerHTML = "";
  if (!rows.length) {
    target.innerHTML = '<p class="muted">Sem registros</p>';
    return;
  }
  rows.forEach((row) => target.appendChild(build(row)));
}

function renderTimeline(data) {
  state.timeline = data;
  const summary = data.summary;
  $("timelineSummary").innerHTML = `
    <p><strong>${escapeHtml(data.person.full_name)}</strong> - ${escapeHtml(summary.journey_status)}</p>
    <p class="muted">Polo: ${escapeHtml(summary.current_polo?.code || "sem polo")} | Beneficiario: ${escapeHtml(summary.beneficiary_status || "sem vinculo")} | Demandas abertas: ${summary.open_demands} | Tarefas abertas: ${summary.open_tasks}</p>
  `;

  const list = $("timelineList");
  list.innerHTML = "";
  if (!data.items.length) {
    list.innerHTML = '<p class="muted">Sem eventos registrados</p>';
    return;
  }
  data.items.forEach((entry) => {
    const node = document.createElement("article");
    node.className = "timeline-item";
    node.dataset.type = entry.type;
    node.innerHTML = `
      <span>${escapeHtml(formatDate(entry.occurred_at))}</span>
      <strong>${escapeHtml(entry.title)}</strong>
      <small>${escapeHtml(entry.type)}${entry.status ? ` - ${escapeHtml(entry.status)}` : ""}</small>
      ${entry.description ? `<p>${escapeHtml(entry.description)}</p>` : ""}
    `;
    list.appendChild(node);
  });
}

function renderPoloOverview(data) {
  state.poloOverview = data;
  const metrics = data.metrics;
  $("poloOverviewSummary").innerHTML = `
    <div class="polo-kpis">
      <article><strong>${metrics.total_beneficiarios}</strong><span>Beneficiarios</span></article>
      <article><strong>${metrics.active_beneficiarios}</strong><span>Ativos</span></article>
      <article><strong>${metrics.present_records}</strong><span>Presencas</span></article>
      <article><strong>${metrics.open_occurrences}</strong><span>Ocorrencias abertas</span></article>
      <article><strong>${metrics.planned_events}</strong><span>Eventos planejados</span></article>
    </div>
    <p class="muted">Polo ${escapeHtml(data.polo.code || shortId(data.polo.id))} | ${escapeHtml(data.polo.address_label || "sem endereco")}</p>
  `;

  const beneficiaries = data.beneficiaries.map((beneficiary) => `
    <article class="ops-item">
      <strong>${shortId(beneficiary.person_id)}</strong>
      <small>${escapeHtml(beneficiary.status)} | ${shortId(beneficiary.id)}</small>
    </article>
  `).join("");
  const occurrences = data.recent_occurrences.map((occurrence) => `
    <article class="ops-item">
      <strong>${escapeHtml(occurrence.title)}</strong>
      <small>${escapeHtml(occurrence.severity)} | ${escapeHtml(occurrence.status)}</small>
    </article>
  `).join("");
  const events = data.field_events.map((event) => `
    <article class="ops-item">
      <strong>${escapeHtml(event.title)}</strong>
      <small>${escapeHtml(event.event_type)} | ${escapeHtml(event.status)} | ${escapeHtml(event.event_date)}</small>
    </article>
  `).join("");

  $("poloOverviewLists").innerHTML = `
    <article><h3>Beneficiarios</h3>${beneficiaries || '<p class="muted">Sem beneficiarios</p>'}</article>
    <article><h3>Ocorrencias</h3>${occurrences || '<p class="muted">Sem ocorrencias</p>'}</article>
    <article><h3>Eventos</h3>${events || '<p class="muted">Sem eventos</p>'}</article>
  `;
}

function renderCabinetOverview(data) {
  state.cabinetOverview = data;
  state.cabinet = data.cabinet.organization;
  state.vereador = data.cabinet.vereador;
  const metrics = data.metrics;
  $("cabinetOverviewSummary").innerHTML = `
    <div class="cabinet-kpis">
      <article><strong>${metrics.linked_people}</strong><span>Carteira</span></article>
      <article><strong>${metrics.captures}</strong><span>Captacoes</span></article>
      <article><strong>${metrics.demands}</strong><span>Demandas</span></article>
      <article><strong>${metrics.open_demands}</strong><span>Demandas abertas</span></article>
      <article><strong>${metrics.tasks}</strong><span>Tarefas</span></article>
      <article><strong>${metrics.open_tasks}</strong><span>Tarefas abertas</span></article>
      <article><strong>${metrics.planned_events}</strong><span>Agenda</span></article>
    </div>
    <p class="muted">${escapeHtml(data.cabinet.organization.name)} | ${escapeHtml(data.cabinet.vereador.person?.full_name || "vereador sem pessoa")}</p>
  `;

  const captures = data.recent_captures.map((capture) => `
    <article class="ops-item">
      <strong>${escapeHtml(capture.full_name)}</strong>
      <small>${escapeHtml(capture.capture_status)} | ${escapeHtml(capture.phone || "sem telefone")}</small>
    </article>
  `).join("");
  const demands = data.recent_demands.map((demand) => `
    <article class="ops-item">
      <strong>${escapeHtml(demand.title)}</strong>
      <small>${escapeHtml(demand.status)} | ${escapeHtml(demand.priority)}</small>
    </article>
  `).join("");
  const tasks = data.recent_tasks.map((task) => `
    <article class="ops-item">
      <strong>${escapeHtml(task.title)}</strong>
      <small>${escapeHtml(task.status)} | ${escapeHtml(task.task_type)}</small>
    </article>
  `).join("");
  const events = data.field_events.map((event) => `
    <article class="ops-item">
      <strong>${escapeHtml(event.title)}</strong>
      <small>${escapeHtml(event.event_type)} | ${escapeHtml(event.status)} | ${escapeHtml(event.event_date)}</small>
    </article>
  `).join("");

  $("cabinetOverviewLists").innerHTML = `
    <article><h3>Captacoes</h3>${captures || '<p class="muted">Sem captacoes</p>'}</article>
    <article><h3>Demandas</h3>${demands || '<p class="muted">Sem demandas</p>'}</article>
    <article><h3>Tarefas</h3>${tasks || '<p class="muted">Sem tarefas</p>'}</article>
    <article><h3>Agenda</h3>${events || '<p class="muted">Sem agenda</p>'}</article>
  `;
}

function formatMoney(value) {
  const number = Number(value || 0);
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(number);
}

function accountabilityQuery() {
  const params = new URLSearchParams();
  if (state.fundingSource?.id) {
    params.set("funding_source_id", state.fundingSource.id);
  } else if (state.vereador?.id) {
    params.set("vereador_id", state.vereador.id);
  }
  if (state.polo?.id) params.set("polo_id", state.polo.id);
  return params.toString();
}

function fundingLabel(funding) {
  return funding ? `${funding.name} | ${funding.source_type} | ${funding.appropriation_number || "sem identificador"}` : "Captacao nao selecionada";
}

function isParliamentarySource(sourceType) {
  return ["EMENDA_IMPOSITIVA", "EMENDA_PARLAMENTAR", "PROJETO_GABINETE"].includes(sourceType);
}

function renderAccountabilityReport(data) {
  state.accountabilityReport = data;
  const totals = data.totals;
  $("accountabilitySummary").innerHTML = `
    <div class="accountability-kpis">
      <article><strong>${escapeHtml(formatMoney(totals.deposited_amount))}</strong><span>Depositado</span></article>
      <article><strong>${escapeHtml(formatMoney(totals.movement_inflows))}</strong><span>Entradas</span></article>
      <article><strong>${escapeHtml(formatMoney(totals.movement_outflows))}</strong><span>Pagamentos</span></article>
      <article><strong>${escapeHtml(formatMoney(totals.staff_monthly_payroll))}</strong><span>Folha mensal</span></article>
      <article><strong>${escapeHtml(formatMoney(totals.available_balance))}</strong><span>Saldo</span></article>
    </div>
  `;

  const movements = data.financial_movements.map((movement) => `
    <article class="ops-item">
      <strong>${escapeHtml(movement.description)}</strong>
      <small>${escapeHtml(movement.movement_type)} | ${escapeHtml(formatMoney(movement.amount))} | ${escapeHtml(movement.document_ref || "sem anexo")}</small>
    </article>
  `).join("");
  const purchases = data.purchase_requests.map((purchase) => `
    <article class="ops-item">
      <strong>${escapeHtml(purchase.description)}</strong>
      <small>${escapeHtml(purchase.status)} | ${escapeHtml(formatMoney(purchase.approved_amount || purchase.estimated_amount || 0))} | ${escapeHtml(purchase.document_ref || "sem anexo")}</small>
    </article>
  `).join("");
  const staff = data.staff_contracts.map((contract) => `
    <article class="ops-item">
      <strong>${escapeHtml(contract.role_title)}</strong>
      <small>${escapeHtml(contract.status)} | ${escapeHtml(formatMoney(contract.salary_amount))} | ${escapeHtml(contract.contract_type)}</small>
    </article>
  `).join("");
  const docs = data.fiscal_documents.map((document) => `
    <article class="ops-item">
      <strong>${escapeHtml(document.document_ref)}</strong>
      <small>${escapeHtml(document.source)} | ${shortId(document.entity_id)}</small>
    </article>
  `).join("");

  $("accountabilityLists").innerHTML = `
    <article><h3>Movimentos</h3>${movements || '<p class="muted">Sem movimentos</p>'}</article>
    <article><h3>Compras</h3>${purchases || '<p class="muted">Sem compras</p>'}</article>
    <article><h3>Pessoal</h3>${staff || '<p class="muted">Sem contratos</p>'}</article>
    <article><h3>Anexos</h3>${docs || '<p class="muted">Sem anexos</p>'}</article>
  `;
}

function renderPurchaseAlerts(data) {
  state.purchaseAlerts = data;
  const rows = data.purchase_requests.map((request) => `
    <article class="ops-item">
      <strong>${escapeHtml(request.description)}</strong>
      <small>${escapeHtml(request.category)} | ${escapeHtml(request.status)} | Polo ${shortId(request.polo_id)} | ${request.items?.length || 0} itens</small>
    </article>
  `).join("");
  $("purchaseAlertsSummary").innerHTML = `
    <div class="accountability-kpis">
      <article><strong>${data.open_purchase_requests}</strong><span>Requisicoes abertas</span></article>
    </div>
    ${rows || '<p class="muted">Sem requisicoes de compras abertas.</p>'}
  `;
}

function renderPermanentAssets(data) {
  state.permanentAssets = data;
  const rows = data.map((asset) => `
    <article class="ops-item">
      <strong>${escapeHtml(asset.asset_number)}</strong>
      <small>${escapeHtml(asset.status)} | Polo ${shortId(asset.polo_id)} | ${escapeHtml(asset.location_label || "sem local")}</small>
      <p>${escapeHtml(asset.description)}${asset.brand ? ` | ${escapeHtml(asset.brand)}` : ""}</p>
    </article>
  `).join("");
  $("assetSummary").innerHTML = rows || '<p class="muted">Sem bens permanentes registrados.</p>';
}

function renderMonthlyReports(data) {
  state.monthlyReports = data;
  const rows = data.map((report) => `
    <article class="ops-item">
      <strong>Relatorio ${escapeHtml(report.reference_month.slice(0, 7))}</strong>
      <small>${escapeHtml(report.status)} | Polo ${shortId(report.polo_id)} | ${report.active_modalities_count} modalidades | ${report.attachments?.length || 0} anexos</small>
      <p>${escapeHtml((report.narrative_text || "").slice(0, 260))}</p>
    </article>
  `).join("");
  $("monthlyReportsSummary").innerHTML = rows || '<p class="muted">Sem relatorios mensais enviados.</p>';
}

function renderActionPlans(data) {
  state.actionPlans = data;
  const rows = data.map((plan) => `
    <article class="ops-item">
      <strong>${escapeHtml(plan.title)}</strong>
      <small>Ano Base ${escapeHtml(plan.base_year)} | Polo ${shortId(plan.polo_id)} | Modalidade ${shortId(plan.modalidade_id)} | ${escapeHtml(plan.status)}</small>
      <p>${escapeHtml(plan.professional_name || plan.original_filename)}</p>
    </article>
  `).join("");
  $("actionPlansSummary").innerHTML = rows || '<p class="muted">Sem Planos de Acao enviados.</p>';
}

function renderManagementOverview() {
  const openPurchases = state.purchaseRequests.filter((request) => request.status !== "CLOSED");
  const activeStaff = state.staffContracts.filter((contract) => contract.status === "ACTIVE");
  const currentYear = new Date().getFullYear();
  const currentYearPlans = state.actionPlans.filter((plan) => Number(plan.base_year) === currentYear);
  const estimatedTotal = state.fundingSources.reduce((total, funding) => total + Number(funding.estimated_amount || 0), 0);
  const depositedTotal = state.fundingSources.reduce((total, funding) => total + Number(funding.deposited_amount || 0), 0);
  const plannedTotal = state.budgetItems.reduce((total, item) => total + Number(item.planned_amount || 0), 0);
  const plannedBalance = depositedTotal - plannedTotal;

  $("managementSummary").innerHTML = `
    <div class="accountability-kpis">
      <article><strong>${escapeHtml(formatMoney(estimatedTotal))}</strong><span>Captacoes aprovadas</span></article>
      <article><strong>${escapeHtml(formatMoney(depositedTotal))}</strong><span>Depositado</span></article>
      <article><strong>${escapeHtml(formatMoney(plannedTotal))}</strong><span>Plano de Trabalho</span></article>
      <article><strong>${escapeHtml(formatMoney(plannedBalance))}</strong><span>Saldo apos despesas iniciais</span></article>
      <article><strong>${openPurchases.length}</strong><span>Compras em andamento</span></article>
      <article><strong>${currentYearPlans.length}</strong><span>Planos ${currentYear}</span></article>
    </div>
  `;

  const fundingRows = state.fundingSources.slice(0, 8).map((funding) => `
    <article class="ops-item">
      <strong>${escapeHtml(funding.name)}</strong>
      <small>${escapeHtml(funding.status)} | ${escapeHtml(funding.appropriation_number || "sem numero")} | ${escapeHtml(formatMoney(funding.deposited_amount))}</small>
    </article>
  `).join("");
  const purchaseRows = openPurchases.slice(0, 8).map((purchase) => `
    <article class="ops-item">
      <strong>${escapeHtml(purchase.description)}</strong>
      <small>${escapeHtml(purchase.category)} | ${escapeHtml(purchase.status)} | Polo ${shortId(purchase.polo_id)} | ${purchase.items?.length || 0} itens</small>
    </article>
  `).join("");
  const budgetRows = state.budgetItems.slice(0, 8).map((budget) => `
    <article class="ops-item">
      <strong>${escapeHtml(budget.description)}</strong>
      <small>${escapeHtml(budget.category)} | ${escapeHtml(budget.status)} | ${escapeHtml(formatMoney(budget.planned_amount))}</small>
    </article>
  `).join("");
  const staffRows = activeStaff.slice(0, 8).map((contract) => `
    <article class="ops-item">
      <strong>${escapeHtml(contract.role_title)}</strong>
      <small>${escapeHtml(contract.contract_type)} | ${escapeHtml(formatMoney(contract.salary_amount))} | Polo ${shortId(contract.polo_id)}</small>
    </article>
  `).join("");
  const planRows = state.actionPlans.slice(0, 8).map((plan) => `
    <article class="ops-item">
      <strong>${escapeHtml(plan.title)}</strong>
      <small>Ano Base ${escapeHtml(plan.base_year)} | Polo ${shortId(plan.polo_id)} | ${escapeHtml(plan.status)}</small>
    </article>
  `).join("");

  $("managementLists").innerHTML = `
    <article><h3>Captacoes</h3>${fundingRows || '<p class="muted">Sem captacoes cadastradas</p>'}</article>
    <article><h3>Plano de Trabalho</h3>${budgetRows || '<p class="muted">Sem itens planejados</p>'}</article>
    <article><h3>Compras</h3>${purchaseRows || '<p class="muted">Sem compras abertas</p>'}</article>
    <article><h3>Pessoal</h3>${staffRows || '<p class="muted">Sem contratos ativos</p>'}</article>
    <article><h3>Planos de Acao</h3>${planRows || '<p class="muted">Sem Planos de Acao enviados</p>'}</article>
  `;
}

async function loadActionPlans() {
  const polos = await api("/api/v1/polos");
  const plansByPolo = await Promise.all(
    polos.map((polo) => api(`/api/v1/polos/${polo.id}/action-plans`).catch(() => [])),
  );
  const plans = plansByPolo.flat();
  renderActionPlans(plans);
  renderManagementOverview();
  toast("Planos de Acao carregados");
}

async function loadTimeline() {
  if (!state.person) throw new Error("Selecione ou prepare uma pessoa primeiro");
  const data = await api(`/api/v1/persons/${state.person.id}/timeline`);
  renderTimeline(data);
  toast("Jornada carregada");
}

async function loadPoloOverview() {
  const poloId = requireUuid($("poloId").value || state.polo?.id, "Polo ID");
  const data = await api(`/api/v1/polos/${poloId}/overview`);
  state.polo = data.polo;
  setSelected();
  renderPoloOverview(data);
  toast("Gestao do polo carregada");
}

async function loadCabinetOverview() {
  if (!canAccessModule("cabinet")) throw new Error("Seu perfil nao possui acesso ao Modulo Gabinete.");
  let cabinetId = state.cabinet?.id;
  if (!cabinetId) {
    const cabinets = await api("/api/v1/cabinets");
    if (!cabinets.length) throw new Error("Prepare a demo ou crie um gabinete primeiro");
    state.cabinet = cabinets[0].organization;
    state.vereador = cabinets[0].vereador;
    cabinetId = state.cabinet.id;
  }
  const data = await api(`/api/v1/cabinets/${cabinetId}/overview`);
  renderCabinetOverview(data);
  toast("Gabinete carregado");
}

async function login(event) {
  event.preventDefault();
  const data = await api("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({
      username: $("username").value,
      password: $("password").value,
    }),
  });
  state.token = data.access_token;
  localStorage.setItem("revisa.token", state.token);
  setSession();
  await loadCurrentUser();
  toast("Acesso liberado");
  await refreshAll();
}

async function loadCurrentUser() {
  state.currentUser = await api("/api/v1/auth/me");
  applyAccessControls();
  return state.currentUser;
}

async function checkHealth() {
  try {
    await api("/health", { headers: {} });
    setApiStatus(true);
    toast("API online");
  } catch (error) {
    setApiStatus(false);
    toast(`API indisponivel: ${error.message}`);
  }
}

async function refreshAll() {
  if (!state.token) return;
  const [
    people,
    captures,
    demands,
    tasks,
    polos,
    fundingSources,
    budgetItems,
    purchaseRequests,
    purchaseAlerts,
    staffContracts,
    permanentAssets,
    monthlyReports,
  ] = await Promise.all([
    api("/api/v1/persons").catch(() => []),
    api("/api/v1/contacts-capture").catch(() => []),
    api("/api/v1/demands").catch(() => []),
    api("/api/v1/tasks").catch(() => []),
    api("/api/v1/polos").catch(() => []),
    api("/api/v1/administration/funding-sources").catch(() => []),
    api("/api/v1/administration/budget-items").catch(() => []),
    api("/api/v1/administration/purchase-requests").catch(() => []),
    api("/api/v1/administration/purchase-alerts").catch(() => null),
    api("/api/v1/administration/staff-contracts").catch(() => []),
    api("/api/v1/administration/permanent-assets").catch(() => []),
    api("/api/v1/administration/monthly-reports").catch(() => []),
  ]);
  const actionPlans = (
    await Promise.all(polos.map((polo) => api(`/api/v1/polos/${polo.id}/action-plans`).catch(() => [])))
  ).flat();

  state.fundingSources = fundingSources;
  state.budgetItems = budgetItems;
  state.purchaseRequests = purchaseRequests;
  state.purchaseAlerts = purchaseAlerts;
  state.staffContracts = staffContracts;
  state.permanentAssets = permanentAssets;
  state.monthlyReports = monthlyReports;
  state.actionPlans = actionPlans;

  $("personCount").textContent = people.length;
  $("poloCount").textContent = polos.length;
  $("fundingCount").textContent = fundingSources.length;
  $("purchaseOpenCount").textContent = purchaseAlerts?.open_purchase_requests ?? purchaseRequests.filter((request) => request.status !== "CLOSED").length;
  $("staffCount").textContent = staffContracts.length;
  $("assetCount").textContent = permanentAssets.length;
  $("monthlyReportCount").textContent = monthlyReports.length;
  $("actionPlanCount").textContent = actionPlans.length;

  renderList("capturesList", captures, (capture) =>
    item(capture.full_name, `${capture.capture_status} - ${capture.phone || "sem telefone"}`, capture.capture_status, () => {
      state.capture = capture;
      setPersonFromRow(capture);
      setSelected();
    }),
  );
  renderList("demandsList", demands, (demand) =>
    item(demand.title, `${demand.status} - ${demand.category}`, demand.status, () => {
      state.demand = demand;
      setPersonFromRow(demand);
      setSelected();
    }),
  );
  renderList("tasksList", tasks, (task) =>
    item(task.title, `${task.status} - ${task.task_type}`, task.status, () => {
      state.task = task;
      setPersonFromRow(task);
      setSelected();
    }),
  );
  renderList("polosList", polos, (polo) =>
    item(polo.code || polo.id, polo.address_label || "sem endereco", polo.active ? "OPEN" : "CLOSED", () => {
      state.polo = polo;
      setSelected();
      loadPoloOverview().catch(() => {});
    }),
  );
  renderMonthlyReports(monthlyReports);
  renderPermanentAssets(permanentAssets);
  renderPurchaseAlerts(purchaseAlerts || { open_purchase_requests: 0, purchase_requests: [] });
  renderActionPlans(actionPlans);
  renderManagementOverview();
}

async function bootstrapDemo() {
  const result = await api("/api/v1/demo/bootstrap", {
    method: "POST",
    body: JSON.stringify({}),
  });
  state.organization = result.organization;
  state.polo = result.polo;
  state.cabinet = result.cabinet;
  state.vereador = result.vereador;
  state.person = result.person;
  state.capture = result.capture;
  state.demand = result.demand;
  state.task = result.task;
  state.beneficiary = result.beneficiary;
  setSelected();
  toast(result.created.length ? `Demo preparada: ${result.created.join(", ")}` : "Demo pronta");
  await refreshAll();
  await loadTimeline();
  await loadPoloOverview();
  await loadCabinetOverview();
}

async function createCapture() {
  const capture = await api("/api/v1/contacts-capture", {
    method: "POST",
    body: JSON.stringify({
      origin: "WEB_DEMO",
      classification: "DEMANDA",
      vereador_id: state.vereador?.id || null,
      full_name: $("captureName").value,
      phone: $("capturePhone").value,
      district: $("captureDistrict").value,
      priority_level: $("capturePriority").value,
      notes: $("captureNotes").value,
    }),
  });
  state.capture = capture;
  setSelected();
  toast("Captacao criada");
  await refreshAll();
}

async function convertDemand() {
  if (!state.capture) throw new Error("Selecione ou crie uma captacao");
  const result = await api(`/api/v1/contacts-capture/${state.capture.id}/convert-demand`, {
    method: "POST",
    body: JSON.stringify({
      category: "ATENDIMENTO",
      title: `Atendimento - ${state.capture.full_name}`,
      priority: $("capturePriority").value,
    }),
  });
  state.capture = result.capture;
  state.person = result.person;
  state.demand = result.demand;
  setSelected();
  toast("Demanda criada");
  await refreshAll();
  await loadTimeline();
}

async function createTask() {
  if (!state.demand) throw new Error("Selecione ou crie uma demanda");
  const task = await api(`/api/v1/demands/${state.demand.id}/tasks`, {
    method: "POST",
    body: JSON.stringify({
      task_type: "DEMAND_FOLLOW_UP",
      title: `Retorno - ${state.demand.title}`,
      priority: state.demand.priority,
    }),
  });
  state.task = task;
  setSelected();
  toast("Tarefa gerada");
  await refreshAll();
  if (state.person) await loadTimeline();
}

async function completeTask() {
  if (!state.task) throw new Error("Selecione ou crie uma tarefa");
  const task = await api(`/api/v1/tasks/${state.task.id}/complete`, {
    method: "POST",
    body: JSON.stringify({
      resolution_notes: "Finalizado na demonstracao",
      resolve_demand: true,
    }),
  });
  state.task = task;
  if (task.demand_id) {
    state.demand = await api(`/api/v1/demands/${task.demand_id}`);
  }
  setSelected();
  toast("Tarefa concluida");
  await refreshAll();
  if (state.person) await loadTimeline();
}

async function createPolo() {
  const organizationId = requireUuid($("poloOrganizationId").value, "Organization ID");
  const vereadorId = requireUuid($("poloVereadorId").value || state.vereador?.id, "Vereador ID");
  if (state.polo && `${state.polo.organization_id}` === organizationId) {
    toast("Polo ja selecionado");
    return;
  }
  let polo;
  let reusedPolo = false;
  try {
    polo = await api("/api/v1/polos", {
      method: "POST",
      body: JSON.stringify({
        organization_id: organizationId,
        vereador_id: vereadorId,
        code: "DEMO",
        address_label: "Unidade de demonstracao",
      }),
    });
  } catch (error) {
    if (!`${error.message}`.includes("Polo ja existe")) throw error;
    const polos = await api("/api/v1/polos");
    polo = polos.find((item) => `${item.organization_id}` === organizationId);
    if (!polo) throw error;
    reusedPolo = true;
  }
  state.polo = polo;
  setSelected();
  toast(reusedPolo ? "Polo existente selecionado" : "Polo criado");
  await refreshAll();
}

async function createFundingSource() {
  if (!state.organization) throw new Error("Prepare a demo para selecionar a organizacao gestora");
  const sourceType = $("fundingType").value;
  if (isParliamentarySource(sourceType) && !state.vereador) {
    throw new Error("Informe ou carregue o vereador para captacoes parlamentares.");
  }
  const funding = await api("/api/v1/administration/funding-sources", {
    method: "POST",
    body: JSON.stringify({
      organization_id: state.organization.id,
      vereador_id: state.vereador?.id || null,
      source_type: sourceType,
      name: $("fundingName").value,
      description: $("workPlanObject").value || null,
      appropriation_number: $("fundingNumber").value,
      estimated_amount: $("fundingEstimated").value,
      secured_amount: $("fundingDeposited").value,
      deposited_amount: $("fundingDeposited").value,
      deposited_on: new Date().toISOString().slice(0, 10),
      status: "ACTIVE",
      notes: "Captacao independente da REVISA, tratada como centro de custo proprio para prestacao de contas.",
    }),
  });
  state.fundingSource = funding;
  setSelected();
  toast("Captacao cadastrada");
  await refreshAll();
}

async function createWorkPlanBudgetItem() {
  if (!state.fundingSource) throw new Error("Cadastre uma captacao antes do Plano de Trabalho");
  const budgetItem = await api("/api/v1/administration/budget-items", {
    method: "POST",
    body: JSON.stringify({
      organization_id: state.organization?.id || null,
      funding_source_id: state.fundingSource.id,
      polo_id: state.polo?.id || null,
      category: $("workPlanCategory").value,
      description: $("workPlanDescription").value,
      planned_amount: $("workPlanAmount").value || "0",
      committed_amount: $("workPlanAmount").value || "0",
      paid_amount: "0",
      status: "PLANNED",
      notes: `${$("workPlanPeriod").value || "Periodo nao informado"} | ${$("workPlanObject").value || ""}`,
    }),
  });
  state.budgetItems.unshift(budgetItem);
  toast("Item do Plano de Trabalho cadastrado");
  await refreshAll();
}

async function registerDeposit() {
  if (!state.fundingSource) throw new Error("Cadastre uma captacao primeiro");
  const movement = await api("/api/v1/administration/financial-movements", {
    method: "POST",
    body: JSON.stringify({
      funding_source_id: state.fundingSource.id,
      polo_id: state.polo?.id || null,
      movement_type: $("fundingType").value === "EMENDA_IMPOSITIVA" ? "PREFEITURA_DEPOSITO" : "ENTRADA",
      description: "Entrada de recurso da captacao na conta da REVISA",
      amount: $("fundingDeposited").value,
      movement_date: new Date().toISOString().slice(0, 10),
      status: "CONFIRMED",
    }),
  });
  state.financialMovement = movement;
  setSelected();
  toast("Entrada registrada");
  await loadAccountabilityReport().catch(() => {});
}

async function createPurchaseRequest() {
  if (!state.fundingSource) throw new Error("Cadastre uma captacao primeiro");
  const purchase = await api("/api/v1/administration/purchase-requests", {
    method: "POST",
    body: JSON.stringify({
      organization_id: state.organization?.id || null,
      polo_id: state.polo?.id || null,
      funding_source_id: state.fundingSource.id,
      category: "INSUMOS",
      description: $("purchaseDescription").value,
      estimated_amount: "1500.00",
      status: "REQUESTED",
      needed_on: new Date().toISOString().slice(0, 10),
      items: [
        {
          product: $("purchaseDescription").value,
          quantity: "1",
          unit: "lote",
          notes: "Item criado pela demonstracao administrativa.",
        },
      ],
    }),
  });
  state.purchaseRequest = purchase;
  setSelected();
  toast("Compra solicitada");
  await refreshAll();
}

async function createStaffContract() {
  if (!state.fundingSource) throw new Error("Cadastre uma captacao primeiro");
  const person = await api("/api/v1/persons", {
    method: "POST",
    body: JSON.stringify({
      full_name: "Colaborador Polo Demo",
      phone: `${Date.now()}`.slice(-11),
      notes: "Pessoa criada para demonstracao de contrato de pessoal.",
    }),
  });
  const staff = await api("/api/v1/administration/staff-contracts", {
    method: "POST",
    body: JSON.stringify({
      organization_id: state.organization?.id || null,
      polo_id: state.polo?.id || null,
      funding_source_id: state.fundingSource.id,
      person_id: person.id,
      role_title: "Instrutor de apoio",
      contract_type: "TEMPORARIO",
      salary_amount: "2500.00",
      starts_on: new Date().toISOString().slice(0, 10),
      status: "ACTIVE",
      notes: "Contrato vinculado ao recurso da captacao.",
    }),
  });
  state.staffContract = staff;
  setSelected();
  toast("Contrato de pessoal registrado");
  await refreshAll();
}

async function loadAccountabilityReport() {
  const query = accountabilityQuery();
  if (!query) throw new Error("Prepare a demo ou cadastre uma captacao primeiro");
  const report = await api(`/api/v1/administration/accountability-report?${query}`);
  renderAccountabilityReport(report);
  toast("Prestacao carregada");
}

async function loadPurchaseAlerts() {
  const alerts = await api("/api/v1/administration/purchase-alerts");
  renderPurchaseAlerts(alerts);
  renderManagementOverview();
  toast("Alertas carregados");
}

async function loadMonthlyReports() {
  const reports = await api("/api/v1/administration/monthly-reports");
  renderMonthlyReports(reports);
  renderManagementOverview();
  toast("Relatorios carregados");
}

async function loadPermanentAssets() {
  const query = state.polo?.id ? `?polo_id=${state.polo.id}` : "";
  const assets = await api(`/api/v1/administration/permanent-assets${query}`);
  renderPermanentAssets(assets);
  renderManagementOverview();
  toast("Patrimonio carregado");
}

async function createPermanentAsset() {
  if (!state.fundingSource && !state.polo && !state.purchaseRequest) {
    throw new Error("Informe captacao, polo ou requisicao para registrar patrimonio.");
  }
  const asset = await api("/api/v1/administration/permanent-assets", {
    method: "POST",
    body: JSON.stringify({
      organization_id: state.organization?.id || null,
      polo_id: state.polo?.id || null,
      funding_source_id: state.fundingSource?.id || null,
      purchase_request_id: state.purchaseRequest?.id || null,
      asset_type: "BEM_PERMANENTE",
      description: $("purchaseDescription").value || "Bem permanente do Polo",
      brand: "A conferir",
      model: null,
      acquisition_date: new Date().toISOString().slice(0, 10),
      acquisition_value: "0",
      status: "ACTIVE",
      location_label: state.polo?.code || state.fundingSource?.name || "REVISA",
      notes: "Numero patrimonial gerado para impressao posterior de etiqueta.",
    }),
  });
  toast(`Patrimonio registrado: ${asset.asset_number}`);
  await loadPermanentAssets();
}

async function exportAccountabilityReport() {
  const query = accountabilityQuery();
  if (!query) throw new Error("Prepare a demo ou cadastre uma captacao primeiro");
  const response = await fetch(`${apiBase()}/api/v1/administration/accountability-report/export?${query}`, {
    headers: headers(false),
  });
  if (!response.ok) throw new Error("Nao foi possivel exportar a prestacao");
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "prestacao-contas.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  toast("CSV exportado");
}

async function linkBeneficiary() {
  const poloId = requireUuid($("poloId").value, "Polo ID");
  const personId = requireUuid($("poloPersonId").value, "Pessoa ID");
  const beneficiary = await api(`/api/v1/polos/${poloId}/beneficiarios`, {
    method: "POST",
    body: JSON.stringify({
      person_id: personId,
      source_capture_id: state.capture?.id || null,
      status: "ATIVO",
    }),
  });
  state.beneficiary = beneficiary;
  toast("Beneficiario vinculado");
  await loadPoloOverview();
  if (state.person) await loadTimeline();
}

async function registerAttendance() {
  const poloId = requireUuid($("poloId").value, "Polo ID");
  if (!state.beneficiary) throw new Error("Vincule um beneficiario primeiro");
  await api(`/api/v1/polos/${poloId}/frequencias`, {
    method: "POST",
    body: JSON.stringify({
      beneficiario_id: state.beneficiary.id,
      activity_date: new Date().toISOString().slice(0, 10),
      present: true,
      notes: "Presenca registrada na demo",
    }),
  });
  toast("Frequencia registrada");
  await loadPoloOverview();
  if (state.person) await loadTimeline();
}

async function registerOccurrence() {
  const poloId = requireUuid($("poloId").value, "Polo ID");
  await api(`/api/v1/polos/${poloId}/ocorrencias`, {
    method: "POST",
    body: JSON.stringify({
      beneficiario_id: state.beneficiary?.id || null,
      severity: "MEDIUM",
      title: "Ocorrencia de demo",
      description: "Registro criado durante a demonstracao",
    }),
  });
  toast("Ocorrencia registrada");
  await loadPoloOverview();
  if (state.person) await loadTimeline();
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

$("loginForm").addEventListener("submit", async (event) => {
  try {
    await login(event);
  } catch (error) {
    toast(error.message);
  }
});

$("logoutBtn").addEventListener("click", () => {
  state.token = "";
  state.currentUser = null;
  localStorage.removeItem("revisa.token");
  setSession();
  applyAccessControls();
  toast("Sessao encerrada");
});

bind("healthBtn", checkHealth);
bind("bootstrapDemoBtn", bootstrapDemo);
bind("timelineBtn", loadTimeline);
bind("poloOverviewBtn", loadPoloOverview);
bind("cabinetOverviewBtn", loadCabinetOverview);
bind("refreshBtn", refreshAll);
bind("createCaptureBtn", createCapture);
bind("convertDemandBtn", convertDemand);
bind("createTaskBtn", createTask);
bind("completeTaskBtn", completeTask);
bind("createPoloBtn", createPolo);
bind("createFundingBtn", createFundingSource);
bind("workPlanItemBtn", createWorkPlanBudgetItem);
bind("depositFundingBtn", registerDeposit);
bind("purchaseRequestBtn", createPurchaseRequest);
bind("staffContractBtn", createStaffContract);
bind("purchaseAlertsBtn", loadPurchaseAlerts);
bind("createAssetBtn", createPermanentAsset);
bind("assetListBtn", loadPermanentAssets);
bind("monthlyReportsBtn", loadMonthlyReports);
bind("actionPlansBtn", loadActionPlans);
bind("accountabilityBtn", loadAccountabilityReport);
bind("exportAccountabilityBtn", exportAccountabilityReport);
bind("linkBeneficiaryBtn", linkBeneficiary);
bind("attendanceBtn", registerAttendance);
bind("occurrenceBtn", registerOccurrence);

document.querySelectorAll(".side-menu a").forEach((link) => {
  link.addEventListener("click", () => {
    state.activeModule = link.dataset.navModule || "overview";
    applyAccessControls();
  });
});

async function initialize() {
  setSession();
  setSelected();
  applyAccessControls();
  await checkHealth();
  if (state.token) {
    await loadCurrentUser().catch(() => {
      state.token = "";
      state.currentUser = null;
      localStorage.removeItem("revisa.token");
      setSession();
      applyAccessControls();
    });
    await refreshAll().catch(() => {});
  }
}

initialize();
