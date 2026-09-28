const LOCAL_ESCALATION_API = "http://localhost:13001/api/escalations";

export function getEscalationApiUrl() {
  const configuredApi = import.meta.env.VITE_HUMAN_SUPPORT_API?.trim();
  return configuredApi || LOCAL_ESCALATION_API;
}
