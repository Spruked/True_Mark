const ACCOUNT_KEY = "tm-user-account";
const SESSION_KEY = "tm-user-session";
const ADMIN_SESSION_KEY = "tm-admin-session";
const WORKSPACE_PREFIX = "tm-user-workspace";

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
    email: account.email,
    name: account.name,
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
  return Boolean(getUserSession());
}

export function clearUserSession() {
  window.sessionStorage.removeItem(SESSION_KEY);
  window.dispatchEvent(new Event("tm-auth-changed"));
}

export function startAdminSession(account) {
  window.sessionStorage.setItem(ADMIN_SESSION_KEY, JSON.stringify({
    email: account.email,
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
  return Boolean(getAdminSession());
}

export function clearAdminSession() {
  window.sessionStorage.removeItem(ADMIN_SESSION_KEY);
  window.dispatchEvent(new Event("tm-auth-changed"));
}

function getWorkspaceKey(email) {
  return `${WORKSPACE_PREFIX}:${email}`;
}

export function getStoredWorkspace(email) {
  if (!email) {
    return null;
  }

  const rawWorkspace = window.localStorage.getItem(getWorkspaceKey(email));

  if (!rawWorkspace) {
    return null;
  }

  try {
    return JSON.parse(rawWorkspace);
  } catch {
    return null;
  }
}

export function saveStoredWorkspace(email, workspace) {
  if (!email) {
    return;
  }

  window.localStorage.setItem(getWorkspaceKey(email), JSON.stringify(workspace));
}
