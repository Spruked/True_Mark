import React from "react";
import { Box, Button, Container, Paper, Stack, TextField, Typography } from "@mui/material";
import { colors, styles } from "./designTokens";

export default function Verify() {
  return <Box sx={{ ...styles.page, minHeight: "calc(100vh - 76px)", py: 8 }}><Container maxWidth="sm"><Typography variant="overline" sx={{ color: colors.gold, letterSpacing: 2 }}>INDEPENDENT VERIFICATION</Typography><Typography variant="h3" sx={{ fontWeight: 800, mt: 1 }}>Verify a record</Typography><Typography sx={{ color: colors.mutedText, lineHeight: 1.8, mt: 1, mb: 3 }}>Check a canonical certificate manifest, sealed object identifier, or verification QR reference.</Typography><Paper sx={{ ...styles.panel, p: 3 }}><Stack spacing={2}><TextField label="Object ID, certificate ID, or verification reference" fullWidth /><Button variant="contained" sx={styles.primaryButton}>Verify Record</Button></Stack></Paper></Container></Box>;
}
