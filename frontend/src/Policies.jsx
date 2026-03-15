import React from "react";
import { Box, Container, Typography } from "@mui/material";
import { colors } from "./designTokens";

export default function Policies() {
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
          Policies and Procedures
        </Typography>
        <Typography variant="body1" sx={{ mt: 3, fontSize: 18, opacity: 0.95 }}>
          <b>Josephine, Your Chat Assistant:</b> Josephine is always available to answer questions about policies, privacy, and compliance.<br /><br />
          <b>Data Handling:</b> Files uploaded for NFT minting are staged through the payment and mint workflow, then purged after final document delivery. Only your account information is retained for communications and marketing. NFT records are permanently logged with a glyph trace and stored in a secure vault for audit and accounting.<br /><br />
          <b>Privacy:</b> We do not sell, share, or disclose your data to third parties. You may opt out of marketing communications at any time.<br /><br />
          <b>Security:</b> All records are stored in a secure vault system with persistent logging and cryptographic glyph trace for every NFT.<br /><br />
          <b>Refund Policy:</b> All sales are final. No returns or refunds are offered unless files are corrupted or malformed. If you experience a technical issue, please contact support for resolution.<br /><br />
          <b>Compliance:</b> True Mark Mint Engine operates in accordance with applicable data protection and digital asset regulations. For questions about compliance, contact legal@truemarkmint.com.<br /><br />
          <b>Contact:</b> For support or policy questions, email support@truemarkmint.com.
        </Typography>
      </Container>
    </Box>
  );
}
