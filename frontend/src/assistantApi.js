const LOCAL_ASSISTANT_API = "http://localhost:3301/chat";

const PRODUCTION_ASSISTANT_BY_HOST = {
  "true-mark.spruked.com": "https://chat.true-mark.spruked.com/chat",
  "www.true-mark.spruked.com": "https://chat.true-mark.spruked.com/chat",
  "truemark.spruked.com": "https://chat.true-mark.spruked.com/chat",
  "www.truemark.spruked.com": "https://chat.true-mark.spruked.com/chat",
  "true_mark.spruked.com": "https://chat.true-mark.spruked.com/chat",
  "www.true_mark.spruked.com": "https://chat.true-mark.spruked.com/chat",
};

export function getAssistantApiUrl() {
  const configuredApi = import.meta.env.VITE_JOSEPHINE_API?.trim();

  if (configuredApi) {
    return configuredApi;
  }

  const hostname = window.location.hostname.toLowerCase();
  return PRODUCTION_ASSISTANT_BY_HOST[hostname] || LOCAL_ASSISTANT_API;
}
