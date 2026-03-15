const LOCAL_BACKEND_API = "http://localhost:13000";

// DNS hostnames should ideally use hyphens, but we accept both here so the
// frontend still resolves the backend if either naming style is used.
const PRODUCTION_API_BY_HOST = {
  "true-mark.spruked.com": "https://api.true-mark.spruked.com",
  "www.true-mark.spruked.com": "https://api.true-mark.spruked.com",
  "truemark.spruked.com": "https://api.true-mark.spruked.com",
  "www.truemark.spruked.com": "https://api.true-mark.spruked.com",
  "true_mark.spruked.com": "https://api.true-mark.spruked.com",
  "www.true_mark.spruked.com": "https://api.true-mark.spruked.com",
};

export function getBackendApiBase() {
  const configuredApi = import.meta.env.VITE_BACKEND_API?.trim();

  if (configuredApi) {
    return configuredApi;
  }

  const hostname = window.location.hostname.toLowerCase();
  return PRODUCTION_API_BY_HOST[hostname] || LOCAL_BACKEND_API;
}
