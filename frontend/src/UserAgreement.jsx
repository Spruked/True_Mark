import React from "react";
import { Box, Container, Typography } from "@mui/material";
import { colors } from "./designTokens";

export default function UserAgreement() {
  return (
    <Box
      sx={{
        position: "relative",
        minHeight: "100vh",
        overflow: "hidden",
        backgroundColor: colors.background,
        color: colors.text,
        py: 8,
      }}
    >
      {/* Watermark overlay */}
      <img
        src="/assets/tree_watermark_1200.png"
        alt="True Mark Watermark"
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: 0.04,
          zIndex: 1,
          pointerEvents: "none",
        }}
      />
      <Container maxWidth="md" sx={{ position: "relative", zIndex: 2 }}>
        <Typography variant="h3" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
          User Agreement
        </Typography>
        <Typography variant="body1" sx={{ mt: 3, fontSize: 18, opacity: 0.95 }}>
          By creating an account on True Mark Mint Engine, you agree to abide by all platform rules, policies, and procedures. You acknowledge that your data will be used solely for account management and platform communications, and will never be sold or shared with third parties. You agree to use the platform for lawful, non-speculative, and non-commercial purposes as described in the documentation.<br /><br />
          <b>Josephine, Your Chat Assistant:</b> Josephine is always available to answer questions about the User Agreement, privacy, and platform rules.<br /><br />
          For full details, see our Policies and Procedures document.
        </Typography>
      </Container>
    </Box>
  );
}
