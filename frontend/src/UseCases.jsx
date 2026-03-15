import React from "react";
import { Box, Container, Typography, Divider } from "@mui/material";
import { colors } from "./designTokens";

const UseCases = () => (
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
        Use Cases
      </Typography>
      <Typography variant="h5" fontWeight={600} sx={{ mt: 4 }}>
        Certified Digital Objects for High-Value Knowledge
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        True Mark Mint is designed for environments where <b>verifiable authorship, immutable records, and long-term traceability</b> are essential.
      </Typography>
      <Typography paragraph>
        Rather than serving as a public NFT marketplace, the system functions as <b>forensic digital object infrastructure</b> deployed inside organizations that need permanent proof of creation and ownership.
      </Typography>
      <Typography paragraph>
        Below are representative scenarios illustrating how institutions and individuals use the platform.
      </Typography>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        Medical Research & Healthcare Systems
      </Typography>
      <Typography variant="subtitle1" fontWeight={500} sx={{ mt: 2 }}>
        Example: Hospital Networks and Clinical Research
      </Typography>
      <Typography paragraph sx={{ mt: 1 }}>
        Large medical institutions generate vast volumes of sensitive intellectual property, including:
      </Typography>
      <ul>
        <li>treatment protocols</li>
        <li>clinical discoveries</li>
        <li>prescription optimization methods</li>
        <li>laboratory research breakthroughs</li>
        <li>trial data timestamps</li>
      </ul>
      <Typography paragraph>
        Traditional systems store these records in internal databases or document repositories. While useful operationally, they often lack <b>independent proof of authorship and creation timing</b>.
      </Typography>
      <Typography paragraph>
        Using the True Mark mint engine, a hospital can mint each discovery as a <b>forensic digital object</b>.
      </Typography>
      <Typography paragraph>
        Example identifier:
      </Typography>
      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 700 }}>
        E-NFT-MAYO-MED-2026-000002
      </Typography>
      <Typography paragraph>
        Each minted object contains:
      </Typography>
      <ul>
        <li>creator authentication</li>
        <li>institutional prefix verification</li>
        <li>encrypted metadata</li>
        <li>layered certificate provenance</li>
        <li>immutable timestamp anchoring</li>
      </ul>
      <Typography paragraph>
        This allows organizations to demonstrate <b>exact creation history</b> in audits, regulatory reviews, or legal proceedings.
      </Typography>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        Scientific Research Institutions
      </Typography>
      <Typography variant="subtitle1" fontWeight={500} sx={{ mt: 2 }}>
        Example: Universities and Research Labs
      </Typography>
      <Typography paragraph sx={{ mt: 1 }}>
        Academic institutions constantly generate knowledge assets such as:
      </Typography>
      <ul>
        <li>doctoral theses</li>
        <li>experimental methodologies</li>
        <li>research protocols</li>
        <li>lab discoveries</li>
        <li>collaborative publications</li>
      </ul>
      <Typography paragraph>
        These assets often circulate across departments and partner institutions.
      </Typography>
      <Typography paragraph>
        By minting them as certified digital objects, universities create a <b>permanent internal research ledger</b>.
      </Typography>
      <Typography paragraph>
        Benefits include:
      </Typography>
      <ul>
        <li>tamper-proof discovery timestamps</li>
        <li>clear authorship attribution</li>
        <li>permanent institutional knowledge archives</li>
        <li>secure collaboration with partner labs</li>
      </ul>
      <Typography paragraph>
        The system supports internal minting through private nodes, ensuring sensitive research remains inside the organization’s environment.
      </Typography>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        Pharmaceutical & Biotechnology Development
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        Pharmaceutical research requires precise documentation of discovery timelines.
      </Typography>
      <Typography paragraph>
        Use cases include:
      </Typography>
      <ul>
        <li>drug formulation development</li>
        <li>trial phase results</li>
        <li>molecule discovery records</li>
        <li>regulatory documentation snapshots</li>
      </ul>
      <Typography paragraph>
        By certifying these records through forensic minting, organizations gain <b>immutable discovery evidence</b> that may support intellectual property claims or regulatory compliance documentation.
      </Typography>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        Enterprise Intellectual Property
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        Corporations frequently create proprietary frameworks and operational systems that represent significant intellectual capital.
      </Typography>
      <Typography paragraph>
        Examples include:
      </Typography>
      <ul>
        <li>manufacturing processes</li>
        <li>engineering methodologies</li>
        <li>business frameworks</li>
        <li>proprietary algorithms</li>
        <li>industrial design systems</li>
      </ul>
      <Typography paragraph>
        Minting these assets produces a <b>verifiable proof-of-origin archive</b>.
      </Typography>
      <Typography paragraph>
        This allows organizations to demonstrate when a methodology or framework was created and by whom, creating long-term protection against disputes.
      </Typography>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        Family Offices & Generational Knowledge
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        The system is also designed to preserve <b>personal and family intellectual legacy</b>.
      </Typography>
      <Typography paragraph>
        Family offices and individuals often possess knowledge that would otherwise disappear over time, such as:
      </Typography>
      <ul>
        <li>proprietary investment strategies</li>
        <li>culinary techniques</li>
        <li>family history documentation</li>
        <li>private research or inventions</li>
        <li>generational craft knowledge</li>
      </ul>
      <Typography paragraph>
        These can be minted as <b>heirloom digital objects</b>, creating permanent records that can be inherited by future generations.
      </Typography>
      <Typography paragraph>
        Example identifier:
      </Typography>
      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 700 }}>
        HL-NFT-SMITHFAM-CUL-2026-000008
      </Typography>
      <Typography paragraph>
        This creates a verified, inheritable knowledge archive rather than a simple document repository.
      </Typography>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        Creative and Cultural Preservation
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        Artists, musicians, and cultural institutions may use the platform to certify:
      </Typography>
      <ul>
        <li>original compositions</li>
        <li>creative techniques</li>
        <li>design systems</li>
        <li>production methodologies</li>
      </ul>
      <Typography paragraph>
        Unlike speculative art NFTs, these records serve as <b>forensic authorship certification</b> rather than trading assets.
      </Typography>
      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" fontWeight={600}>
        Summary
      </Typography>
      <Typography paragraph sx={{ mt: 2 }}>
        Across all industries, the system serves a single core purpose:
      </Typography>
      <Typography variant="h6" fontWeight={700} sx={{ mt: 1, mb: 2 }}>
        Transform knowledge into permanent, verifiable digital objects with immutable provenance.
      </Typography>
      <Typography paragraph>
        This allows organizations and individuals to preserve intellectual assets with confidence that they will remain verifiable decades into the future.
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

export default UseCases;
