const LOCAL_BACKEND_API = "http://localhost:13000";
const DEFAULT_PRODUCTION_BACKEND_API = "https://truemark-api.spruked.com";

// DNS hostnames should ideally use hyphens, but we accept multiple naming
// styles here so the frontend still resolves the backend if either form is
// used during deployment.
const PRODUCTION_API_BY_HOST = {
  "true-mark.spruked.com": DEFAULT_PRODUCTION_BACKEND_API,
  "www.true-mark.spruked.com": DEFAULT_PRODUCTION_BACKEND_API,
  "truemark.spruked.com": DEFAULT_PRODUCTION_BACKEND_API,
  "www.truemark.spruked.com": DEFAULT_PRODUCTION_BACKEND_API,
  "true_mark.spruked.com": DEFAULT_PRODUCTION_BACKEND_API,
  "www.true_mark.spruked.com": DEFAULT_PRODUCTION_BACKEND_API,
};

export function getBackendApiBase() {
  const configuredApi = import.meta.env.VITE_BACKEND_API?.trim();

  if (configuredApi) {
    return configuredApi;
  }

  const hostname = window.location.hostname.toLowerCase();
  return PRODUCTION_API_BY_HOST[hostname] || LOCAL_BACKEND_API;
}
