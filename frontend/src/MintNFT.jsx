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
  Divider,
} from "@mui/material";
import axios from "axios";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { useMintFlow } from "./context/MintFlowContext";
import { colors, styles } from "./designTokens";
import { getBackendApiBase } from "./apiBase";

const API_BASE = getBackendApiBase();

const NFT_TYPES = [
  { value: "K-NFT", label: "Knowledge NFT" },
  { value: "H-NFT", label: "Heirloom NFT" },
  { value: "L-NFT", label: "Legacy NFT" },
  { value: "C-NFT", label: "Custom NFT" },
];

export default function MintNFT() {
  const navigate = useNavigate();
  const {
    checkoutDraft,
    setCheckoutDraft,
    paymentSession,
    setPaymentSession,
    clearPaymentSession,
    updateWorkspace,
  } = useMintFlow();
  const [form, setForm] = useState({
    name: "",
    email: "",
    node_id: "TMK",
    region_code: "US",
    registrant_code: "",
    nft_type: "K-NFT",
    package_tier: "starter",
    encryption: "none",
    chain: "polygon",
    quantity: 1,
    file: null,
    metadata: "",
  });
  const [mintStandard, setMintStandard] = useState({
    node_id: "TMK",
    region_code: "US",
    identifier_format: "TYPE-NODE-REGION-YEAR-USER-SEQ",
    type_codes: {},
  });
  const [progress, setProgress] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [mintResult, setMintResult] = useState(null);

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
    let active = true;

    async function loadMintStandard() {
      try {
        const response = await axios.get(`${API_BASE}/mint-standard`);
        if (!active) {
          return;
        }

        setMintStandard(response.data);
        setForm((previous) => ({
          ...previous,
          node_id: response.data.node_id || previous.node_id || "TMK",
          region_code: previous.region_code === "US"
            ? (response.data.region_code || previous.region_code || "US")
            : (previous.region_code || response.data.region_code || "US"),
        }));
      } catch {
        if (active) {
          setMintStandard((previous) => ({
            ...previous,
          }));
        }
      }
    }

    loadMintStandard();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!checkoutDraft) {
      return;
    }

    setForm((previous) => ({
      ...previous,
      name: checkoutDraft.name || previous.name,
      email: checkoutDraft.email || previous.email,
      node_id: checkoutDraft.node_id || previous.node_id || mintStandard.node_id,
      region_code: checkoutDraft.region_code || checkoutDraft.industry || previous.region_code || mintStandard.region_code,
      registrant_code: checkoutDraft.registrant_code || checkoutDraft.prefix || previous.registrant_code,
      nft_type: checkoutDraft.nft_type || previous.nft_type,
      package_tier: checkoutDraft.package_tier || previous.package_tier,
      encryption: checkoutDraft.encryption || previous.encryption,
      chain: checkoutDraft.chain || previous.chain,
      quantity: checkoutDraft.quantity || previous.quantity,
      metadata: checkoutDraft.metadata || previous.metadata,
      file: previous.file,
    }));
  }, [checkoutDraft, mintStandard.node_id, mintStandard.region_code]);

  useEffect(() => {
    let active = true;

    async function refreshPaymentSession() {
      if (!paymentSession?.payment_token) {
        return;
      }

      try {
        const response = await axios.get(`${API_BASE}/payments/${paymentSession.payment_token}`);
        if (active) {
          setPaymentSession(response.data);
        }
      } catch {
        if (active) {
          clearPaymentSession();
        }
      }
    }

    refreshPaymentSession();

    return () => {
      active = false;
    };
  }, [paymentSession?.payment_token, setPaymentSession, clearPaymentSession]);

  const handleChange = (event) => {
    const { name, value, files } = event.target;
    const normalizedValue = name === "registrant_code" || name === "region_code"
      ? value.toUpperCase()
      : value;
    setForm((previous) => ({
      ...previous,
      [name]: files ? files[0] : normalizedValue,
    }));
  };

  const handlePrepareForCheckout = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");
    setMintResult(null);

    if (!form.file) {
      setError("Upload the file you want to mint before continuing.");
      return;
    }

    setProgress(true);
    setCheckoutDraft({
      ...form,
      node_id: form.node_id,
      region_code: form.region_code.trim().toUpperCase(),
      registrant_code: form.registrant_code.trim().toUpperCase(),
      prefix: form.registrant_code.trim().toUpperCase(),
      industry: form.region_code.trim().toUpperCase(),
      metadata: form.metadata.trim(),
    });
    updateWorkspace({
      notes: "",
      links: "",
      checklist: "",
    });
    setSuccess("File confirmed. Continue to checkout for the estimate and payment step.");
    setTimeout(() => {
      setProgress(false);
      navigate("/checkout");
    }, 500);
  };

  const handleFinalizeMint = async () => {
    if (!paymentSession?.payment_token) {
      return;
    }

    setProgress(true);
    setError("");
    setSuccess("");
    setMintResult(null);

    try {
      const response = await axios.post(`${API_BASE}/mint/complete`, {
        payment_token: paymentSession.payment_token,
      });
      setMintResult(response.data);
      setSuccess(`Mint completed. ${response.data.nft_identifier} is now recorded and invoice ${response.data.invoice_number} is ready.`);
      clearPaymentSession();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "The NFT could not be minted right now.");
    } finally {
      setProgress(false);
    }
  };

  const hasPaidSession = paymentSession?.status === "payment_cleared";
  const wasCanceledAfterPayment = paymentSession?.status === "canceled_after_payment";

  return (
    <Box sx={{ minHeight: "100vh", background: colors.background, color: colors.text, py: 8 }}>
      <Container maxWidth="sm">
        <Typography variant="h4" fontWeight={700} gutterBottom sx={styles.title}>
          Mint Your NFT
        </Typography>
        <Typography variant="body2" sx={{ mb: 2, opacity: 0.8 }}>
          Upload your knowledge, legacy, or custom asset. Your file is staged for pricing first, payment is processed second, and the actual NFT mint happens only after you return here to finalize it.
        </Typography>
        <Alert severity="info" sx={{ mb: 2 }}>
          True Mark is a standalone mint platform. Upload and prepare your record here, process payment in checkout, then return to this page to complete the NFT mint and receive the final invoice.
        </Alert>
        {progress && <LinearProgress sx={{ mb: 2 }} />}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        {mintResult && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Invoice delivery: {mintResult.invoice_email_status}. {mintResult.invoice_email_detail}
          </Alert>
        )}

        <Box sx={{ mb: 3, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
          <Typography variant="h6" fontWeight={700} sx={{ color: colors.gold, mb: 1 }}>
            Customer Workflow
          </Typography>
          <Stack spacing={1.2}>
            <Typography variant="body2">1. Sign in or create your account before preparing the mint request.</Typography>
            <Typography variant="body2">2. Upload the source file and save the request for checkout.</Typography>
            <Typography variant="body2">3. In Checkout, review the estimate and process payment.</Typography>
            <Typography variant="body2">4. Return here to mint the NFT only after payment clears.</Typography>
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

        {hasPaidSession && (
          <Box sx={{ mb: 3, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} sx={{ color: colors.gold, mb: 1 }}>
              Payment Cleared, Ready to Mint
            </Typography>
            <Stack spacing={1.2}>
              <Typography><b>Payment Reference:</b> {paymentSession.payment_reference}</Typography>
              <Typography><b>Receipt Number:</b> {paymentSession.receipt_number}</Typography>
              <Typography><b>Node Code:</b> {paymentSession.node_id || mintStandard.node_id}</Typography>
              <Typography><b>Region:</b> {paymentSession.region_code || mintStandard.region_code}</Typography>
              <Typography><b>Registrant Code:</b> {paymentSession.registrant_code || "PUBLIC"}</Typography>
              <Typography><b>File:</b> {paymentSession.file_name}</Typography>
              <Typography><b>Estimated Total Paid:</b> ${Number(paymentSession.total_usd || 0).toFixed(2)}</Typography>
              <Typography><b>Projected Serial:</b> {paymentSession.minted_serial || "The next available True Mark serial will be assigned at mint time."}</Typography>
              <Typography><b>Minted Identifier:</b> {paymentSession.minted_nft_identifier || "The canonical identifier will be assigned at mint time."}</Typography>
            </Stack>
            <Stack spacing={2} sx={{ mt: 2 }}>
              <Button onClick={handleFinalizeMint} variant="contained" sx={styles.primaryButton}>
                Mint NFT Now
              </Button>
              {paymentSession.receipt_download_url && (
                <Button href={paymentSession.receipt_download_url} variant="outlined" sx={styles.secondaryButton}>
                  Download Payment Receipt
                </Button>
              )}
              <Button component={RouterLink} to="/checkout" variant="outlined" sx={{ borderColor: colors.neutral, color: colors.neutral, fontWeight: 700 }}>
                Back to Checkout
              </Button>
            </Stack>
          </Box>
        )}

        {wasCanceledAfterPayment && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            This payment was canceled after processing began. The request must be started again from a new upload if you still want to mint.
          </Alert>
        )}

        {mintResult && (
          <Box sx={{ mb: 3, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} sx={{ color: colors.gold, mb: 1 }}>
              Mint Complete
            </Typography>
            <Stack spacing={1.2}>
              <Typography><b>Serial:</b> {mintResult.serial}</Typography>
              <Typography><b>NFT Identifier:</b> {mintResult.nft_identifier}</Typography>
              <Typography><b>Node Code:</b> {mintResult.node_id || mintStandard.node_id}</Typography>
              <Typography><b>Region:</b> {mintResult.region_code || mintStandard.region_code}</Typography>
              <Typography><b>Registrant Code:</b> {mintResult.registrant_code || form.registrant_code || "PUBLIC"}</Typography>
              <Typography><b>Invoice:</b> {mintResult.invoice_number}</Typography>
              <Typography><b>Payment Reference:</b> {mintResult.payment_reference}</Typography>
              <Typography><b>Receipt Number:</b> {mintResult.receipt_number}</Typography>
            </Stack>
            <Stack spacing={2} sx={{ mt: 2 }}>
              {mintResult.invoice_download_url && (
                <Button href={mintResult.invoice_download_url} variant="outlined" sx={styles.secondaryButton}>
                  Download Final Invoice
                </Button>
              )}
              {mintResult.receipt_download_url && (
                <Button href={mintResult.receipt_download_url} variant="outlined" sx={styles.secondaryButton}>
                  Download Payment Receipt
                </Button>
              )}
              {mintResult.vault_download_url && (
                <Button href={mintResult.vault_download_url} variant="outlined" sx={styles.secondaryButton}>
                  Download Vault Package
                </Button>
              )}
            </Stack>
          </Box>
        )}

        <Divider sx={{ borderColor: "rgba(255,255,255,0.12)", mb: 3 }} />

        {!hasPaidSession && (
          <form onSubmit={handlePrepareForCheckout}>
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
                label="Mint Node Code"
                name="node_id"
                value={form.node_id}
                fullWidth
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ readOnly: true, style: { color: "#F4F7F8" } }}
              />
              <TextField
                label="Region Code"
                name="region_code"
                value={form.region_code}
                onChange={handleChange}
                fullWidth
                required
                helperText="Geographic region for the mint record, for example US or EU."
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                FormHelperTextProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />
              <TextField
                label="Registrant Code"
                name="registrant_code"
                value={form.registrant_code}
                onChange={handleChange}
                fullWidth
                required
                helperText="Short customer or entity code used in the identifier, for example SPRUKED or HARVARD."
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                FormHelperTextProps={{ style: { color: "#C8CCD0" } }}
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
              <Button variant="contained" component="label" sx={styles.primaryButton}>
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
        )}
      </Container>
    </Box>
  );
}
