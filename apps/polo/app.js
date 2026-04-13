const staffRoles = {
  ADMINISTRATIVO: [
    "Assistente administrativo",
    "Supervisor de polo",
    "Gerente de projetos",
    "Faxineiro",
    "Zelador",
    "Porteiro",
  ],
  ESPECIALISTA: [
    "Psicologo",
    "Pedagogo",
    "Psicopedagogo",
    "Fisioterapeuta",
    "Fonoaudiologo",
    "Terapeuta ocupacional",
    "Psicoterapeuta",
    "Terapeuta integrativo",
    "Professor de educacao fisica",
    "Assistente social",
  ],
  OFICINEIRO: [
    "Artesanato",
    "Lutas",
    "Dancas",
    "Yoga",
    "Ballet",
    "Musica",
    "Monitor de esportes",
  ],
};

const state = {
  token: localStorage.getItem("revisa.polo.token") || "",
  organization: null,
  vereador: null,
  polo: null,
  beneficiary: null,
  modalidade: null,
  people: [],
  beneficiaries: [],
  modalidades: [],
  staffContracts: [],
  attendances: [],
  occurrences: [],
  purchaseItems: [],
  purchaseRequests: [],
  purchaseAlerts: null,
  monthlyReportPreview: null,
  monthlyReports: [],
  actionPlans: [],
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
    if (response.status === 404 && text.includes("File not found")) {
      throw new Error("A API esta apontando para o frontend. Use http://127.0.0.1:8000.");
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

function money(value) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(Number(value || 0));
}

function personName(personId) {
  return state.people.find((person) => `${person.id}` === `${personId}`)?.full_name || shortId(personId);
}

function modalidadeName(modalidadeId) {
  return state.modalidades.find((modalidade) => `${modalidade.id}` === `${modalidadeId}`)?.name || shortId(modalidadeId);
}

function fileCount(id) {
  return $(id).files ? $(id).files.length : 0;
}

function beneficiaryLabel(beneficiary) {
  return `${personName(beneficiary.person_id)} - ${beneficiary.status}`;
}

function setSession() {
  $("sessionState").textContent = state.token ? "Sessao ativa" : "Sessao pendente";
}

function setContext() {
  $("contextPolo").textContent = state.polo ? `${state.polo.code || "Polo"} - ${state.polo.address_label || shortId(state.polo.id)}` : "nenhum";
  $("contextVereador").textContent = state.vereador?.full_name || shortId(state.polo?.vereador_id || state.vereador?.id);
  $("metricBeneficiarios").textContent = state.overview?.metrics?.total_beneficiarios ?? state.beneficiaries.length;
  $("metricModalidades").textContent = state.modalidades.length;
  $("metricEquipe").textContent = state.staffContracts.length;
  $("metricOcorrencias").textContent = state.overview?.metrics?.open_occurrences ?? state.occurrences.filter((item) => item.status === "OPEN").length;
  $("metricRequisicoes").textContent = state.purchaseAlerts?.open_purchase_requests ?? state.purchaseRequests.filter((item) => item.status !== "CLOSED").length;
}

function renderEmpty(target, message) {
  target.innerHTML = `<p class="empty">${escapeHtml(message)}</p>`;
}

function renderItem(target, title, subtitle, body, tone = "cyan") {
  const node = document.createElement("article");
  node.className = "item";
  node.dataset.tone = tone;
  node.innerHTML = `
    <strong>${escapeHtml(title)}</strong>
    <small>${escapeHtml(subtitle || "")}</small>
    ${body ? `<p>${escapeHtml(body)}</p>` : ""}
  `;
  target.appendChild(node);
}

function fillRoleOptions() {
  const group = $("staffGroup").value;
  $("staffRole").innerHTML = staffRoles[group]
    .map((role) => `<option value="${escapeHtml(role)}">${escapeHtml(role)}</option>`)
    .join("");
}

function fillOperationalSelects() {
  $("attendanceBeneficiary").innerHTML = state.beneficiaries.length
    ? state.beneficiaries.map((beneficiary) => `<option value="${beneficiary.id}">${escapeHtml(beneficiaryLabel(beneficiary))}</option>`).join("")
    : '<option value="">Cadastre um beneficiario</option>';

  $("attendanceModality").innerHTML = state.modalidades.length
    ? state.modalidades.map((modalidade) => `<option value="${modalidade.id}">${escapeHtml(modalidade.name)}</option>`).join("")
    : '<option value="">Sem modalidade</option>';

  const activeModalities = state.modalidades.filter((modalidade) => modalidade.active);
  $("actionPlanModality").innerHTML = activeModalities.length
    ? activeModalities.map((modalidade) => `<option value="${modalidade.id}">${escapeHtml(modalidade.name)}</option>`).join("")
    : '<option value="">Cadastre uma modalidade ativa</option>';

  if (state.beneficiary) $("attendanceBeneficiary").value = state.beneficiary.id;
  if (state.modalidade) $("attendanceModality").value = state.modalidade.id;
  if (state.modalidade?.active) $("actionPlanModality").value = state.modalidade.id;
  updateActionPlanTitle();
}

function renderLists() {
  const beneficiaries = $("beneficiariesList");
  beneficiaries.innerHTML = "";
  if (!state.beneficiaries.length) renderEmpty(beneficiaries, "Nenhum beneficiario cadastrado neste Polo.");
  state.beneficiaries.forEach((beneficiary) => {
    renderItem(
      beneficiaries,
      personName(beneficiary.person_id),
      `${beneficiary.status} | beneficiario ${shortId(beneficiary.id)}`,
      beneficiary.admitted_at ? `Admitido em ${beneficiary.admitted_at.slice(0, 10)}` : "Sem data de admissao",
      beneficiary.status === "ATIVO" ? "green" : "yellow",
    );
  });

  const modalities = $("modalitiesList");
  modalities.innerHTML = "";
  if (!state.modalidades.length) renderEmpty(modalities, "Nenhuma modalidade cadastrada neste Polo.");
  state.modalidades.forEach((modalidade) => {
    const baseYear = Number($("actionPlanYear").value || new Date().getFullYear());
    const hasActionPlan = state.actionPlans.some(
      (plan) => `${plan.modalidade_id}` === `${modalidade.id}` && Number(plan.base_year) === baseYear,
    );
    const planStatus = modalidade.active
      ? `Plano de Acao ${baseYear}: ${hasActionPlan ? "enviado" : "pendente"}`
      : "Plano de Acao dispensado enquanto a modalidade estiver inativa";
    renderItem(
      modalities,
      modalidade.name,
      modalidade.active ? "Ativa" : "Inativa",
      `${modalidade.description || "Sem descricao"} | ${planStatus}`,
      modalidade.active && hasActionPlan ? "green" : modalidade.active ? "yellow" : "red",
    );
  });

  const staff = $("staffList");
  staff.innerHTML = "";
  if (!state.staffContracts.length) renderEmpty(staff, "Nenhum contrato de equipe cadastrado.");
  state.staffContracts.forEach((contract) => {
    renderItem(
      staff,
      contract.role_title,
      `${personName(contract.person_id)} | ${contract.contract_type} | ${contract.status}`,
      `${money(contract.salary_amount)} a partir de ${contract.starts_on}`,
      contract.status === "ACTIVE" ? "green" : "yellow",
    );
  });

  const attendances = $("attendancesList");
  attendances.innerHTML = "";
  if (!state.attendances.length) renderEmpty(attendances, "Nenhuma frequencia registrada.");
  state.attendances.forEach((attendance) => {
    const beneficiary = state.beneficiaries.find((item) => `${item.id}` === `${attendance.beneficiario_id}`);
    renderItem(
      attendances,
      beneficiary ? personName(beneficiary.person_id) : shortId(attendance.beneficiario_id),
      `${attendance.activity_date} | ${attendance.present ? "Presente" : "Ausente"}`,
      attendance.modalidade_id ? modalidadeName(attendance.modalidade_id) : attendance.notes,
      attendance.present ? "green" : "red",
    );
  });

  const occurrences = $("occurrencesList");
  occurrences.innerHTML = "";
  if (!state.occurrences.length) renderEmpty(occurrences, "Nenhuma ocorrencia registrada.");
  state.occurrences.forEach((occurrence) => {
    renderItem(
      occurrences,
      occurrence.title,
      `${occurrence.severity} | ${occurrence.status}`,
      occurrence.description,
      occurrence.status === "OPEN" ? "yellow" : "green",
    );
  });

  const purchaseRequests = $("purchaseRequestsList");
  purchaseRequests.innerHTML = "";
  if (!state.purchaseRequests.length) renderEmpty(purchaseRequests, "Nenhuma requisicao de materiais enviada.");
  state.purchaseRequests.forEach((request) => {
    renderItem(
      purchaseRequests,
      request.description,
      `${request.category} | ${request.status} | ${request.items?.length || 0} itens`,
      request.requester_name ? `Solicitante: ${request.requester_name}` : request.notes,
      request.status === "REQUESTED" ? "yellow" : "green",
    );
  });

  const monthlyReports = $("monthlyReportsList");
  monthlyReports.innerHTML = "";
  if (!state.monthlyReports.length) renderEmpty(monthlyReports, "Nenhum relatorio mensal enviado.");
  state.monthlyReports.forEach((report) => {
    renderItem(
      monthlyReports,
      `Competencia ${report.reference_month.slice(0, 7)}`,
      `${report.status} | ${report.active_modalities_count} modalidades | ${report.attachments?.length || 0} anexos`,
      report.occurrence_summary || "Sem ocorrencias informadas",
      report.status === "SUBMITTED" ? "green" : "yellow",
    );
  });

  const actionPlans = $("actionPlansList");
  actionPlans.innerHTML = "";
  if (!state.actionPlans.length) renderEmpty(actionPlans, "Nenhum Plano de Acao anual enviado.");
  state.actionPlans.forEach((plan) => {
    renderItem(
      actionPlans,
      plan.title,
      `Ano Base ${plan.base_year} | ${modalidadeName(plan.modalidade_id)} | ${plan.status}`,
      plan.professional_name ? `Profissional: ${plan.professional_name}` : plan.original_filename,
      plan.status === "SUBMITTED" ? "green" : "yellow",
    );
  });

  fillOperationalSelects();
  renderMonthlyModalities();
  renderPurchaseDraft();
  setContext();
}

function renderPurchaseDraft() {
  const target = $("purchaseDraftList");
  target.innerHTML = "";
  if (!state.purchaseItems.length) {
    renderEmpty(target, "Adicione ao menos um item antes de enviar para a REVISA.");
    return;
  }
  state.purchaseItems.forEach((item, index) => {
    renderItem(
      target,
      `${index + 1}. ${item.product}`,
      `${item.quantity} ${item.unit || ""} | ${item.size || "sem tamanho"} | ${item.desired_brand || "marca livre"}`,
      item.notes,
      "cyan",
    );
  });
}

function renderMonthlyModalities() {
  const target = $("monthlyModalities");
  target.innerHTML = "";
  const activeModalities = state.modalidades.filter((modalidade) => modalidade.active);
  if (!activeModalities.length) {
    renderEmpty(target, "Cadastre ao menos uma modalidade ativa para consolidar o relatorio mensal.");
    return;
  }
  activeModalities.forEach((modalidade) => {
    const existing = target.querySelector(`[data-modalidade-id="${modalidade.id}"]`);
    if (existing) return;
    const row = document.createElement("div");
    row.className = "monthly-modality-row";
    row.dataset.modalidadeId = modalidade.id;
    row.dataset.modalidadeName = modalidade.name;
    row.innerHTML = `
      <label>
        Modalidade
        <input value="${escapeHtml(modalidade.name)}" disabled />
      </label>
      <label>
        Ativa
        <select data-field="active">
          <option value="true">Sim</option>
          <option value="false">Nao</option>
        </select>
      </label>
      <label>
        Beneficiarios
        <input data-field="beneficiaries_count" value="0" />
      </label>
      <label>
        Observacao
        <input data-field="notes" placeholder="Opcional" />
      </label>
    `;
    target.appendChild(row);
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
  localStorage.setItem("revisa.polo.token", state.token);
  setSession();
  toast("Acesso liberado");
  await refreshAll();
}

async function prepareContext() {
  const result = await api("/api/v1/demo/bootstrap", {
    method: "POST",
    body: JSON.stringify({}),
  });
  state.organization = result.organization;
  state.polo = result.polo;
  state.vereador = result.vereador;
  state.beneficiary = result.beneficiary;
  state.modalidade = result.modalidade;
  toast("Contexto do Polo preparado");
  await refreshAll();
}

async function ensurePolo() {
  if (state.polo) return state.polo;
  const polos = await api("/api/v1/polos");
  if (!polos.length) throw new Error("Prepare o contexto para selecionar um Polo.");
  state.polo = polos[0];
  return state.polo;
}

async function refreshAll() {
  if (!state.token) return;
  const polo = await ensurePolo();
  const [people, overview, beneficiaries, modalidades, staffContracts, attendances, occurrences, purchaseRequests, purchaseAlerts, monthlyReports, actionPlans] = await Promise.all([
    api("/api/v1/persons?limit=200").catch(() => []),
    api(`/api/v1/polos/${polo.id}/overview`).catch(() => null),
    api(`/api/v1/polos/${polo.id}/beneficiarios`).catch(() => []),
    api(`/api/v1/polos/${polo.id}/modalidades`).catch(() => []),
    api(`/api/v1/administration/staff-contracts?polo_id=${polo.id}`).catch(() => []),
    api(`/api/v1/polos/${polo.id}/frequencias`).catch(() => []),
    api(`/api/v1/polos/${polo.id}/ocorrencias`).catch(() => []),
    api(`/api/v1/administration/purchase-requests?polo_id=${polo.id}`).catch(() => []),
    api("/api/v1/administration/purchase-alerts").catch(() => null),
    api(`/api/v1/polos/${polo.id}/monthly-reports`).catch(() => []),
    api(`/api/v1/polos/${polo.id}/action-plans`).catch(() => []),
  ]);
  state.people = people;
  state.overview = overview;
  state.beneficiaries = beneficiaries;
  state.modalidades = modalidades;
  state.staffContracts = staffContracts;
  state.attendances = attendances;
  state.occurrences = occurrences;
  state.purchaseRequests = purchaseRequests;
  state.purchaseAlerts = purchaseAlerts;
  state.monthlyReports = monthlyReports;
  state.actionPlans = actionPlans;
  if (!state.beneficiary && beneficiaries.length) state.beneficiary = beneficiaries[0];
  if (!state.modalidade && modalidades.length) state.modalidade = modalidades[0];
  renderLists();
}

async function createPerson(fullName, phone, notes, cpf = "") {
  return api("/api/v1/persons", {
    method: "POST",
    body: JSON.stringify({
      full_name: fullName,
      phone: phone || null,
      cpf: cpf || null,
      notes: notes || null,
    }),
  });
}

async function createBeneficiary() {
  const polo = await ensurePolo();
  const person = await createPerson(
    $("beneficiaryName").value,
    $("beneficiaryPhone").value,
    $("beneficiaryNotes").value,
    $("beneficiaryCpf").value,
  );
  const beneficiary = await api(`/api/v1/polos/${polo.id}/beneficiarios`, {
    method: "POST",
    body: JSON.stringify({
      person_id: person.id,
      status: $("beneficiaryStatus").value,
      admitted_at: new Date().toISOString(),
    }),
  });
  state.beneficiary = beneficiary;
  toast("Beneficiario cadastrado");
  await refreshAll();
}

async function createStaffContract() {
  const polo = await ensurePolo();
  const person = await createPerson(
    $("staffName").value,
    $("staffPhone").value,
    `${$("staffGroup").value} - ${$("staffRole").value}`,
  );
  await api("/api/v1/administration/staff-contracts", {
    method: "POST",
    body: JSON.stringify({
      organization_id: state.organization?.id || null,
      polo_id: polo.id,
      person_id: person.id,
      role_title: $("staffRole").value,
      contract_type: $("contractType").value,
      salary_amount: $("salaryAmount").value || "0",
      starts_on: $("startsOn").value || today(),
      ends_on: $("endsOn").value || null,
      status: "ACTIVE",
      notes: `Grupo operacional: ${$("staffGroup").value}`,
    }),
  });
  toast("Profissional cadastrado");
  await refreshAll();
}

async function createModality() {
  const polo = await ensurePolo();
  const modalidade = await api(`/api/v1/polos/${polo.id}/modalidades`, {
    method: "POST",
    body: JSON.stringify({
      name: $("modalityName").value,
      description: $("modalityDescription").value || null,
      active: $("modalityActive").value === "true",
    }),
  });
  state.modalidade = modalidade;
  toast("Modalidade cadastrada");
  await refreshAll();
}

function updateActionPlanTitle() {
  const selected = state.modalidades.find((modalidade) => `${modalidade.id}` === `${$("actionPlanModality").value}`);
  const year = $("actionPlanYear").value || new Date().getFullYear();
  if (!selected) return;
  $("actionPlanTitle").value = `Plano de Acao ${selected.name} - Ano Base ${year}`;
}

async function uploadActionPlan() {
  const polo = await ensurePolo();
  const modalidadeId = $("actionPlanModality").value;
  if (!modalidadeId) throw new Error("Cadastre uma modalidade ativa para anexar o Plano de Acao.");
  if (!$("actionPlanFile").files?.length) throw new Error("Selecione o arquivo do Plano de Acao.");

  const form = new FormData();
  form.append("base_year", $("actionPlanYear").value || new Date().getFullYear());
  form.append("title", $("actionPlanTitle").value || "Plano de Acao");
  form.append("professional_name", $("actionPlanProfessional").value || "");
  form.append("notes", $("actionPlanNotes").value || "");
  form.append("file", $("actionPlanFile").files[0]);

  const response = await fetch(`${apiBase()}/api/v1/polos/${polo.id}/modalidades/${modalidadeId}/action-plans`, {
    method: "POST",
    headers: state.token ? { Authorization: `Bearer ${state.token}` } : {},
    body: form,
  });
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(data?.detail || "Falha ao enviar Plano de Acao.");
  }
  $("actionPlanFile").value = "";
  toast("Plano de Acao enviado para REVISA");
  await refreshAll();
}

async function registerAttendance() {
  const polo = await ensurePolo();
  const beneficiarioId = $("attendanceBeneficiary").value;
  if (!beneficiarioId) throw new Error("Cadastre ou selecione um beneficiario.");
  const modalidadeId = $("attendanceModality").value || null;
  await api(`/api/v1/polos/${polo.id}/frequencias`, {
    method: "POST",
    body: JSON.stringify({
      beneficiario_id: beneficiarioId,
      modalidade_id: modalidadeId,
      activity_date: $("activityDate").value || today(),
      present: $("present").value === "true",
      notes: $("attendanceNotes").value || null,
    }),
  });
  toast("Frequencia registrada");
  await refreshAll();
}

async function registerOccurrence() {
  const polo = await ensurePolo();
  const beneficiarioId = $("attendanceBeneficiary").value || null;
  await api(`/api/v1/polos/${polo.id}/ocorrencias`, {
    method: "POST",
    body: JSON.stringify({
      beneficiario_id: beneficiarioId,
      severity: $("occurrenceSeverity").value,
      title: $("occurrenceTitle").value,
      description: $("occurrenceDescription").value,
      status: $("occurrenceStatus").value,
    }),
  });
  toast("Ocorrencia registrada");
  await refreshAll();
}

function addPurchaseItem() {
  const product = $("purchaseProduct").value.trim();
  const quantity = $("purchaseQuantity").value.trim();
  if (!product) throw new Error("Informe o produto.");
  if (!quantity || Number(quantity) <= 0) throw new Error("Informe uma quantidade valida.");
  state.purchaseItems.push({
    product,
    size: $("purchaseSize").value.trim() || null,
    desired_brand: $("purchaseBrand").value.trim() || null,
    quantity,
    unit: $("purchaseUnit").value.trim() || null,
    notes: $("purchaseNotes").value.trim() || null,
  });
  $("purchaseProduct").value = "";
  $("purchaseSize").value = "";
  $("purchaseBrand").value = "";
  $("purchaseQuantity").value = "1";
  $("purchaseUnit").value = "un";
  $("purchaseNotes").value = "";
  renderPurchaseDraft();
  toast("Item adicionado");
}

async function sendPurchaseRequest() {
  const polo = await ensurePolo();
  if (!state.purchaseItems.length) throw new Error("Adicione ao menos um item.");
  const itemNames = state.purchaseItems.map((item) => item.product).join(", ");
  const request = await api("/api/v1/administration/purchase-requests", {
    method: "POST",
    body: JSON.stringify({
      organization_id: state.organization?.id || null,
      polo_id: polo.id,
      requester_name: $("purchaseRequester").value || null,
      category: $("purchaseCategory").value,
      description: `Requisicao de materiais - ${itemNames}`,
      status: "REQUESTED",
      needed_on: $("purchaseNeededOn").value || null,
      notes: "Solicitacao enviada pelo Modulo Polo para cotacao e compra pela REVISA.",
      items: state.purchaseItems,
    }),
  });
  state.purchaseItems = [];
  state.purchaseRequests.unshift(request);
  toast("Requisicao enviada para REVISA");
  await refreshAll();
}

function monthlyPayload() {
  const modalities = [...document.querySelectorAll(".monthly-modality-row")].map((row) => ({
    modalidade_id: row.dataset.modalidadeId,
    modalidade_name: row.dataset.modalidadeName,
    active: row.querySelector('[data-field="active"]').value === "true",
    beneficiaries_count: Number(row.querySelector('[data-field="beneficiaries_count"]').value || 0),
    notes: row.querySelector('[data-field="notes"]').value || null,
  }));
  if (!modalities.length) throw new Error("Cadastre uma modalidade ativa antes do relatorio mensal.");
  return {
    reference_month: `${$("monthlyReference").value || today().slice(0, 7)}-01`,
    occurrence_summary: $("monthlyOccurrences").value || null,
    notes: $("monthlyNotes").value || null,
    modalities,
  };
}

async function previewMonthlyReport() {
  const polo = await ensurePolo();
  const preview = await api(`/api/v1/polos/${polo.id}/monthly-reports/preview`, {
    method: "POST",
    body: JSON.stringify(monthlyPayload()),
  });
  state.monthlyReportPreview = preview;
  $("monthlyPreview").textContent = preview.narrative_text;
  toast("Minuta gerada");
}

async function uploadMonthlyFiles(poloId, reportId, inputId, attachmentType, description) {
  const files = $(inputId).files;
  if (!files || !files.length) return;
  const form = new FormData();
  form.append("attachment_type", attachmentType);
  form.append("description", description);
  [...files].forEach((file) => form.append("files", file));
  const response = await fetch(`${apiBase()}/api/v1/polos/${poloId}/monthly-reports/${reportId}/attachments`, {
    method: "POST",
    headers: state.token ? { Authorization: `Bearer ${state.token}` } : {},
    body: form,
  });
  if (!response.ok) throw new Error(`Falha ao enviar anexos: ${attachmentType}`);
}

async function submitMonthlyReport() {
  const polo = await ensurePolo();
  const payload = monthlyPayload();
  const hasActive = payload.modalities.some((item) => item.active);
  if (hasActive && fileCount("photoFiles") === 0) {
    throw new Error("Inclua o acervo fotografico das modalidades ativas.");
  }
  if (!state.monthlyReportPreview) {
    await previewMonthlyReport();
  }
  const report = await api(`/api/v1/polos/${polo.id}/monthly-reports`, {
    method: "POST",
    body: JSON.stringify({
      ...payload,
      status: $("monthlyStatus").value,
      narrative_text: $("monthlyPreview").textContent,
    }),
  });
  await uploadMonthlyFiles(polo.id, report.id, "attendanceFiles", "ATTENDANCE_LIST", "Listas de presenca do mes");
  await uploadMonthlyFiles(polo.id, report.id, "photoFiles", "PHOTO_COLLECTION", "Acervo fotografico do mes");
  await uploadMonthlyFiles(polo.id, report.id, "documentFiles", "SUPPORTING_DOCUMENT", "Documentos comprobatórios do mes");
  state.monthlyReportPreview = null;
  $("monthlyPreview").textContent = "Relatorio enviado para REVISA.";
  $("attendanceFiles").value = "";
  $("photoFiles").value = "";
  $("documentFiles").value = "";
  toast("Relatorio mensal enviado para REVISA");
  await refreshAll();
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

$("staffGroup").addEventListener("change", fillRoleOptions);
$("actionPlanModality").addEventListener("change", updateActionPlanTitle);
$("actionPlanYear").addEventListener("input", updateActionPlanTitle);
$("purchaseCategory").addEventListener("change", () => {
  if ($("purchaseCategory").value !== "BENS_PERMANENTES") return;
  $("purchaseProduct").value = "Notebook";
  $("purchaseSize").value = "14 polegadas";
  $("purchaseBrand").value = "Marca a cotar";
  $("purchaseQuantity").value = "1";
  $("purchaseUnit").value = "unidade";
  $("purchaseNotes").value = "Bem permanente sujeito a controle patrimonial e etiqueta de tombamento.";
});

bind("healthBtn", checkHealth);
bind("loginBtn", login);
bind("contextBtn", prepareContext);
bind("refreshBtn", refreshAll);
bind("createBeneficiaryBtn", createBeneficiary);
bind("createStaffBtn", createStaffContract);
bind("createModalityBtn", createModality);
bind("uploadActionPlanBtn", uploadActionPlan);
bind("attendanceBtn", registerAttendance);
bind("occurrenceBtn", registerOccurrence);
bind("addPurchaseItemBtn", addPurchaseItem);
bind("sendPurchaseBtn", sendPurchaseRequest);
bind("monthlyPreviewBtn", previewMonthlyReport);
bind("monthlySubmitBtn", submitMonthlyReport);

$("startsOn").value = today();
$("activityDate").value = today();
$("purchaseNeededOn").value = today();
$("monthlyReference").value = today().slice(0, 7);
$("actionPlanYear").value = `${new Date().getFullYear()}`;
fillRoleOptions();
setSession();
setContext();
renderPurchaseDraft();
renderMonthlyModalities();
refreshAll().catch(() => {});
