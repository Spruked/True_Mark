    // Removed stray setSubmitted(true); that caused ReferenceError
import React, { useState } from "react";
import { Box, Typography, TextField, Button, Paper, Divider } from "@mui/material";
import { colors, styles } from "./designTokens";

const InvestorInquiry = () => {
  const [form, setForm] = useState({
    name: "",
    organization: "",
    focus: "",
    email: "",
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Connect to backend
    setSubmitted(true);
  };

  return (
    <Box
      sx={{
        position: "relative",
        minHeight: "100vh",
        overflow: "hidden",
        backgroundColor: "#0A0F1F",
        color: "#F4F7F8",
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
      <Box maxWidth={900} mx="auto" my={6} sx={{ position: "relative", zIndex: 2 }}>
        <Paper elevation={3} sx={{ p: { xs: 2, md: 5 } }}>
        <Typography variant="h3" gutterBottom fontWeight={700} align="center">
          Investor Inquiry
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <Typography variant="h5" gutterBottom fontWeight={600} sx={{ color: colors.gold }}>
            Strategic Investment in Sovereign Digital Object Infrastructure
          </Typography>
          <Typography paragraph>
            True Mark Mint Engine operates within the <b>Alpha CertSig ecosystem</b>, a forensic-grade digital object infrastructure designed for long-term knowledge certification, immutable archival records, and institutional digital sovereignty.
          </Typography>
          <Typography paragraph>
            As the global market transitions from speculative NFTs to <b>Digital Object Infrastructure</b>, Alpha CertSig and True Mark Mint are positioned to serve organizations requiring permanent, verifiable records for research, intellectual property, and generational knowledge.
          </Typography>
          <Typography paragraph>
            We welcome discussions with investors who understand the emerging demand for <b>secure, sovereign digital record systems</b>.
          </Typography>

          <Divider sx={{ my: 4 }} />

          <Typography variant="h5" gutterBottom fontWeight={600}>
            Investment Philosophy
          </Typography>
          <Typography paragraph>
            The system is built around a simple principle:
          </Typography>
          <Typography variant="h6" gutterBottom fontWeight={700}>
            Organizations should own the infrastructure that certifies their knowledge.
          </Typography>
          <Typography paragraph>
            Traditional cloud platforms impose ongoing fees, custody risk, and data exposure. The Alpha CertSig architecture replaces this with <b>licensed sovereign mint infrastructure</b> that institutions deploy within their own environments.
          </Typography>
          <Typography paragraph>
            This model creates predictable revenue while maintaining strict data sovereignty for clients.
          </Typography>

          <Divider sx={{ my: 4 }} />

          <Typography variant="h5" gutterBottom fontWeight={600}>
            Core Technology Platform
          </Typography>
          <ul>
            <li><b>License-First Smart Contracts</b>: All mint operations originate from controlled license authorities before ledger anchoring.</li>
            <li><b>Multi-Chain Anchoring</b>: Records can anchor verification hashes across multiple blockchains to ensure survivability and audit traceability.</li>
            <li><b>ChaCha20 Encryption</b>: Sensitive metadata may be encrypted locally prior to anchoring, allowing verification without exposing confidential data.</li>
            <li><b>13-Layer Forensic Certificate Rendering</b>: Each minted object generates a certificate containing layered evidence including creator authentication, identifier provenance, ownership chain records, and audit verification.</li>
          </ul>

          <Divider sx={{ my: 4 }} />

          <Typography variant="h5" gutterBottom fontWeight={600}>
            Market Opportunity
          </Typography>
          <Typography paragraph>
            The speculative NFT cycle (2021–2023) focused on collectibles and trading.
          </Typography>
          <Typography paragraph>
            The next phase of the market focuses on <b>Digital Object Infrastructure</b> used for:
          </Typography>
          <ul>
            <li>research verification</li>
            <li>intellectual property protection</li>
            <li>medical and scientific record certification</li>
            <li>enterprise knowledge archives</li>
            <li>generational legacy assets</li>
          </ul>
          <Typography paragraph>
            Institutions increasingly require systems capable of producing <b>tamper-proof, court-defensible records</b>.
          </Typography>
          <Typography paragraph>
            The Alpha CertSig platform addresses this need.
          </Typography>

          <Divider sx={{ my: 4 }} />

          <Typography variant="h5" gutterBottom fontWeight={600}>
            Revenue Model
          </Typography>
          <Typography paragraph>
            The ecosystem follows a <b>license-based infrastructure model</b>.
          </Typography>
          <Typography paragraph>
            Organizations purchase a perpetual license to deploy the mint engine within their own environment.
          </Typography>
          <Typography paragraph>
            Typical revenue streams include:
          </Typography>
          <ul>
            <li><b>Perpetual Infrastructure Licenses</b>: Organizations acquire the mint engine to run internally.</li>
            <li><b>Deployment and Configuration Services</b>: Optional enterprise deployment, security hardening, and compliance setup.</li>
            <li><b>Affiliate Network Expansion Rights</b>: Institutions may extend certified minting to partner organizations under controlled prefixes.</li>
            <li><b>Maintenance and Security Updates</b>: Optional annual renewal for updates and forensic layer improvements.</li>
          </ul>
          <Typography paragraph>
            This structure avoids SaaS dependency while creating scalable enterprise revenue.
          </Typography>

          <Divider sx={{ my: 4 }} />

          <Typography variant="h5" gutterBottom fontWeight={600}>
            Market Position
          </Typography>
          <Typography paragraph>
            Alpha CertSig and True Mark Mint are positioned as <b>Digital Object Infrastructure providers</b>, not marketplaces.
          </Typography>
          <Typography paragraph>
            The ecosystem supports use cases such as:
          </Typography>
          <ul>
            <li>research institutions</li>
            <li>hospital networks</li>
            <li>pharmaceutical labs</li>
            <li>universities</li>
            <li>engineering organizations</li>
            <li>family offices preserving generational knowledge</li>
          </ul>
          <Typography paragraph>
            Each minted object follows a standardized identifier format:
          </Typography>
          <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 700 }}>
            [TYPE]-NFT-[PREFIX]-[INDUSTRY]-[YEAR]-[SEQUENCE]
          </Typography>
          <Typography paragraph>
            Example:
          </Typography>
          <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 700 }}>
            E-NFT-MAYO-MED-2026-000002
          </Typography>
          <Typography paragraph>
            This structured format allows institutional records to remain searchable and verifiable across decades.
          </Typography>

          <Divider sx={{ my: 4 }} />

          <Typography variant="h5" gutterBottom fontWeight={600}>
            Founder Structure
          </Typography>
          <Typography paragraph>
            The ecosystem consists of two distinct systems:
          </Typography>
          <ul>
            <li><b>Alpha CertSig Elite Mint Engine</b>: Licensed infrastructure deployed by organizations.</li>
            <li><b>True Mark Mint Engine</b>: Founder-controlled mint authority and curated vault used for canonical certification and archival authority.</li>
          </ul>
          <Typography paragraph>
            Maintaining this separation preserves the integrity of the ecosystem while enabling scalable enterprise deployment.
          </Typography>

          <Divider sx={{ my: 4 }} />

          <Typography variant="h5" gutterBottom fontWeight={600}>
            Investor Profile
          </Typography>
          <Typography paragraph>
            We are interested in conversations with investors who have experience in:
          </Typography>
          <ul>
            <li>enterprise infrastructure software</li>
            <li>digital security platforms</li>
            <li>research and healthcare technology</li>
            <li>digital asset infrastructure</li>
            <li>sovereign data systems</li>
          </ul>
          <Typography paragraph>
            Strategic investors who understand the long-term value of <b>verified knowledge infrastructure</b> are particularly encouraged to connect.
          </Typography>

          <Divider sx={{ my: 4 }} />

          <Typography variant="h5" gutterBottom fontWeight={600}>
            Investment Inquiries
          </Typography>
          <Typography paragraph>
            Qualified investors may request additional materials including:
          </Typography>
          <ul>
            <li>executive overview</li>
            <li>technical architecture briefing</li>
            <li>deployment model documentation</li>
            <li>revenue projections</li>
            <li>partnership structure</li>
          </ul>
          <Typography paragraph>
            Please submit inquiries through the form below.
          </Typography>

          <Typography variant="subtitle1" fontWeight={700}>
            Investor Relations<br />True Mark Mint Engine / Alpha CertSig<br />
            <span style={{ fontWeight: 400 }}>Contact: <a href="mailto:bryan@spruked.com">bryan@spruked.com</a></span>
          </Typography>

          {submitted ? (
            <Typography color="success.main" mt={3} align="center">
              Thank you for your inquiry. Our team will respond to qualified inquiries within five business days.
            </Typography>
          ) : (
            <Box component="form" onSubmit={handleSubmit} mt={4}>
              <TextField
                label="Name"
                name="name"
                value={form.name}
                onChange={handleChange}
                fullWidth
                margin="normal"
                required
              />
              <TextField
                label="Organization"
                name="organization"
                value={form.organization}
                onChange={handleChange}
                fullWidth
                margin="normal"
                required
              />
              <TextField
                label="Investment Focus"
                name="focus"
                value={form.focus}
                onChange={handleChange}
                fullWidth
                margin="normal"
                required
              />
              <TextField
                label="Email"
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                fullWidth
                margin="normal"
                required
              />
              <TextField
                label="Message"
                name="message"
                value={form.message}
                onChange={handleChange}
                fullWidth
                margin="normal"
                multiline
                minRows={4}
                required
              />
              <Button type="submit" variant="contained" sx={{ mt: 2, ...styles.primaryButton }} fullWidth>
                Submit Inquiry
              </Button>
            </Box>
          )}

          <Divider sx={{ my: 4 }} />
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 4 }}>
            Pro Prime Series company<br />
            © 2026 Spruked. All rights reserved. Unauthorized copying, reproduction, modification, or distribution of this content or associated materials is strictly prohibited.<br />
            © 2026 Spruked — Official Website of Bryan Spruk. All rights reserved.<br />
            © 2026 Spruked. Unauthorized reproduction or distribution is prohibited.
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
};

export default InvestorInquiry;
