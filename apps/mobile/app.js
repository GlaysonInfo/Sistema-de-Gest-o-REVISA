const state = {
  token: localStorage.getItem("revisa.mobile.token") || "",
  person: null,
  capture: null,
  demand: null,
  beneficiary: null,
  personLink: null,
  cabinet: null,
  polo: null,
};

const TONINHO_DOCUMENT = "GABINETE-TONINHO-FARMACIA";

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
    if (response.status === 422 && Array.isArray(detail)) throw new Error(formatValidationError(detail));
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

function shortId(value) {
  return value ? `${value}`.slice(0, 8) : "nenhum";
}

function isUuid(value) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(`${value}`.trim());
}

function requireUuid(value, label) {
  const clean = `${value || ""}`.trim();
  if (!isUuid(clean)) throw new Error(`${label} precisa ser um UUID valido.`);
  return clean;
}

function maybeUuid(value, label) {
  const clean = `${value || ""}`.trim();
  return clean ? requireUuid(clean, label) : null;
}

function formatValidationError(detail) {
  const first = detail[0] || {};
  const field = Array.isArray(first.loc) ? first.loc.filter((part) => part !== "body").join(".") : "campo";
  return `${field}: ${first.msg || "valor invalido"}`;
}

function currentMode() {
  return document.querySelector('input[name="intakeMode"]:checked')?.value || "POLO_BENEFICIARIO";
}

function contextForMode() {
  if (currentMode() === "POLO_BENEFICIARIO") {
    return {
      organizationId: state.polo?.organization_id || $("organizationId").value.trim(),
      vereadorId: state.polo?.vereador_id || state.cabinet?.vereador?.id || $("vereadorId").value.trim(),
      poloId: state.polo?.id || $("poloId").value.trim(),
    };
  }
  return {
    organizationId: state.cabinet?.organization?.id || $("organizationId").value.trim(),
    vereadorId: state.cabinet?.vereador?.id || $("vereadorId").value.trim(),
    poloId: null,
  };
}

function setSession() {
  $("sessionState").textContent = state.token ? "Sessao ativa" : "Sessao pendente";
}

function setMetrics() {
  const mode = currentMode();
  $("metricDestino").textContent = mode === "POLO_BENEFICIARIO" ? "Polo / Beneficiario" : "Gabinete / Perfil politico";
  $("metricPolo").textContent = state.polo ? `${state.polo.code || "Polo"} (${shortId(state.polo.id)})` : "Nao carregado";
  $("metricGabinete").textContent = state.cabinet
    ? `${state.cabinet.organization.name || "Gabinete"} (${shortId(state.cabinet.vereador.id)})`
    : "Nao carregado";
}

function syncContextFields() {
  const mode = currentMode();
  document.querySelector(".context-fields").dataset.mode = mode;
  const context = contextForMode();
  $("organizationId").value = context.organizationId || "";
  $("vereadorId").value = context.vereadorId || "";
  $("poloId").value = context.poloId || "";
  setMetrics();
}

function renderResult(data) {
  state.person = data.person;
  state.capture = data.capture;
  state.demand = data.demand;
  state.beneficiary = data.beneficiary;
  state.personLink = data.person_link;

  const destination = data.beneficiary
    ? "Beneficiario pre-cadastrado no Polo"
    : data.person_link
      ? "Perfil politico vinculado ao Gabinete"
      : "Cadastro registrado";

  $("result").innerHTML = `
    <article class="result-item">
      <strong>${escapeHtml(data.person.full_name)}</strong>
      <small>Pessoa ${shortId(data.person.id)} | Captacao ${shortId(data.capture.id)}</small>
    </article>
    <article class="result-item">
      <strong>${escapeHtml(destination)}</strong>
      <small>${escapeHtml(data.intake_type)} | ${data.created_person ? "pessoa nova" : "pessoa existente"}</small>
    </article>
    <article class="result-item">
      <strong>${escapeHtml(data.demand?.title || "Sem demanda criada")}</strong>
      <small>${escapeHtml(data.demand?.category || "sem categoria")} | ${escapeHtml(data.demand?.status || "sem status")}</small>
    </article>
  `;
}

async function renderTimeline(personId) {
  const data = await api(`/api/v1/persons/${personId}/timeline`);
  if (!data.items.length) {
    $("timeline").innerHTML = '<p class="muted">Sem historico para a pessoa.</p>';
    return;
  }
  $("timeline").innerHTML = data.items
    .slice(0, 10)
    .map(
      (item) => `
        <article class="timeline-item" data-type="${escapeHtml(item.type)}">
          <strong>${escapeHtml(item.title)}</strong>
          <small>${escapeHtml(item.type)} | ${escapeHtml(item.status || "sem status")}</small>
          ${item.description ? `<p>${escapeHtml(item.description)}</p>` : ""}
        </article>
      `,
    )
    .join("");
}

function findToninhoCabinet(cabinets) {
  return cabinets.find((cabinet) => {
    const name = `${cabinet.organization?.name || ""} ${cabinet.vereador?.person?.full_name || ""}`.toLowerCase();
    return name.includes("toninho");
  });
}

async function ensureToninhoCabinet() {
  const cabinets = await api("/api/v1/cabinets");
  let cabinet = findToninhoCabinet(cabinets);
  if (cabinet) return cabinet;

  try {
    cabinet = await api("/api/v1/cabinets", {
      method: "POST",
      body: JSON.stringify({
        name: "Gabinete Toninho da Farmacia",
        legal_name: "Gabinete Toninho da Farmacia",
        document_number: TONINHO_DOCUMENT,
        vereador_full_name: "Toninho da Farmacia",
        vereador_phone: "31990000031",
        vereador_email: "toninho.farmacia@revisa.local",
      }),
    });
  } catch (error) {
    if (!`${error.message}`.includes("existe")) throw error;
    cabinet = findToninhoCabinet(await api("/api/v1/cabinets"));
  }
  if (!cabinet) throw new Error("Nao foi possivel preparar o Gabinete Toninho.");
  return cabinet;
}

async function loadPoloForContext(vereadorId) {
  const polos = await api("/api/v1/polos?active=true");
  return polos.find((polo) => `${polo.vereador_id}` === `${vereadorId}`) || polos[0] || null;
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
  localStorage.setItem("revisa.mobile.token", state.token);
  setSession();
  toast("Acesso liberado");
}

async function prepareContext() {
  if (!state.token) throw new Error("Entre no sistema antes de carregar o contexto.");

  state.cabinet = await ensureToninhoCabinet();
  state.polo = await loadPoloForContext(state.cabinet.vereador.id);

  if (!state.polo) {
    const demo = await api("/api/v1/demo/bootstrap", {
      method: "POST",
      body: JSON.stringify({}),
    });
    state.polo = demo.polo;
  }

  syncContextFields();
  toast("Contexto do aplicativo carregado");
}

async function submitIntake() {
  const mode = currentMode();
  const context = contextForMode();
  const payload = {
    intake_type: mode,
    full_name: $("fullName").value,
    phone: $("phone").value || null,
    cpf: $("cpf").value || null,
    birth_date: $("birthDate").value || null,
    email: $("email").value || null,
    gender: $("gender").value || null,
    district: $("district").value || null,
    notes: $("notes").value || null,
    priority_level: $("priorityLevel").value,
    organization_id: maybeUuid(context.organizationId, "Organization ID"),
    vereador_id: maybeUuid(context.vereadorId, "Vereador ID"),
    polo_id: mode === "POLO_BENEFICIARIO" ? requireUuid(context.poloId, "Polo ID") : null,
    create_demand: $("createDemand").checked,
  };

  const result = await api("/api/v1/mobile/intakes", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  renderResult(result);
  await renderTimeline(result.person.id);
  toast(mode === "POLO_BENEFICIARIO" ? "Beneficiario registrado no Polo" : "Perfil politico registrado no Gabinete");
}

async function classifyPerson() {
  if (!state.person) throw new Error("Envie um cadastro primeiro.");
  const context = contextForMode();
  const result = await api("/api/v1/relationships/classifications", {
    method: "POST",
    body: JSON.stringify({
      person_id: state.person.id,
      organization_id: maybeUuid(context.organizationId, "Organization ID"),
      vereador_id: maybeUuid(context.vereadorId, "Vereador ID"),
      level: $("relationshipLevel").value,
      engagement: $("engagement").value,
      priority: $("priorityLevel").value,
      notes: $("relationshipNotes").value || null,
    }),
  });
  await renderTimeline(state.person.id);
  toast(`Classificado como ${result.level}`);
}

async function markLeadership() {
  if (!state.person) throw new Error("Envie um cadastro primeiro.");
  const context = contextForMode();
  const result = await api("/api/v1/relationships/leaderships", {
    method: "POST",
    body: JSON.stringify({
      person_id: state.person.id,
      organization_id: maybeUuid(context.organizationId, "Organization ID"),
      vereador_id: maybeUuid(context.vereadorId, "Vereador ID"),
      polo_id: context.poloId ? requireUuid(context.poloId, "Polo ID") : null,
      district: $("district").value || null,
      leadership_type: $("relationshipLevel").value === "APOIADOR" ? "APOIADOR" : "LIDERANCA_COMUNITARIA",
      area_atuacao: currentMode() === "POLO_BENEFICIARIO" ? "Polo" : "Base politica do gabinete",
      influence_count: null,
      loyalty_level: $("engagement").value,
      notes: $("relationshipNotes").value || null,
    }),
  });
  await renderTimeline(state.person.id);
  toast(`Lideranca registrada: ${shortId(result.id)}`);
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

document.querySelectorAll('input[name="intakeMode"]').forEach((input) => {
  input.addEventListener("change", syncContextFields);
});

bind("healthBtn", checkHealth);
bind("loginBtn", login);
bind("contextBtn", prepareContext);
bind("submitBtn", submitIntake);
bind("classifyBtn", classifyPerson);
bind("leadershipBtn", markLeadership);

setSession();
syncContextFields();
