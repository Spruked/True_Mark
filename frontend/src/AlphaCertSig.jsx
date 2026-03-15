import React from "react";
import { Box, Button, Container, Stack, Typography } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import { colors, styles } from "./designTokens";

const licenseTiers = [
  {
    name: "Starter Mint",
    price: "$4,888.88",
    renewal: "$388 Annual Maintenance (Optional)",
    points: [
      "Single prefix registry",
      "5-layer certificate system",
      "DIY deployment",
      "Community support",
    ],
  },
  {
    name: "Institutional Core",
    price: "$8,888.88",
    renewal: "15% Annual Renewal",
    points: [
      "Unlimited internal users",
      "Private minting infrastructure",
      "Prefix registry management",
      "Enterprise documentation",
    ],
  },
  {
    name: "Institutional Flagship",
    price: "$11,888.88",
    renewal: "15% Annual Renewal",
    points: [
      "Full 10-layer forensic certificate system",
      "ChaCha20 encryption module",
      "Priority onboarding",
      "Compliance-ready documentation",
    ],
  },
];

const deploymentServices = [
  {
    name: "Guided Setup",
    price: "$1,888",
    points: ["Two remote setup sessions", "Prefix configuration", "Private mint initialization"],
  },
  {
    name: "Enterprise Installation",
    price: "$3,888",
    points: ["Hardened deployment", "Encryption configuration", "Certificate layer calibration", "60-day priority support"],
  },
  {
    name: "Air-Gapped Installation",
    price: "Starting at $5,888",
    points: ["Offline installation package", "Security key ceremony training", "Hardened system documentation"],
  },
];

export default function AlphaCertSig() {
  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: colors.background,
        color: colors.text,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <img
        src="/assets/tree_watermark_1200.png"
        alt="True Mark Watermark"
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: 0.04,
          pointerEvents: "none",
        }}
      />

      <Container maxWidth="lg" sx={{ position: "relative", zIndex: 1, py: 10 }}>
        <Stack spacing={3} sx={{ mb: 7 }}>
          <Typography variant="h3" fontWeight={700} sx={styles.title}>
            Alpha CertSig Elite Mint Engine
          </Typography>
          <Typography variant="h5" fontWeight={500}>
            Sovereign Digital Object Infrastructure
          </Typography>
          <Typography variant="body1" sx={{ fontSize: 18, opacity: 0.92, maxWidth: 920 }}>
            Alpha CertSig is a self-hosted mint engine for institutions and sovereign creators who need forensic-grade
            digital object issuance without relying on third-party platforms. It is licensed infrastructure that runs
            inside your own environment and is designed for internal minting, digital twins, intellectual property,
            certified documents, institutional knowledge objects, and long-term evidentiary records.
          </Typography>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <Button
              component="a"
              href="https://spruked.com/products/alpha-certsig"
              target="_blank"
              rel="noreferrer"
              variant="contained"
              sx={styles.primaryButton}
            >
              View Product Page
            </Button>
            <Button component={RouterLink} to="/about" variant="outlined" sx={styles.secondaryButton}>
              Compare With True Mark
            </Button>
          </Stack>
        </Stack>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "repeat(2, 1fr)" },
            gap: 3,
            mb: 6,
          }}
        >
          <Box sx={{ ...styles.panel, p: 3 }}>
            <Typography variant="h6" fontWeight={700} sx={{ color: colors.gold, mb: 2 }}>
              The Market Has Changed
            </Typography>
            <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
              The first wave of NFTs focused on speculation. The next wave is infrastructure. Organizations are not
              looking for collectible tokens. They need immutable internal records, forensic timestamping, digital twin
              infrastructure, verifiable intellectual property, and sovereign data control.
            </Typography>
          </Box>
          <Box sx={{ ...styles.panel, p: 3 }}>
            <Typography variant="h6" fontWeight={700} sx={{ color: colors.gold, mb: 2 }}>
              The Key Distinction
            </Typography>
            <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
              Alpha CertSig is the licensed mint engine. True Mark Mint is the founder&apos;s curated vault. Alpha
              CertSig is self-hosted, deployable, and licensable. True Mark is not installable, not licensable, and
              not commoditized. True Mark functions as the museum. Alpha CertSig is the printing press.
            </Typography>
          </Box>
        </Box>

        <Box sx={{ mb: 6 }}>
          <Typography variant="h4" fontWeight={700} sx={{ ...styles.title, mb: 3 }}>
            Core Capabilities
          </Typography>
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)" },
              gap: 2,
            }}
          >
            {[
              "Self-hosted ownership with no platform dependency",
              "Docker, Linux, WSL2, and private network deployment support",
              "Multi-layer forensic certificate architecture",
              "Optional ChaCha20 secure object encryption",
              "Structured digital object identifiers",
              "Institutional memory preservation with searchable verifiable records",
            ].map((item) => (
              <Box key={item} sx={{ ...styles.panel, p: 3 }}>
                <Typography variant="body1" sx={{ lineHeight: 1.8 }}>{item}</Typography>
              </Box>
            ))}
          </Box>
        </Box>

        <Box sx={{ mb: 6 }}>
          <Typography variant="h4" fontWeight={700} sx={{ ...styles.title, mb: 3 }}>
            Licensing Options
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.88, mb: 3 }}>
            These tiers are priced to be more attractive on the way into the ecosystem while still supporting scaled institutional deployment.
          </Typography>
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)" },
              gap: 2,
            }}
          >
            {licenseTiers.map((tier) => (
              <Box key={tier.name} sx={{ ...styles.panel, p: 3 }}>
                <Typography variant="h6" fontWeight={700} sx={{ color: colors.gold }}>
                  {tier.name}
                </Typography>
                <Typography variant="h4" fontWeight={800} sx={{ mt: 1 }}>
                  {tier.price}
                </Typography>
                <Typography variant="body2" sx={{ color: colors.mutedText, mb: 2 }}>
                  {tier.renewal}
                </Typography>
                {tier.points.map((point) => (
                  <Typography key={point} variant="body2" sx={{ mb: 1.1, lineHeight: 1.7 }}>
                    • {point}
                  </Typography>
                ))}
              </Box>
            ))}
          </Box>
        </Box>

        <Box sx={{ mb: 6 }}>
          <Typography variant="h4" fontWeight={700} sx={{ ...styles.title, mb: 3 }}>
            Financing Considerations
          </Typography>
          <Box
            sx={{
              ...styles.panel,
              p: 3,
            }}
          >
            <Typography variant="h6" fontWeight={700} sx={{ color: colors.gold, mb: 2 }}>
              Pricing Structure
            </Typography>
            <Stack spacing={1.2} sx={{ mb: 3 }}>
              <Typography variant="body1"><b>Starter Mint base price:</b> $4,888.88</Typography>
              <Typography variant="body1"><b>Base Enterprise Mint Engine:</b> $8,888.88</Typography>
              <Typography variant="body1"><b>Top Tier Enterprise Mint Engine:</b> $11,888.88</Typography>
            </Stack>
            <Typography variant="h6" fontWeight={700} sx={{ color: colors.gold, mb: 2 }}>
              Financing Policy
            </Typography>
            <Stack spacing={1}>
              <Typography variant="body2" sx={{ lineHeight: 1.7 }}>
                • Minimum down payment is 25% if financing is approved.
              </Typography>
              <Typography variant="body2" sx={{ lineHeight: 1.7 }}>
                • Enterprise tiers do not include standard advertised financing plans.
              </Typography>
              <Typography variant="body2" sx={{ lineHeight: 1.7 }}>
                • Financing may be considered on a case-by-case basis for enterprise tiers only.
              </Typography>
              <Typography variant="body2" sx={{ lineHeight: 1.7 }}>
                • Terms are negotiable and reviewed individually rather than offered as a fixed schedule.
              </Typography>
            </Stack>
          </Box>
        </Box>

        <Box sx={{ mb: 6 }}>
          <Typography variant="h4" fontWeight={700} sx={{ ...styles.title, mb: 3 }}>
            Deployment Services
          </Typography>
          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)" },
              gap: 2,
            }}
          >
            {deploymentServices.map((service) => (
              <Box key={service.name} sx={{ ...styles.panel, p: 3 }}>
                <Typography variant="h6" fontWeight={700} sx={{ color: colors.gold }}>
                  {service.name}
                </Typography>
                <Typography variant="h5" fontWeight={800} sx={{ mt: 1, mb: 2 }}>
                  {service.price}
                </Typography>
                {service.points.map((point) => (
                  <Typography key={point} variant="body2" sx={{ mb: 1.1, lineHeight: 1.7 }}>
                    • {point}
                  </Typography>
                ))}
              </Box>
            ))}
          </Box>
        </Box>

        <Box sx={{ ...styles.panel, p: 4, mb: 6 }}>
          <Typography variant="h4" fontWeight={700} sx={{ ...styles.title, mb: 2 }}>
            The Peace of Mind Framework
          </Typography>
          <Typography variant="body1" sx={{ lineHeight: 1.8 }}>
            Finality: records cannot be retroactively altered. Independence: the engine continues to function even if
            Alpha CertSig ceases operations. Sovereignty: no external vendor holds custody of your records. Continuity:
            structured digital objects survive system upgrades and personnel changes.
          </Typography>
        </Box>

        <Box sx={{ ...styles.panel, p: 4 }}>
          <Typography variant="h4" fontWeight={700} sx={{ ...styles.title, mb: 2 }}>
            Bottom Line
          </Typography>
          <Typography variant="body1" sx={{ lineHeight: 1.8, mb: 3 }}>
            Alpha CertSig is not an NFT marketplace. It is licensed digital object infrastructure for institutions and
            sovereign creators who need permanent, verifiable records. Spruked owns the press. True Mark curates the vault.
          </Typography>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <Button
              component="a"
              href="https://spruked.com/products/alpha-certsig"
              target="_blank"
              rel="noreferrer"
              variant="contained"
              sx={styles.primaryButton}
            >
              Request Enterprise Quote
            </Button>
            <Button component={RouterLink} to="/contact" variant="outlined" sx={styles.secondaryButton}>
              Contact Spruked
            </Button>
          </Stack>
        </Box>
      </Container>
    </Box>
  );
}
