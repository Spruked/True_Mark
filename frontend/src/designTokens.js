export const colors = {
  background: "#0B1220",
  backgroundAlt: "#111827",
  surface: "#121A2A",
  surfaceSolid: "#1F2937",
  gold: "#C9A227",
  goldDark: "#A88416",
  text: "#F3F4F6",
  mutedText: "#9CA3AF",
  textMuted: "#6B7280",
  neutral: "#E5E7EB",
  border: "rgba(229, 231, 235, 0.2)",
  input: "#0F172A",
};

export const styles = {
  page: {
    minHeight: "100vh",
    background: colors.background,
    color: colors.text,
    fontFamily: "Inter, system-ui, sans-serif",
  },
  primaryButton: {
    background: colors.gold,
    color: "#111111",
    fontWeight: 700,
    borderRadius: 2,
    "&:hover": {
      background: colors.goldDark,
    },
  },
  secondaryButton: {
    borderColor: colors.gold,
    color: colors.gold,
    fontWeight: 700,
    borderRadius: 2,
    "&:hover": {
      borderColor: colors.goldDark,
      background: "rgba(201, 162, 39, 0.08)",
    },
  },
  utilityButton: {
    background: colors.surfaceSolid,
    color: colors.neutral,
    borderColor: colors.border,
    fontWeight: 700,
    borderRadius: 2,
    "&:hover": {
      background: "#273244",
      borderColor: colors.neutral,
    },
  },
  title: {
    color: colors.gold,
    fontFamily: "Inter, system-ui, sans-serif",
  },
  mutedLabel: {
    color: colors.mutedText,
    fontSize: "0.85rem",
  },
  panel: {
    background: colors.surface,
    border: `1px solid ${colors.border}`,
    borderRadius: 3,
  },
};
