const ACCOUNT_KEY = "tm-user-account";
const SESSION_KEY = "tm-user-session";
const ADMIN_SESSION_KEY = "tm-admin-session";

export function getStoredAccount() {
  const rawAccount = window.localStorage.getItem(ACCOUNT_KEY);

  if (!rawAccount) {
    return null;
  }

  try {
    return JSON.parse(rawAccount);
  } catch {
    return null;
  }
}

export function saveStoredAccount(account) {
  window.localStorage.setItem(ACCOUNT_KEY, JSON.stringify(account));
}

export function startUserSession(account) {
  window.sessionStorage.setItem(SESSION_KEY, JSON.stringify({
    id: account.id,
    email: account.email,
    name: account.name,
    token: account.session_token,
    expiresAt: account.session_expires_at,
    startedAt: new Date().toISOString(),
  }));
  window.dispatchEvent(new Event("tm-auth-changed"));
}

export function getUserSession() {
  const rawSession = window.sessionStorage.getItem(SESSION_KEY);

  if (!rawSession) {
    return null;
  }

  try {
    return JSON.parse(rawSession);
  } catch {
    return null;
  }
}

export function getActiveUser() {
  return getUserSession() || getStoredAccount();
}

export function isUserAuthenticated() {
  const session = getUserSession();
  if (!session?.token) return false;
  if (session.expiresAt && Date.now() >= session.expiresAt * 1000) {
    clearUserSession();
    return false;
  }
  return true;
}

export function getUserAuthHeaders() {
  const session = getUserSession();
  return session?.token ? { Authorization: `Bearer ${session.token}` } : {};
}

export function clearUserSession() {
  window.sessionStorage.removeItem(SESSION_KEY);
  window.dispatchEvent(new Event("tm-auth-changed"));
}

export function startAdminSession(account) {
  const expiresAt = Number(account.expires_at ?? account.expiresAt ?? 0) || null;

  window.sessionStorage.setItem(ADMIN_SESSION_KEY, JSON.stringify({
    email: account.email?.trim().toLowerCase(),
    token: account.token,
    expiresAt,
    startedAt: new Date().toISOString(),
  }));
  window.dispatchEvent(new Event("tm-auth-changed"));
}

export function getAdminSession() {
  const rawSession = window.sessionStorage.getItem(ADMIN_SESSION_KEY);

  if (!rawSession) {
    return null;
  }

  try {
    return JSON.parse(rawSession);
  } catch {
    return null;
  }
}

export function isAdminAuthenticated() {
  const adminSession = getAdminSession();

  if (!adminSession?.token) {
    return false;
  }

  if (adminSession.expiresAt && Date.now() >= adminSession.expiresAt * 1000) {
    clearAdminSession();
    return false;
  }

  return true;
}

export function clearAdminSession() {
  window.sessionStorage.removeItem(ADMIN_SESSION_KEY);
  window.dispatchEvent(new Event("tm-auth-changed"));
}

export function getAdminAuthHeaders() {
  const adminSession = getAdminSession();

  if (!adminSession?.token) {
    return {};
  }

  return {
    Authorization: `Bearer ${adminSession.token}`,
  };
}
