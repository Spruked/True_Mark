import React from "react";
import { Alert, Box, Button, Chip, Container, Divider, Grid, Paper, Stack, Typography } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import { colors, styles } from "./designTokens";

const workflow = [
  ["01", "Evidence", "Gather identity, provenance, files, images, and supporting records."],
  ["02", "Commit", "Review the exact record and authorize the transition from draft to authority."],
  ["03", "Vault", "Seal the committed evidence in the immutable record."],
  ["04", "Verify", "Issue a Prime Layer Certificate and let anyone independently check it."],
];

const layers = [2, 3, 5, 7, 11, 13];

function App() {
  return <Box sx={{ ...styles.page, minHeight: "calc(100vh - 76px)", py: { xs: 4, md: 7 } }}>
    <Container maxWidth="xl">
      <Grid container spacing={{ xs: 4, md: 7 }} alignItems="center" sx={{ mb: { xs: 7, md: 10 } }}>
        <Grid item xs={12} lg={7}>
          <Typography variant="overline" sx={{ color: colors.gold, letterSpacing: 2.2 }}>TRUE MARK · OBJECT AUTHENTICATION</Typography>
          <Typography variant="h1" sx={{ color: colors.text, fontWeight: 800, letterSpacing: -1.5, mt: 1.5, mb: 2 }}>Authenticate.<br />Preserve. Prove.</Typography>
          <Typography variant="h6" sx={{ color: colors.mutedText, maxWidth: 680, lineHeight: 1.65, fontWeight: 400 }}>Create a governed record of an object, its evidence, provenance, and chain of custody. Seal the record, issue a Prime Layer Certificate, and independently verify it.</Typography>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} sx={{ mt: 3 }}>
            <Button component={RouterLink} to="/objects/new" variant="contained" sx={styles.primaryButton}>Authenticate an Object</Button>
            <Button component={RouterLink} to="/verify" variant="outlined" sx={styles.secondaryButton}>Verify an Object</Button>
          </Stack>
        </Grid>
        <Grid item xs={12} lg={5}>
          <Paper sx={{ ...styles.panel, p: { xs: 3, md: 4 }, borderTop: `4px solid ${colors.gold}` }}>
            <Typography variant="overline" sx={{ color: colors.gold, letterSpacing: 1.8 }}>THE AUTHORITY BOUNDARY</Typography>
            <Typography variant="h4" sx={{ fontWeight: 800, mt: 1 }}>Draft privately. Commit deliberately.</Typography>
            <Typography sx={{ color: colors.mutedText, lineHeight: 1.75, mt: 1.5 }}>Secretum Privatum is your mutable preparation space. Nothing becomes authoritative until you review the evidence and authorize Commit.</Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mt: 2 }}>{["Working Copy", "Ready for Review", "Commit", "Sealed"].map((label, index) => <Chip key={label} label={`${index + 1} · ${label}`} size="small" sx={{ color: index === 0 ? colors.gold : colors.mutedText, borderColor: colors.border, background: "transparent" }} variant="outlined" />)}</Stack>
          </Paper>
        </Grid>
      </Grid>

      <Paper sx={{ ...styles.panel, p: { xs: 2.5, md: 4 }, mb: 4 }}>
        <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" spacing={2} sx={{ mb: 3 }}>
          <Box><Typography variant="overline" sx={{ color: colors.mutedText, letterSpacing: 1.6 }}>PRIVATE WORKSPACE</Typography><Typography variant="h4" sx={{ fontWeight: 800, mt: 0.5 }}>Secretum Privatum</Typography></Box>
          <Button component={RouterLink} to="/sanctum" variant="outlined" sx={styles.secondaryButton}>Open My Sanctum</Button>
        </Stack>
        <Typography sx={{ color: colors.mutedText, maxWidth: 820, lineHeight: 1.75 }}>Prepare evidence, organize provenance, upload supporting material, and build the record privately before anything becomes authoritative. Every object type belongs in the same governed workflow.</Typography>
      </Paper>

      <Grid container spacing={2} sx={{ mb: 7 }}>
        {workflow.map(([number, title, body]) => <Grid item xs={12} sm={6} md={3} key={title}><Paper sx={{ ...styles.panel, p: 2.5, height: "100%", borderTop: `3px solid ${title === "Verify" ? "#74D6A0" : colors.gold}` }}><Typography sx={{ color: colors.gold, fontWeight: 900, letterSpacing: 1.5 }}>{number}</Typography><Typography variant="h6" sx={{ fontWeight: 800, mt: 1 }}>{title}</Typography><Typography variant="body2" sx={{ color: colors.mutedText, lineHeight: 1.7, mt: 1 }}>{body}</Typography></Paper></Grid>)}
      </Grid>

      <Grid container spacing={3} alignItems="stretch">
        <Grid item xs={12} md={7}><Paper sx={{ ...styles.panel, p: { xs: 2.5, md: 3.5 }, height: "100%" }}><Typography variant="overline" sx={{ color: colors.mutedText, letterSpacing: 1.6 }}>PRIME LAYER CERTIFICATES</Typography><Typography variant="h4" sx={{ fontWeight: 800, mt: 0.5 }}>Forensic depth, governed by prime numbers.</Typography><Typography sx={{ color: colors.mutedText, lineHeight: 1.75, mt: 1.5 }}>Certificate depth is separate from the visual design. Frames, colors, seals, typography, layout, and watermark treatment may vary; the evidence-layer count may only be one of these six profiles.</Typography><Stack direction="row" flexWrap="wrap" gap={1} sx={{ mt: 2.5 }}>{layers.map((layer) => <Chip key={layer} label={`${layer}-Layer`} sx={{ color: colors.gold, borderColor: colors.gold, background: "transparent" }} variant="outlined" />)}</Stack><Button component={RouterLink} to="/demo-mint" sx={{ color: colors.gold, px: 0, mt: 2 }}>Explore certificate profiles →</Button></Paper></Grid>
        <Grid item xs={12} md={5}><Paper sx={{ ...styles.panel, p: { xs: 2.5, md: 3.5 }, height: "100%" }}><Typography variant="overline" sx={{ color: colors.mutedText, letterSpacing: 1.6 }}>OPTIONAL DIGITAL EXTENSIONS</Typography><Typography variant="h5" sx={{ fontWeight: 800, mt: 0.5 }}>Extend the record after certification.</Typography><Typography sx={{ color: colors.mutedText, lineHeight: 1.75, mt: 1.5 }}>NFTs, licensing, transfer, inheritance, and other digital representations remain optional extensions after the object has been authenticated and sealed.</Typography><Divider sx={{ borderColor: colors.border, my: 2.5 }} /><Alert severity="info" sx={{ background: "rgba(201,162,39,0.10)", color: colors.neutral, border: `1px solid ${colors.border}`, "& .MuiAlert-icon": { color: colors.gold } }}>The object record is the authority. A digital extension is never a second issuance path.</Alert></Paper></Grid>
      </Grid>
    </Container>
  </Box>;
}

export default App;
