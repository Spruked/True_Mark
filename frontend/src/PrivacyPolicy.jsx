import React from "react";
import { Box, Container, Typography } from "@mui/material";
import { colors } from "./designTokens";

export default function PrivacyPolicy() {
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
          Privacy Policy
        </Typography>
        <Typography variant="body1" sx={{ mt: 3, fontSize: 18, opacity: 0.95 }}>
          True Mark Mint Engine values your privacy. All personal information collected during onboarding is used solely for account management and platform communications. We do not sell, share, or disclose your data to third parties. You may opt out of marketing communications at any time.<br /><br />
          <b>Josephine, Your Chat Assistant:</b> Josephine is always available to answer privacy questions and guide you through secure onboarding, minting, and data handling.<br /><br />
          <b>Data Purging:</b> Files uploaded for NFT minting are staged for payment and mint processing, then deleted after the mint is completed and your document package is delivered. Only your account information is retained for communications and marketing about new and upcoming products.<br /><br />
          <b>Persistent Records:</b> All NFT records are permanently logged with a glyph trace and stored in a secure vault system for accounting and audit purposes. No personal data is included in these records.<br /><br />
          <b>No Return/Refund Policy:</b> All sales are final. No returns or refunds are offered unless files are corrupted or malformed. If you experience a technical issue, please contact support for resolution.
        </Typography>
      </Container>
    </Box>
  );
}
