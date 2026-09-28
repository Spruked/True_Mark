import React from "react";
import {
  Alert,
  Box,
  Button,
  Chip,
  Container,
  Divider,
  Grid,
  LinearProgress,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import { colors, styles } from "./designTokens";

const dashboardCards = [
  { code: "KL", title: "Knowledge Series", body: "Issue encrypted access to masterclasses, methods, and specialist expertise.", action: "Create Knowledge Certificate", to: "/mint", tone: colors.gold },
  { code: "HL", title: "Heirloom Series", body: "Preserve family archives, memories, and inheritance-bound records.", action: "Open Heirloom Flow", to: "/mint", tone: "#9DB7C9" },
  { code: "LL", title: "Legacy Series", body: "Protect enterprise IP, training systems, and licensable operating frameworks.", action: "Review Legacy Options", to: "/investor", tone: "#C98762" },
];

const activity = [
  ["KL-2026-0042", "Advanced Electrical Systems", "5-Layer Certificate", "Ready"],
  ["HL-2026-0039", "The Calder Family Archive", "13-Layer Elite Forensic Certificate", "Anchored"],
  ["LL-2026-0031", "Franchise Operations Manual", "7-Layer Certificate", "Draft"],
];

function Metric({ label, value, detail }) {
  return <Paper sx={{ ...styles.panel, p: 2.5, height: "100%" }}>
    <Typography variant="overline" sx={{ color: colors.mutedText, letterSpacing: 1.4 }}>{label}</Typography>
    <Typography variant="h4" sx={{ color: colors.gold, fontWeight: 800, mt: 0.5 }}>{value}</Typography>
    <Typography variant="body2" sx={{ color: colors.mutedText, mt: 0.5 }}>{detail}</Typography>
  </Paper>;
}

function App() {
  return <Box sx={{ ...styles.page, minHeight: "calc(100vh - 76px)", py: { xs: 4, md: 6 } }}>
    <Container maxWidth="xl">
      <Stack direction={{ xs: "column", lg: "row" }} justifyContent="space-between" alignItems={{ xs: "flex-start", lg: "flex-end" }} spacing={3} sx={{ mb: 4 }}>
        <Box>
          <Typography variant="overline" sx={{ color: colors.gold, letterSpacing: 2 }}>FORENSIC VAULT ISSUANCE ENGINE</Typography>
          <Typography variant="h2" sx={{ color: colors.text, fontWeight: 800, letterSpacing: -1, mt: 1, mb: 1 }}>Issue authority.<br />Preserve what matters.</Typography>
          <Typography variant="body1" sx={{ color: colors.mutedText, maxWidth: 620, lineHeight: 1.8 }}>Your operational dashboard for encrypted vaults, forensic certificates, licensed knowledge, heirlooms, and enterprise IP.</Typography>
        </Box>
        <Stack direction="row" spacing={1.5}>
          <Button component={RouterLink} to="/demo-mint" variant="outlined" sx={styles.secondaryButton}>Preview Certificate</Button>
          <Button component={RouterLink} to="/mint" variant="contained" sx={styles.primaryButton}>Create Certificate</Button>
        </Stack>
      </Stack>

      <Alert severity="info" sx={{ mb: 3, background: "rgba(201,162,39,0.10)", color: colors.neutral, border: `1px solid ${colors.border}`, "& .MuiAlert-icon": { color: colors.gold } }}>
        ChaCha20 secure vault is ready. Content is encrypted at source before the issuance workflow continues.
      </Alert>

      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}><Metric label="Active Vaults" value="08" detail="Encrypted records in custody" /></Grid>
        <Grid item xs={12} sm={6} md={3}><Metric label="Certificates" value="24" detail="Across KL, HL, and LL series" /></Grid>
        <Grid item xs={12} sm={6} md={3}><Metric label="Protected Assets" value="148 GB" detail="2 GB included per single mint" /></Grid>
        <Grid item xs={12} sm={6} md={3}><Metric label="Access Events" value="312" detail="Logged in the last 30 days" /></Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Paper sx={{ ...styles.panel, p: { xs: 2.5, md: 3 } }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2.5 }}>
              <Box><Typography variant="overline" sx={{ color: colors.mutedText, letterSpacing: 1.5 }}>ISSUANCE PATHS</Typography><Typography variant="h5" sx={{ fontWeight: 800 }}>Choose your certificate series</Typography></Box>
              <Chip label="License-first" size="small" sx={{ color: colors.gold, border: `1px solid ${colors.gold}`, background: "transparent" }} />
            </Stack>
            <Grid container spacing={2}>
              {dashboardCards.map((card) => <Grid item xs={12} md={4} key={card.code}>
                <Paper sx={{ height: "100%", p: 2.5, background: colors.surfaceSolid, border: `1px solid ${colors.border}`, borderTop: `3px solid ${card.tone}`, borderRadius: 2 }}>
                  <Typography sx={{ color: card.tone, fontWeight: 900, letterSpacing: 2, fontSize: 18 }}>{card.code}-SERIES</Typography>
                  <Typography variant="h6" sx={{ color: colors.text, fontWeight: 800, mt: 1 }}>{card.title}</Typography>
                  <Typography variant="body2" sx={{ color: colors.mutedText, lineHeight: 1.65, mt: 1.5, minHeight: 78 }}>{card.body}</Typography>
                  <Button component={RouterLink} to={card.to} variant="text" sx={{ color: card.tone, px: 0, mt: 1, fontWeight: 800 }}>{card.action} →</Button>
                </Paper>
              </Grid>)}
            </Grid>
          </Paper>

          <Paper sx={{ ...styles.panel, p: { xs: 2.5, md: 3 }, mt: 3 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}><Box><Typography variant="overline" sx={{ color: colors.mutedText, letterSpacing: 1.5 }}>RECENT ACTIVITY</Typography><Typography variant="h5" sx={{ fontWeight: 800 }}>Your authority ledger</Typography></Box><Button component={RouterLink} to="/demo-mint" sx={{ color: colors.gold }}>View all</Button></Stack>
            {activity.map(([id, title, cert, status], index) => <React.Fragment key={id}><Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems={{ xs: "flex-start", sm: "center" }} sx={{ py: 2 }}><Box sx={{ width: 42, height: 42, borderRadius: 1.5, display: "grid", placeItems: "center", background: "rgba(201,162,39,0.14)", color: colors.gold, fontWeight: 900 }}>{id.slice(0, 2)}</Box><Box sx={{ flex: 1 }}><Typography sx={{ fontWeight: 800 }}>{title}</Typography><Typography variant="body2" sx={{ color: colors.mutedText }}>{id} · {cert}</Typography></Box><Chip label={status} size="small" sx={{ color: status === "Draft" ? colors.mutedText : "#74D6A0", background: status === "Draft" ? "rgba(255,255,255,0.08)" : "rgba(116,214,160,0.12)" }} /></Stack>{index < activity.length - 1 && <Divider sx={{ borderColor: colors.border }} />}</React.Fragment>)}
          </Paper>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Paper sx={{ ...styles.panel, p: 3, mb: 3 }}>
            <Typography variant="overline" sx={{ color: colors.mutedText, letterSpacing: 1.5 }}>VAULT HEALTH</Typography>
            <Typography variant="h5" sx={{ fontWeight: 800, mt: 0.5 }}>Secure and operational</Typography>
            <Typography variant="body2" sx={{ color: colors.mutedText, lineHeight: 1.7, mt: 1 }}>All active assets are encrypted before exposure. Access logs and key-gated delivery are enabled for this workspace.</Typography>
            <LinearProgress variant="determinate" value={82} sx={{ mt: 3, height: 8, borderRadius: 99, background: colors.surfaceSolid, "& .MuiLinearProgress-bar": { background: colors.gold } }} />
            <Stack direction="row" justifyContent="space-between" sx={{ mt: 1 }}><Typography variant="caption" sx={{ color: colors.mutedText }}>Storage used</Typography><Typography variant="caption" sx={{ color: colors.gold }}>82%</Typography></Stack>
            <Button component={RouterLink} to="/cart" fullWidth variant="outlined" sx={{ ...styles.secondaryButton, mt: 3 }}>Open Vault</Button>
          </Paper>
          <Paper sx={{ ...styles.panel, p: 3 }}>
            <Typography variant="overline" sx={{ color: colors.mutedText, letterSpacing: 1.5 }}>FORENSIC LAYER FORGE</Typography>
            <Typography variant="h5" sx={{ fontWeight: 800, mt: 0.5 }}>Prime-number profiles</Typography>
            <Typography variant="body2" sx={{ color: colors.mutedText, lineHeight: 1.7, mt: 1 }}>Every certificate uses a governed 2, 3, 5, 7, 11, or 13-layer evidence profile.</Typography>
            <Stack direction="row" flexWrap="wrap" gap={1} sx={{ mt: 2 }}>{[2, 3, 5, 7, 11, 13].map((layer) => <Chip key={layer} label={`${layer}L`} sx={{ color: colors.gold, borderColor: colors.gold, background: "transparent" }} variant="outlined" />)}</Stack>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  </Box>;
}

export default App;
