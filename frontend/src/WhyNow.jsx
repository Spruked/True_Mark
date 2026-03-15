import React from "react";
import { Box, Container, Typography, Divider } from "@mui/material";
import { colors } from "./designTokens";

const WhyNow = () => (
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
        Why Now
      </Typography>
      <Typography variant="h5" fontWeight={600} sx={{ mt: 4 }}>
        The Shift from NFTs to Digital Object Infrastructure
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        The first wave of blockchain-based tokens focused largely on speculation.
      </Typography>
      <Typography paragraph>
        Between 2021 and 2023, most NFTs represented:
      </Typography>
      <ul>
        <li>collectible images</li>
        <li>speculative trading assets</li>
        <li>marketplace-driven digital art</li>
      </ul>
      <Typography paragraph>
        While this phase introduced millions of people to blockchain technology, it did not fully explore the deeper capabilities of <b>verifiable digital objects</b>.
      </Typography>
      <Typography paragraph>
        Today, the market is entering a second phase.
      </Typography>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        The Infrastructure Phase
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        Organizations are increasingly interested in blockchain not for trading assets but for <b>verifiable record infrastructure</b>.
      </Typography>
      <Typography paragraph>
        Instead of asking:
      </Typography>
      <Typography variant="body2" sx={{ fontStyle: 'italic', mt: 1 }}>
        “Can we sell digital collectibles?”
      </Typography>
      <Typography paragraph>
        Institutions are asking:
      </Typography>
      <Typography variant="body2" sx={{ fontStyle: 'italic', mt: 1 }}>
        “How can we create permanent, tamper-proof records of knowledge?”
      </Typography>
      <Typography paragraph>
        This shift is driving the emergence of <b>Digital Object Infrastructure</b>.
      </Typography>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        The Knowledge Economy
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        Modern economies increasingly revolve around knowledge assets.
      </Typography>
      <Typography paragraph>
        Research, intellectual property, proprietary methods, and scientific discoveries often represent billions of dollars in value.
      </Typography>
      <Typography paragraph>
        Yet these assets are frequently stored in fragile formats:
      </Typography>
      <ul>
        <li>PDFs</li>
        <li>spreadsheets</li>
        <li>proprietary databases</li>
        <li>cloud storage systems</li>
      </ul>
      <Typography paragraph>
        These systems provide convenience but often lack <b>independent verification of authorship and timing</b>.
      </Typography>
      <Typography paragraph>
        Digital object infrastructure solves this problem.
      </Typography>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        Institutional Requirements Are Changing
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        Healthcare systems, universities, and research labs are under growing pressure to demonstrate:
      </Typography>
      <ul>
        <li>data integrity</li>
        <li>authorship verification</li>
        <li>regulatory traceability</li>
        <li>long-term archival stability</li>
      </ul>
      <Typography paragraph>
        Traditional document systems struggle to meet these needs.
      </Typography>
      <Typography paragraph>
        Forensic digital objects provide:
      </Typography>
      <ul>
        <li>immutable timestamps</li>
        <li>structured provenance records</li>
        <li>cryptographic verification</li>
        <li>standardized identifiers</li>
      </ul>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        Data Sovereignty Matters
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        Organizations are also becoming increasingly cautious about storing sensitive information in third-party systems.
      </Typography>
      <Typography paragraph>
        Self-hosted mint infrastructure allows institutions to maintain full control of their records while still benefiting from cryptographic verification and ledger anchoring.
      </Typography>
      <Typography paragraph>
        This aligns with global trends emphasizing:
      </Typography>
      <ul>
        <li>data sovereignty</li>
        <li>regulatory compliance</li>
        <li>institutional independence</li>
      </ul>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        The Emergence of Digital Object Infrastructure
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        Digital object systems represent a shift away from marketplaces and toward <b>permanent record systems</b>.
      </Typography>
      <Typography paragraph>
        Rather than trading digital assets, organizations use these systems to:
      </Typography>
      <ul>
        <li>certify knowledge</li>
        <li>prove discovery timelines</li>
        <li>protect intellectual property</li>
        <li>preserve institutional memory</li>
      </ul>
      <Typography paragraph>
        In this model, tokens are not collectibles.
      </Typography>
      <Typography variant="h6" fontWeight={700} sx={{ mt: 1, mb: 2 }}>
        They are forensic digital objects representing real knowledge assets.
      </Typography>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        A Long-Term Standard
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        As industries continue to digitize, the ability to produce <b>verifiable, tamper-proof knowledge records</b> will become increasingly valuable.
      </Typography>
      <Typography paragraph>
        Digital object infrastructure is emerging as the technical foundation for this capability.
      </Typography>
      <Typography paragraph>
        Systems like Alpha CertSig and True Mark Mint are designed specifically for this new phase of the digital economy.
      </Typography>
      <Divider sx={{ my: 4 }} />
      <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 4 }}>
        Pro Prime Series company<br />
        © 2026 Spruked. All rights reserved. Unauthorized copying, reproduction, modification, or distribution of this content or associated materials is strictly prohibited.<br />
        © 2026 Spruked — Official Website of Bryan Spruk. All rights reserved.<br />
        © 2026 Spruked. Unauthorized reproduction or distribution is prohibited.
      </Typography>
    </Container>
  </Box>
);

export default WhyNow;
