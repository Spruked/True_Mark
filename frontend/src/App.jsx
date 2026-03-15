import React, { useRef, useState } from "react";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import { Link as RouterLink } from "react-router-dom";
import { colors, styles } from "./designTokens";

function App() {
  const videoRef = useRef(null);
  const [muted, setMuted] = useState(true);

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !muted;
      setMuted(!muted);
    }
  };
  return (
    <Box
      sx={{
        position: "relative",
        minHeight: "100vh",
        overflow: "hidden",
        backgroundColor: colors.background,
      }}
    >
      {/* Video background */}
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
        <source src="/assets/Video_Script_Correction_and_Generation.mp4" type="video/mp4" />
      </video>
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          background: "rgba(11, 18, 32, 0.75)",
          zIndex: 0,
        }}
      />
      {/* Mute/Unmute Button */}
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
          cursor: "pointer"
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
          color: colors.text,
          textAlign: "center",
        }}
      >
        {/* Logo */}
        <Box
          sx={{
            width: 152,
            height: 152,
            margin: "0 auto 24px",
            borderRadius: "50%",
            overflow: "hidden",
            boxShadow: "0 16px 32px rgba(0,0,0,0.28)",
          }}
        >
          <img
            src="/assets/truemarkseal.png"
            alt="True Mark Seal"
            style={{ width: "100%", height: "100%", objectFit: "cover", display: "block" }}
          />
        </Box>
        <Typography
          variant="h2"
          fontWeight={700}
          gutterBottom
          sx={{ fontFamily: "Inter, system-ui, sans-serif", color: colors.gold }}
        >
          True Mark Mint Engine
        </Typography>
        <Typography
          variant="h5"
          color="#F4F7F8"
          gutterBottom
          sx={{ fontFamily: "Inter, system-ui, sans-serif", opacity: 0.95 }}
        >
          Mint Knowledge, Heirloom, Legacy, and Custom NFTs with forensic-grade certificates and seamless checkout.
        </Typography>
        <Alert severity="info" sx={{ mt: 4, mb: 3, textAlign: "left", background: "rgba(255,255,255,0.92)" }}>
          True Mark presents a forensic-grade certification system for knowledge records, heirloom archives, and institutional legacy assets.
        </Alert>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2} justifyContent="center" sx={{ mt: 4 }}>
          <Button
            variant="outlined"
            size="large"
            sx={styles.secondaryButton}
            component={RouterLink}
            to="/about"
          >
            About
          </Button>
          <Button
            variant="contained"
            size="large"
            sx={styles.primaryButton}
            component={RouterLink}
            to="/mint"
          >
            Mint NFT
          </Button>
        </Stack>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2} justifyContent="center" sx={{ mt: 2 }}>
          <Button
            variant="outlined"
            size="large"
            sx={styles.secondaryButton}
            component={RouterLink}
            to="/login"
          >
            User Login
          </Button>
          <Button
            variant="outlined"
            size="large"
            sx={styles.secondaryButton}
            component={RouterLink}
            to="/admin/login"
          >
            Admin Login
          </Button>
          <Button
            variant="outlined"
            size="large"
            sx={styles.secondaryButton}
            component={RouterLink}
            to="/checkout"
          >
            Checkout
          </Button>
        </Stack>
        <Box
          sx={{
            mt: 6,
            pt: 5,
            borderTop: `1px solid ${colors.border}`,
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)" },
            gap: 2,
            textAlign: "left",
          }}
        >
          {[
            {
              glyph: "K",
              title: "Knowledge NFTs",
              text: "Research certification, intellectual property proof, and timestamped authorship records.",
            },
            {
              glyph: "H",
              title: "Heirloom NFTs",
              text: "Permanent preservation of generational knowledge, family records, and curated archives.",
            },
            {
              glyph: "L",
              title: "Legacy NFTs",
              text: "Institutional frameworks, operational systems, and enduring governance records.",
            },
          ].map((item) => (
            <Box key={item.title} sx={{ p: 3, borderRadius: 3, background: "rgba(255,255,255,0.06)", border: `1px solid ${colors.border}` }}>
              <Box sx={{ width: 42, height: 42, borderRadius: "50%", display: "grid", placeItems: "center", background: colors.gold, color: "#111111", fontWeight: 800, mb: 2 }}>
                {item.glyph}
              </Box>
              <Typography sx={{ color: colors.gold, fontWeight: 700, mb: 1 }}>{item.title}</Typography>
              <Typography variant="body2" sx={{ color: colors.neutral, lineHeight: 1.7 }}>{item.text}</Typography>
            </Box>
          ))}
        </Box>

        <Box
          sx={{
            mt: 5,
            p: 3,
            borderRadius: 3,
            textAlign: "left",
            background: "rgba(255,255,255,0.06)",
            border: `1px solid ${colors.border}`,
          }}
        >
          <Typography variant="overline" sx={{ color: colors.mutedText, letterSpacing: 1.2 }}>
            Platform Direction
          </Typography>
          <Typography variant="h5" fontWeight={700} sx={{ color: colors.gold, mt: 1, mb: 1.5 }}>
            True Mark stands on its own as a mint and certification platform.
          </Typography>
          <Typography variant="body1" sx={{ color: colors.neutral, lineHeight: 1.8, mb: 2 }}>
            True Mark Mint Engine is a standalone website and mint workflow focused on payment-cleared issuance,
            forensic recordkeeping, and long-term evidentiary continuity without marketplace dependency.
          </Typography>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <Button component={RouterLink} to="/about" variant="contained" sx={styles.primaryButton}>
              Explore True Mark
            </Button>
            <Button
              component="a"
              href="https://spruked.com"
              target="_blank"
              rel="noreferrer"
              variant="outlined"
              sx={styles.secondaryButton}
            >
              Open Spruked
            </Button>
          </Stack>
        </Box>
      </Container>
    </Box>
  );
}

export default App;
