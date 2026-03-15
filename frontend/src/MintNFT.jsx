import React, { useEffect, useMemo, useState } from "react";
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  MenuItem,
  LinearProgress,
  Alert,
  Stack,
  Divider
} from "@mui/material";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { useMintFlow } from "./context/MintFlowContext";
import { colors, styles } from "./designTokens";

const NFT_TYPES = [
  { value: "K-NFT", label: "Knowledge NFT" },
  { value: "H-NFT", label: "Heirloom NFT" },
  { value: "L-NFT", label: "Legacy NFT" },
  { value: "C-NFT", label: "Custom NFT" }
];

export default function MintNFT() {
  const navigate = useNavigate();
  const { checkoutDraft, setCheckoutDraft, updateWorkspace } = useMintFlow();
  const [form, setForm] = useState({
    name: "",
    email: "",
    nft_type: "K-NFT",
    package_tier: "starter",
    encryption: "none",
    chain: "polygon",
    quantity: 1,
    file: null,
    metadata: ""
  });
  const [progress, setProgress] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fileSummary = useMemo(() => {
    if (!form.file) {
      return null;
    }

    const sizeInMb = form.file.size / (1024 * 1024);
    const formattedSize = sizeInMb < 1024
      ? `${sizeInMb.toFixed(2)} MB`
      : `${(sizeInMb / 1024).toFixed(2)} GB`;

    return {
      name: form.file.name,
      size: formattedSize,
      type: form.file.type || "Unknown file type",
    };
  }, [form.file]);

  useEffect(() => {
    if (!checkoutDraft) {
      return;
    }

    setForm((previous) => ({
      ...previous,
      name: checkoutDraft.name || previous.name,
      email: checkoutDraft.email || previous.email,
      nft_type: checkoutDraft.nft_type || previous.nft_type,
      package_tier: checkoutDraft.package_tier || previous.package_tier,
      encryption: checkoutDraft.encryption || previous.encryption,
      chain: checkoutDraft.chain || previous.chain,
      quantity: checkoutDraft.quantity || previous.quantity,
      metadata: checkoutDraft.metadata || previous.metadata,
      file: previous.file,
    }));
  }, [checkoutDraft]);

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: files ? files[0] : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!form.file) {
      setError("Upload the file you want to mint before continuing.");
      return;
    }

    setProgress(true);
    setCheckoutDraft({
      ...form,
      metadata: form.metadata.trim(),
    });
    updateWorkspace({
      notes: "",
      links: "",
      checklist: "",
    });
    setSuccess("File confirmed. Continue to checkout to review and submit the mint request.");
    setTimeout(() => {
      setProgress(false);
      navigate("/checkout");
    }, 500);
  };

  return (
    <Box sx={{ minHeight: "100vh", background: colors.background, color: colors.text, py: 8 }}>
      <Container maxWidth="sm">
        <Typography variant="h4" fontWeight={700} gutterBottom sx={styles.title}>
          Mint Your NFT
        </Typography>
        <Typography variant="body2" sx={{ mb: 2, opacity: 0.8 }}>
          Upload your knowledge, legacy, or custom asset. <b>All uploaded data is purged after you download your zip file. No personal data is retained except your account info, which is used only for platform communications and marketing. All NFT records are permanently logged with a glyph trace and stored in a secure vault system.</b>
        </Typography>
        <Alert severity="info" sx={{ mb: 2 }}>
          Customer onboarding now follows a clearer path: create or access your account, prepare the asset record, confirm the upload, then continue into checkout for final review.
        </Alert>
        {progress && <LinearProgress sx={{ mb: 2 }} />}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        <Box sx={{ mb: 3, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} sx={{ color: colors.gold, mb: 1 }}>
            Customer Onboarding
          </Typography>
          <Stack spacing={1.2}>
            <Typography variant="body2">1. Sign in or create your account before minting so your vault record can be tied to the correct user.</Typography>
            <Typography variant="body2">2. Choose the NFT type and upload the source file you want certified.</Typography>
            <Typography variant="body2">3. Review the checkout summary, confirm submission, and download the generated vault package.</Typography>
          </Stack>
          <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} sx={{ mt: 2 }}>
            <Button component={RouterLink} to="/login" variant="outlined" sx={styles.secondaryButton}>
              User Login
            </Button>
            <Button component={RouterLink} to="/signup" variant="outlined" sx={styles.secondaryButton}>
              Create Account
            </Button>
            <Button component={RouterLink} to="/checkout" variant="outlined" sx={{ borderColor: colors.neutral, color: colors.neutral, fontWeight: 700 }}>
              View Checkout
            </Button>
          </Stack>
        </Box>
        <Divider sx={{ borderColor: "rgba(255,255,255,0.12)", mb: 3 }} />
        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            <TextField
              label="Full Name"
              name="name"
              value={form.name}
              onChange={handleChange}
              fullWidth
              required
              InputLabelProps={{ style: { color: "#C8CCD0" } }}
              InputProps={{ style: { color: "#F4F7F8" } }}
            />
            <TextField
              label="Email Address"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              fullWidth
              required
              InputLabelProps={{ style: { color: "#C8CCD0" } }}
              InputProps={{ style: { color: "#F4F7F8" } }}
            />
            <TextField
              select
              label="NFT Type"
              name="nft_type"
              value={form.nft_type}
              onChange={handleChange}
              fullWidth
              required
              InputLabelProps={{ style: { color: "#C8CCD0" } }}
              InputProps={{ style: { color: "#F4F7F8" } }}
            >
              {NFT_TYPES.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Metadata (optional)"
              name="metadata"
              value={form.metadata}
              onChange={handleChange}
              fullWidth
              multiline
              minRows={2}
              InputLabelProps={{ style: { color: "#C8CCD0" } }}
              InputProps={{ style: { color: "#F4F7F8" } }}
            />
            <Button
              variant="contained"
              component="label"
              sx={styles.primaryButton}
            >
              Upload File
              <input
                type="file"
                name="file"
                hidden
                required
                onChange={handleChange}
              />
            </Button>
            {fileSummary && (
              <Alert severity="success">
                File uploaded: <b>{fileSummary.name}</b> | {fileSummary.size} | {fileSummary.type}
              </Alert>
            )}
            <Button type="submit" variant="contained" fullWidth sx={styles.primaryButton}>
              Continue to Checkout
            </Button>
            <Button
              type="button"
              component={RouterLink}
              to="/cart"
              variant="outlined"
              fullWidth
              sx={{ borderColor: colors.neutral, color: colors.neutral, fontWeight: 700 }}
            >
              Save and Return Later
            </Button>
          </Stack>
        </form>
      </Container>
    </Box>
  );
}
