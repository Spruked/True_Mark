import React, { useState } from "react";
import { Box, Button, Container, Paper, Stack, TextField, Typography } from "@mui/material";
import { colors, styles } from "./designTokens";

const CERTSIG_VERIFY_BASE = "https://certsig.com/verify";

export default function Verify() {
  const [reference, setReference] = useState("");

  const openCertSigRegistry = (event) => {
    event.preventDefault();
    const value = reference.trim();
    const destination = value
      ? `${CERTSIG_VERIFY_BASE}/${encodeURIComponent(value)}`
      : "https://certsig.com/";
    window.open(destination, "_blank", "noopener,noreferrer");
  };

  return (
    <Box sx={{ ...styles.page, minHeight: "calc(100vh - 76px)", py: 8 }}>
      <Container maxWidth="sm">
        <Typography variant="overline" sx={{ color: colors.gold, letterSpacing: 2 }}>
          INDEPENDENT CERTSIG REGISTRY
        </Typography>
        <Typography variant="h3" sx={{ fontWeight: 800, mt: 1 }}>Verify a record</Typography>
        <Typography sx={{ color: colors.mutedText, lineHeight: 1.8, mt: 1, mb: 3 }}>
          Enter a serial or verification reference to open the authoritative public record at certsig.com.
          True Mark serial lookup is a separate internal record check and is not the NFT verifier.
        </Typography>
        <Paper component="form" onSubmit={openCertSigRegistry} sx={{ ...styles.panel, p: 3 }}>
          <Stack spacing={2}>
            <TextField
              label="Serial number or verification reference"
              value={reference}
              onChange={(event) => setReference(event.target.value)}
              placeholder="TM-XXXX-XXXX-XX-XXXXX-X"
              fullWidth
            />
            <Button type="submit" variant="contained" sx={styles.primaryButton}>
              Verify Record at CertSig
            </Button>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
}
