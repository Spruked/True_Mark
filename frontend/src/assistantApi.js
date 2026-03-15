const LOCAL_ASSISTANT_API = "http://localhost:3301/chat";
const DEFAULT_PRODUCTION_ASSISTANT_API = "https://truemark-chat-assistant.spruked.com/chat";

const PRODUCTION_ASSISTANT_BY_HOST = {
  "true-mark.spruked.com": DEFAULT_PRODUCTION_ASSISTANT_API,
  "www.true-mark.spruked.com": DEFAULT_PRODUCTION_ASSISTANT_API,
  "truemark.spruked.com": DEFAULT_PRODUCTION_ASSISTANT_API,
  "www.truemark.spruked.com": DEFAULT_PRODUCTION_ASSISTANT_API,
  "true_mark.spruked.com": DEFAULT_PRODUCTION_ASSISTANT_API,
  "www.true_mark.spruked.com": DEFAULT_PRODUCTION_ASSISTANT_API,
};

export function getAssistantApiUrl() {
  const configuredApi = import.meta.env.VITE_JOSEPHINE_API?.trim();

  if (configuredApi) {
    return configuredApi;
  }

  const hostname = window.location.hostname.toLowerCase();
  return PRODUCTION_ASSISTANT_BY_HOST[hostname] || LOCAL_ASSISTANT_API;
}
