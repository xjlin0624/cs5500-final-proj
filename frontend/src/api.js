const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";
const TOKEN_KEY = "aftercart_token";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function authHeaders() {
  const token = getToken();
  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}

function createApiUrl(path, params = {}) {
  const base = API_BASE.startsWith("http")
    ? API_BASE
    : `${window.location.origin}${API_BASE}`;
  const normalizedBase = base.endsWith("/") ? base : `${base}/`;
  const normalizedPath = path.startsWith("/") ? path.slice(1) : path;
  const url = new URL(normalizedPath, normalizedBase);

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    url.searchParams.set(key, String(value));
  });

  return url.toString();
}

async function handleResponse(res) {
  const contentType = res.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const data = isJson ? await res.json() : await res.text();

  if (!res.ok) {
    const message =
      (isJson && (data.detail || data.message || data.error)) ||
      `Request failed: ${res.status}`;
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }

  return data;
}

export async function login(email, password) {
  const res = await fetch(createApiUrl("auth/login"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await handleResponse(res);
  const token =
    data.access_token || data.token || data.jwt || data.accessToken || null;

  if (token) {
    setToken(token);
  }

  return data;
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
}

export async function getOrders() {
  const res = await fetch(createApiUrl("orders"), {
    method: "GET",
    headers: {
      ...authHeaders(),
    },
  });

  return handleResponse(res);
}

export async function getAlerts(statusOrFilters) {
  const params =
    typeof statusOrFilters === "string"
      ? { status: statusOrFilters }
      : statusOrFilters || {};
  const res = await fetch(createApiUrl("alerts", params), {
    method: "GET",
    headers: {
      ...authHeaders(),
    },
  });

  return handleResponse(res);
}

export async function resolveAlert(id) {
  const res = await fetch(createApiUrl(`alerts/${id}/resolve`), {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
  });

  return handleResponse(res);
}

export async function dismissAlert(id) {
  const res = await fetch(createApiUrl(`alerts/${id}/dismiss`), {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
  });

  return handleResponse(res);
}

export async function getPreferences() {
  const res = await fetch(createApiUrl("users/me/preferences"), {
    method: "GET",
    headers: {
      ...authHeaders(),
    },
  });
  return handleResponse(res);
}

export async function updatePreferences(payload) {
  const res = await fetch(createApiUrl("users/me/preferences"), {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function registerPushToken(payload) {
  const res = await fetch(createApiUrl("push/tokens"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function unregisterPushToken(token) {
  const res = await fetch(createApiUrl(`push/tokens/${encodeURIComponent(token)}`), {
    method: "DELETE",
    headers: {
      ...authHeaders(),
    },
  });
  return handleResponse(res);
}
