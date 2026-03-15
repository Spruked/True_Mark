import React, { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Container,
  FormControl,
  FormControlLabel,
  LinearProgress,
  MenuItem,
  Radio,
  RadioGroup,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import axios from "axios";
import { Link as RouterLink } from "react-router-dom";
import { useMintFlow } from "./context/MintFlowContext";
import { colors, styles } from "./designTokens";
import { getBackendApiBase } from "./apiBase";

const API_BASE = getBackendApiBase();

const emptyPricing = {
  nft_types: {},
  package_tiers: {},
  encryption_options: {},
  chains: {},
  storage: { included_gb: 1, additional_gb_price: 5 },
  currency: "USD",
  settlement: {
    pricing_basis: "fiat_only",
    display_currency: "USD",
    crypto_quote_enabled: true,
    customer_wallet_required: false,
    crypto_quote_note: "",
    mint_execution_note: "",
  },
};

export default function Checkout() {
  const {
    checkoutDraft,
    clearCheckoutDraft,
    paymentSession,
    setPaymentSession,
    clearPaymentSession,
    setCheckoutDraft,
  } = useMintFlow();
  const [pricing, setPricing] = useState(emptyPricing);
  const [quote, setQuote] = useState(null);
  const [nextSerial, setNextSerial] = useState("");
  const [mintStandard, setMintStandard] = useState({
    node_id: "TM01",
    region_code: "US",
    identifier_format: "TYPE-NODE-REGION-YEAR-USER-SEQ",
    type_codes: {},
  });
  const [paymentMethod, setPaymentMethod] = useState("fiat");
  const [agree, setAgree] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [selections, setSelections] = useState({
    package_tier: "starter",
    encryption: "none",
    chain: "polygon",
    quantity: 1,
  });

  useEffect(() => {
    let active = true;

    async function loadCheckoutMetadata() {
      try {
        const [pricingResponse, serialResponse, mintStandardResponse] = await Promise.all([
          axios.get(`${API_BASE}/pricing`),
          axios.get(`${API_BASE}/serial/next`),
          axios.get(`${API_BASE}/mint-standard`),
        ]);

        if (!active) {
          return;
        }

        setPricing(pricingResponse.data);
        setNextSerial(serialResponse.data.next_serial);
        setMintStandard(mintStandardResponse.data);
      } catch {
        if (active) {
          setError("Checkout is available, but pricing details could not be loaded from the backend.");
        }
      }
    }

    loadCheckoutMetadata();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (!checkoutDraft) {
      return;
    }

    setSelections({
      package_tier: checkoutDraft.package_tier || "starter",
      encryption: checkoutDraft.encryption || "none",
      chain: checkoutDraft.chain || "polygon",
      quantity: checkoutDraft.quantity || 1,
    });
    setPaymentMethod(checkoutDraft.payment_method || "fiat");
  }, [checkoutDraft]);

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

  const fileSizeGb = useMemo(() => {
    if (checkoutDraft?.file?.size) {
      return checkoutDraft.file.size / (1024 * 1024 * 1024);
    }

    if (!checkoutDraft?.fileSize) {
      return 0;
    }

    return checkoutDraft.fileSize / (1024 * 1024 * 1024);
  }, [checkoutDraft]);

  useEffect(() => {
    let active = true;

    async function loadQuote() {
      if (!checkoutDraft) {
        setQuote(null);
        return;
      }

      setQuoteLoading(true);

      try {
        const response = await axios.post(`${API_BASE}/quote`, {
          nft_type: checkoutDraft.nft_type || "K-NFT",
          package_tier: selections.package_tier,
          encryption: selections.encryption,
          chain: selections.chain,
          quantity: Number(selections.quantity) || 1,
          estimated_storage_gb: fileSizeGb,
          email: checkoutDraft.email,
        });

        if (!active) {
          return;
        }

        setQuote(response.data);
      } catch {
        if (active) {
          setQuote(null);
          setError("The backend could not calculate a pricing quote for this mint.");
        }
      } finally {
        if (active) {
          setQuoteLoading(false);
        }
      }
    }

    loadQuote();

    return () => {
      active = false;
    };
  }, [checkoutDraft, selections, fileSizeGb]);

  const updateSelection = (field, value) => {
    const nextSelections = {
      ...selections,
      [field]: field === "quantity" ? Math.max(Number(value) || 1, 1) : value,
    };

    setSelections(nextSelections);

    if (checkoutDraft) {
      setCheckoutDraft({
        ...checkoutDraft,
        ...nextSelections,
        payment_method: paymentMethod,
      });
    }
  };

  const handleProcessPayment = async () => {
    if (!checkoutDraft?.file) {
      setError("A live file must be attached before payment can be processed. Return to Mint to reattach the file.");
      return;
    }

    if (!agree) {
      setError("You need to confirm the estimate, payment policy, and cancellation fee before continuing.");
      return;
    }

    setProcessing(true);
    setError("");
    setSuccess("");

    try {
      const data = new FormData();
      data.append("name", checkoutDraft.name);
      data.append("email", checkoutDraft.email);
      data.append("registrant_code", checkoutDraft.registrant_code || checkoutDraft.prefix || "PUBLIC");
      data.append("region_code", checkoutDraft.region_code || checkoutDraft.industry || mintStandard.region_code || "US");
      data.append("prefix", checkoutDraft.registrant_code || checkoutDraft.prefix || "PUBLIC");
      data.append("industry", checkoutDraft.region_code || checkoutDraft.industry || mintStandard.region_code || "US");
      data.append("nft_type", checkoutDraft.nft_type);
      data.append("file", checkoutDraft.file);
      data.append("metadata", checkoutDraft.metadata || "");
      data.append("package_tier", selections.package_tier);
      data.append("encryption", selections.encryption);
      data.append("chain", selections.chain);
      data.append("quantity", String(selections.quantity));
      data.append("payment_method", paymentMethod);

      const response = await axios.post(`${API_BASE}/payments/process`, data);
      setPaymentSession(response.data);
      setSuccess(`Payment cleared. Receipt ${response.data.receipt_number} is ready. Return to Mint to complete the NFT issuance.`);
      clearCheckoutDraft();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Payment could not be processed. Please try again.");
    } finally {
      setProcessing(false);
    }
  };

  const handleCancelAfterPayment = async () => {
    if (!paymentSession?.payment_token) {
      return;
    }

    setProcessing(true);
    setError("");
    setSuccess("");

    try {
      const response = await axios.post(`${API_BASE}/payments/${paymentSession.payment_token}/cancel`);
      setPaymentSession(response.data);
      setSuccess(response.data.message || "Payment canceled.");
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "The payment could not be canceled right now.");
    } finally {
      setProcessing(false);
    }
  };

  const hasPaidSession = paymentSession?.status === "payment_cleared";
  const wasCanceledAfterPayment = paymentSession?.status === "canceled_after_payment";

  return (
    <Box sx={{ minHeight: "100vh", background: colors.background, color: colors.text, py: 8 }}>
      <Container maxWidth="lg">
        <Typography variant="h4" fontWeight={700} gutterBottom sx={styles.title}>
          Checkout
        </Typography>
        <Typography variant="body1" sx={{ mb: 3, opacity: 0.84 }}>
          Upload first, review the estimate here, process payment, then return to Mint to finalize the NFT.
        </Typography>
        <Alert severity="info" sx={{ mb: 3 }}>
          Prices shown here are estimates until payment is processed. Payment must clear before the NFT can be minted.
          If a paid request is canceled after processing has started, a $5.00 cancellation fee applies.
        </Alert>

        {!checkoutDraft && !paymentSession && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            There is no active checkout request yet. Start from Mint, upload your file, and return here for the estimate and payment step.
          </Alert>
        )}

        {(processing || quoteLoading) && <LinearProgress sx={{ mb: 3 }} />}
        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 3 }}>{success}</Alert>}

        {paymentSession && (
          <Alert severity={wasCanceledAfterPayment ? "warning" : "info"} sx={{ mb: 3 }}>
            Payment reference: {paymentSession.payment_reference} | Receipt: {paymentSession.receipt_number} | Status: {paymentSession.status}
            {paymentSession.refund_due_usd != null ? ` | Refund due: $${Number(paymentSession.refund_due_usd).toFixed(2)}` : ""}
          </Alert>
        )}

        <Stack direction={{ xs: "column", xl: "row" }} spacing={3}>
          <Box sx={{ flex: 1, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Upload Summary
            </Typography>
            <Stack spacing={1.5}>
              <Typography><b>Name:</b> {checkoutDraft?.name || paymentSession?.user_name || "Not provided yet"}</Typography>
              <Typography><b>Email:</b> {checkoutDraft?.email || paymentSession?.user_email || "Not provided yet"}</Typography>
              <Typography><b>Node ID:</b> {checkoutDraft?.node_id || paymentSession?.node_id || mintStandard.node_id}</Typography>
              <Typography><b>Region:</b> {checkoutDraft?.region_code || paymentSession?.region_code || mintStandard.region_code}</Typography>
              <Typography><b>Registrant Code:</b> {checkoutDraft?.registrant_code || checkoutDraft?.prefix || paymentSession?.registrant_code || "PUBLIC"}</Typography>
              <Typography><b>NFT Type:</b> {checkoutDraft?.nft_type || paymentSession?.nft_type || "Not selected yet"}</Typography>
              <Typography><b>File:</b> {checkoutDraft?.file?.name || checkoutDraft?.fileName || paymentSession?.file_name || "No file attached"}</Typography>
              <Typography><b>Estimated file size:</b> {checkoutDraft ? `${(fileSizeGb * 1024).toFixed(2)} MB` : "Stored on the backend"}</Typography>
              <Typography><b>Projected serial:</b> {nextSerial || paymentSession?.minted_serial || "Loading..."}</Typography>
              <Typography><b>Minted identifier:</b> {paymentSession?.minted_nft_identifier || "Assigned after payment clears and mint is finalized."}</Typography>
              <Typography><b>Metadata:</b> {checkoutDraft?.metadata || "Metadata is staged with the uploaded file."}</Typography>
              {!checkoutDraft?.file && checkoutDraft?.fileName && !paymentSession && (
                <Alert severity="warning">
                  This order was restored from the protected workspace. Reattach the original file in Mint before payment.
                </Alert>
              )}
            </Stack>
          </Box>

          <Box sx={{ flex: 1, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Package Settings
            </Typography>
            <Stack spacing={2}>
              <TextField
                select
                label="Package Tier"
                value={selections.package_tier}
                onChange={(event) => updateSelection("package_tier", event.target.value)}
                fullWidth
                disabled={hasPaidSession}
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              >
                {Object.entries(pricing.package_tiers || {}).map(([value, option]) => (
                  <MenuItem key={value} value={value}>
                    {option.name} ({option.layers} layers)
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                select
                label="Encryption"
                value={selections.encryption}
                onChange={(event) => updateSelection("encryption", event.target.value)}
                fullWidth
                disabled={hasPaidSession}
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              >
                {Object.entries(pricing.encryption_options || {}).map(([value, option]) => (
                  <MenuItem key={value} value={value}>
                    {option.name}
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                select
                label="Chain"
                value={selections.chain}
                onChange={(event) => updateSelection("chain", event.target.value)}
                fullWidth
                disabled={hasPaidSession}
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              >
                {Object.entries(pricing.chains || {}).map(([value, option]) => (
                  <MenuItem key={value} value={value}>
                    {option.name}
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                label="Quantity"
                type="number"
                value={selections.quantity}
                onChange={(event) => updateSelection("quantity", event.target.value)}
                fullWidth
                disabled={hasPaidSession}
                inputProps={{ min: 1 }}
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />

              <Typography variant="body2" sx={{ opacity: 0.84 }}>
                First {pricing.storage?.included_gb ?? 1} GB is included. Additional storage is currently ${pricing.storage?.additional_gb_price ?? 5} per GB.
              </Typography>
            </Stack>
          </Box>

          <Box sx={{ flex: 1, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Estimate and Payment
            </Typography>
            {quote ? (
              <Stack spacing={1.25}>
                <Typography><b>Base Mint:</b> ${quote.breakdown.base_nft.total.toFixed(2)}</Typography>
                <Typography><b>Package:</b> ${quote.breakdown.package_tier.total.toFixed(2)}</Typography>
                <Typography><b>Encryption:</b> ${quote.breakdown.encryption.total.toFixed(2)}</Typography>
                <Typography><b>Chain:</b> ${quote.breakdown.chain.total.toFixed(2)}</Typography>
                <Typography><b>Storage:</b> ${quote.breakdown.storage.total.toFixed(2)}</Typography>
                {quote.discount_amount > 0 && (
                  <Typography sx={{ color: colors.gold }}>
                    <b>Bulk Discount:</b> -${quote.discount_amount.toFixed(2)}
                  </Typography>
                )}
                <Typography><b>Processing Fee:</b> ${quote.processing_fee.toFixed(2)}</Typography>
                <Typography><b>Estimated Tax:</b> ${Number(quote.estimated_tax || 0).toFixed(2)}</Typography>
                <Typography variant="h5" sx={{ color: colors.gold, pt: 1 }}>
                  Estimated Total: ${Number(quote.grand_total ?? quote.total).toFixed(2)}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.84 }}>
                  Per unit: ${quote.per_unit_total.toFixed(2)} {quote.currency}
                </Typography>
                {quote.tax_state && (
                  <Typography variant="body2" sx={{ opacity: 0.84 }}>
                    Tax basis: {quote.tax_state}
                  </Typography>
                )}
              </Stack>
            ) : (
              <Typography variant="body2" sx={{ opacity: 0.84 }}>
                A live estimate will appear here after the backend pricing engine responds.
              </Typography>
            )}

            <FormControl sx={{ mt: 3, mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: colors.gold }}>
                Payment Path
              </Typography>
              <RadioGroup
                value={paymentMethod}
                onChange={(event) => {
                  setPaymentMethod(event.target.value);
                  if (checkoutDraft) {
                    setCheckoutDraft({
                      ...checkoutDraft,
                      payment_method: event.target.value,
                    });
                  }
                }}
              >
                <FormControlLabel value="fiat" control={<Radio sx={{ color: colors.gold }} />} label="Fiat payment in USD" />
                <FormControlLabel value="crypto" control={<Radio sx={{ color: colors.gold }} />} label="Crypto-equivalent settlement quote" />
              </RadioGroup>
            </FormControl>

            {paymentMethod === "crypto" && (
              <Alert severity="info" sx={{ mb: 2 }}>
                This only affects settlement quoting. The NFT still will not mint until payment clears and you return to Mint for final issuance.
              </Alert>
            )}

            <FormControlLabel
              control={<Checkbox checked={agree} onChange={(event) => setAgree(event.target.checked)} sx={{ color: colors.gold }} />}
              label="I confirm this estimate, agree to the payment step, and understand the $5 cancellation fee after payment."
            />

            <Stack spacing={2} sx={{ mt: 2 }}>
              {!hasPaidSession && !wasCanceledAfterPayment && (
                <Button
                  onClick={handleProcessPayment}
                  disabled={processing || !checkoutDraft}
                  variant="contained"
                  sx={styles.primaryButton}
                >
                  Process Payment
                </Button>
              )}
              <Button component={RouterLink} to="/mint" variant="outlined" sx={styles.secondaryButton}>
                {hasPaidSession ? "Return to Mint" : "Back to Mint Form"}
              </Button>
              <Button component={RouterLink} to="/cart" variant="outlined" sx={{ borderColor: colors.neutral, color: colors.neutral, fontWeight: 700 }}>
                Open Cart Workspace
              </Button>
              {paymentSession?.receipt_download_url && (
                <Button href={paymentSession.receipt_download_url} variant="outlined" sx={styles.secondaryButton}>
                  Download Payment Receipt
                </Button>
              )}
              {hasPaidSession && (
                <Button onClick={handleCancelAfterPayment} variant="outlined" sx={{ borderColor: "#FCA5A5", color: "#FCA5A5", fontWeight: 700 }}>
                  Cancel After Payment ($5 Fee)
                </Button>
              )}
            </Stack>
          </Box>
        </Stack>
      </Container>
    </Box>
  );
}
