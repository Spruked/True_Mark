import React, { useRef, useState } from "react";
import { Box, Container, Typography } from "@mui/material";
import { colors } from "./designTokens";

export default function About() {
  const videoRef = useRef(null);
  const [muted, setMuted] = useState(true);

  const toggleMute = () => {
    if (!videoRef.current) {
      return;
    }

    const nextMuted = !muted;
    videoRef.current.muted = nextMuted;
    setMuted(nextMuted);
  };

  return (
    <Box
      sx={{
        position: "relative",
        minHeight: "100vh",
        overflow: "hidden",
        backgroundColor: colors.background,
        color: colors.text,
      }}
      >
      {/* Launch/about video background */}
      <video
        ref={videoRef}
        autoPlay
        loop
        muted={muted}
        playsInline
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          zIndex: 0,
          opacity: 0.45,
        }}
      >
        <source src="/assets/truemark launch in 2026.mp4" type="video/mp4" />
      </video>
      <button
        onClick={toggleMute}
        style={{
          position: "absolute",
          top: 24,
          right: 24,
          zIndex: 10,
          background: "rgba(0,0,0,0.5)",
          color: "#fff",
          border: "none",
          borderRadius: 24,
          padding: "8px 16px",
          fontSize: 18,
          cursor: "pointer",
        }}
        aria-label={muted ? "Unmute video" : "Mute video"}
      >
        {muted ? "🔇 Sound Off" : "🔊 Sound On"}
      </button>
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
      <Container
        maxWidth="md"
        sx={{
          py: 10,
          position: "relative",
          zIndex: 2,
        }}
      >
        <Typography variant="h3" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
          About True Mark Mint Engine
        </Typography>
        <Typography variant="h5" fontWeight={500} gutterBottom>
          The Sovereign Vault for Certified Digital Objects
        </Typography>
        <Typography variant="body1" sx={{ mt: 3, mb: 2, fontSize: 18, opacity: 0.95 }}>
          True Mark Mint Engine is a founder-controlled forensic minting vault designed for the permanent certification of high-value digital objects, intellectual property, research breakthroughs, and generational knowledge.<br /><br />
          Unlike marketplace-driven NFT platforms, True Mark Mint is not built for speculation or trading. It exists for a different purpose entirely: verifiable permanence, forensic traceability, and legacy preservation.<br /><br />
          True Mark is a standalone mint system and website. Its records, invoices, vault workflow, and public-facing identity belong to True Mark alone.
        </Typography>
        <Typography variant="h6" fontWeight={600} sx={{ mt: 4, color: colors.gold }}>
          Purpose
        </Typography>
        <Typography variant="body1" sx={{ mt: 1, fontSize: 17 }}>
          True Mark Mint Engine exists to solve a growing problem in the digital era:<br /><br />
          Modern knowledge, research, and creative work are stored in fragile formats — cloud drives, PDFs, and proprietary databases that can be edited, lost, or become obsolete.<br /><br />
          True Mark transforms those records into forensic digital objects with:
          <ul>
            <li>Immutable timestamps</li>
            <li>Cryptographic verification</li>
            <li>Multi-layer certificate provenance</li>
            <li>Long-term identifier standards</li>
          </ul>
          Each object minted becomes a permanent, traceable artifact of authorship and creation.
        </Typography>
        <Typography variant="h6" fontWeight={600} sx={{ mt: 4, color: colors.gold }}>
          Architecture Overview
        </Typography>
        <Typography variant="body1" sx={{ mt: 1, fontSize: 17 }}>
          The True Mark Mint Engine is built as a self-contained issuance workflow with pricing, payment clearance, mint finalization, certificate rendering, and long-term record custody inside one platform.<br /><br />
          <b>Key architectural elements include:</b>
          <ul>
            <li>License-First Smart Contracts</li>
            <li>Multi-Chain Anchoring</li>
            <li>ChaCha20 Encryption</li>
            <li>13-Layer Forensic Certificate Rendering</li>
          </ul>
          Each minted object generates a certificate containing layered evidence including creator authentication, identifier provenance, prefix authority validation, ownership chain records, and audit verification layers. These layers transform the NFT into a forensic record rather than a simple token.
        </Typography>
        <Typography variant="h6" fontWeight={600} sx={{ mt: 4, color: colors.gold }}>
          The Identifier Standard
        </Typography>
        <Typography variant="body1" sx={{ mt: 1, fontSize: 17 }}>
          Every object minted within the system follows a structured forensic identifier format:<br />
          <b>[TYPE]-NFT-[PREFIX]-[INDUSTRY]-[YEAR]-[SEQUENCE]</b><br />
          Example: <b>E-NFT-MAYO-MED-2026-000002</b><br /><br />
          This format ensures that every record remains human readable, machine searchable, institutionally branded, and permanently mappable across the True Mark system.
        </Typography>
        <Typography variant="h6" fontWeight={600} sx={{ mt: 4, color: colors.gold }}>
          What True Mark Is — and What It Is Not
        </Typography>
        <Typography variant="body1" sx={{ mt: 1, fontSize: 17 }}>
          <b>True Mark Mint Engine IS</b>
          <ul>
            <li>A sovereign archival mint vault</li>
            <li>A forensic certification system</li>
            <li>A permanent registry for digital knowledge assets</li>
            <li>A legacy preservation mechanism</li>
          </ul>
          <b>True Mark Mint Engine is NOT</b>
          <ul>
            <li>An NFT marketplace</li>
            <li>A speculative trading platform</li>
            <li>A SaaS minting service</li>
          </ul>
          Its purpose is proof, permanence, and provenance.
        </Typography>
        <Typography variant="h6" fontWeight={600} sx={{ mt: 4, color: colors.gold }}>
          Designed for Long-Term Knowledge Preservation
        </Typography>
        <Typography variant="body1" sx={{ mt: 1, fontSize: 17 }}>
          True Mark is designed for use cases where verifiable authorship and historical accuracy matter.<br /><br />
          Typical objects minted include:
          <ul>
            <li>scientific discoveries</li>
            <li>medical protocols</li>
            <li>legal frameworks</li>
            <li>proprietary methodologies</li>
            <li>family knowledge heirlooms</li>
            <li>engineering breakthroughs</li>
            <li>licensed intellectual property</li>
          </ul>
          Each record becomes a digital artifact with court-defensible provenance.
        </Typography>
        <Typography variant="h6" fontWeight={600} sx={{ mt: 4, color: colors.gold }}>
          The Founder's Doctrine
        </Typography>
        <Typography variant="body1" sx={{ mt: 1, fontSize: 17, mb: 6 }}>
          True Mark Mint Engine operates under a simple principle:<br /><br />
          Ownership of knowledge should never depend on a third-party platform.<br /><br />
          Records minted through the system remain permanently verifiable regardless of the survival of any company or marketplace.<br /><br />
          The objective is simple: Create a durable record of truth that survives platforms, companies, and generations.
        </Typography>
      </Container>
    </Box>
  );
}
