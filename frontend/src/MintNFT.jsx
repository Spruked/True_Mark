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
import { getUserAuthHeaders } from "./authStorage";

const API_BASE = getBackendApiBase();

const NFT_TYPES = [
  { value: "H", label: "H — Heirloom NFT", color: "Emerald" },
  { value: "K", label: "K — Knowledge NFT", color: "Blue-Teal" },
  { value: "L", label: "L — Legacy NFT", color: "Violet" },
  { value: "B", label: "B — Bespoke NFT", color: "Blue-Gold" },
  { value: "HL", label: "HL — Licensable Heirloom NFT", color: "Emerald" },
  { value: "KL", label: "KL — Licensable Knowledge NFT", color: "Blue-Teal" },
  { value: "LL", label: "LL — Licensable Legacy NFT", color: "Violet" },
  { value: "BL", label: "BL — Licensable Bespoke NFT", color: "Blue-Gold" },
  { value: "C", label: "C — Custom Contract NFT", color: "Gold-Amber" },
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
    nft_type: "K",
    object_id: "",
    frame_id: "frame-01-engraved-single-line",
    package_tier: "p2",
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
  const [frames, setFrames] = useState([]);
  const [sealedObjects, setSealedObjects] = useState([]);
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
        const [standardResponse, framesResponse] = await Promise.all([
          axios.get(`${API_BASE}/mint-standard`),
          axios.get(`${API_BASE}/certificate-frames`),
        ]);
        if (!active) {
          return;
        }

        setMintStandard(standardResponse.data);
        setFrames(framesResponse.data || []);
        setForm((previous) => ({
          ...previous,
          node_id: standardResponse.data.node_id || previous.node_id || "TMK",
          region_code: previous.region_code === "US"
            ? (standardResponse.data.region_code || previous.region_code || "US")
            : (previous.region_code || standardResponse.data.region_code || "US"),
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
    axios.get(`${API_BASE}/api/objects?state=SEALED`, { headers: getUserAuthHeaders() })
      .then(({ data }) => setSealedObjects(data.objects || []))
      .catch(() => setSealedObjects([]));
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
      object_id: checkoutDraft.object_id || previous.object_id,
      frame_id: checkoutDraft.frame_id || previous.frame_id,
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
        const response = await axios.get(`${API_BASE}/payments/${paymentSession.payment_token}`, { headers: getUserAuthHeaders() });
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
      setError("Add the evidence file you want to authenticate before continuing.");
      return;
    }
    if (!form.object_id) {
      setError("Select the sealed object record that authorizes this optional digital extension.");
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
    setSuccess("Evidence staged. Continue to review the certificate profile and next authority step.");
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
      }, { headers: getUserAuthHeaders() });
      setMintResult(response.data);
      setSuccess(`Object commitment completed. ${response.data.nft_identifier} is now recorded and invoice ${response.data.invoice_number} is ready.`);
      clearPaymentSession();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "The object could not be committed right now.");
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
          Authenticate an Object
        </Typography>
        <Typography variant="body2" sx={{ mb: 2, opacity: 0.8 }}>
          Build a private object record. Upload evidence, add provenance and ownership context, choose a certificate profile, and review the record before any authoritative commitment.
        </Typography>
        <Alert severity="info" sx={{ mb: 2 }}>
          This is your working copy inside Perpetuum. Uploads remain mutable until you explicitly commit and seal the object record.
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
            <Typography variant="body2">1. Sign in or create your account to open your private Sanctum.</Typography>
            <Typography variant="body2">2. Stage evidence and supporting object information.</Typography>
            <Typography variant="body2">3. Review the canonical record and choose a Prime Layer certificate profile.</Typography>
            <Typography variant="body2">4. Commit and seal only when you are ready to create an authoritative Vault event.</Typography>
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
              Review Complete, Ready for Commitment
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
                Commit and Seal Object
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
            This working request was canceled after processing began. Start again from a new evidence package if you still want to continue.
          </Alert>
        )}

        {mintResult && (
          <Box sx={{ mb: 3, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} sx={{ color: colors.gold, mb: 1 }}>
              Object Sealed
            </Typography>
            <Stack spacing={1.2}>
              <Typography><b>Serial:</b> {mintResult.serial}</Typography>
              <Typography><b>Object Identifier:</b> {mintResult.nft_identifier}</Typography>
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
                label="Authority Node Code"
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
                helperText="Geographic region for the object record, for example US or EU."
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
                label="Sealed authoritative object"
                name="object_id"
                value={form.object_id}
                onChange={(event) => {
                  const selected = sealedObjects.find((item) => item.id === event.target.value);
                  setForm((previous) => ({ ...previous, object_id: event.target.value, package_tier: selected?.certificate_profile || previous.package_tier }));
                }}
                fullWidth
                required
                helperText="Only a sealed account-owned object may enter the digital-extension flow."
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              >
                <MenuItem value="" disabled>Select a sealed object</MenuItem>
                {sealedObjects.map((item) => <MenuItem key={item.id} value={item.id}>{item.title} · {item.certificate_profile}</MenuItem>)}
              </TextField>
              <TextField
                select
                label="Object Type"
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
                    {option.label} · {option.color}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Certificate Frame"
                name="frame_id"
                value={form.frame_id}
                onChange={handleChange}
                fullWidth
                required
                helperText="Presentation frame only. It does not change the selected prime evidence depth."
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                FormHelperTextProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              >
                {(frames.length ? frames : [{ frame_id: form.frame_id, name: "Engraved Single-Line", group_label: "Classic Forensic" }]).map((frame) => (
                  <MenuItem key={frame.frame_id} value={frame.frame_id}>
                    {frame.number ? `${frame.number}. ` : ""}{frame.name} · {frame.group_label}
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
