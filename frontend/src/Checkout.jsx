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
  const { checkoutDraft, clearCheckoutDraft, setCheckoutDraft } = useMintFlow();
  const [pricing, setPricing] = useState(emptyPricing);
  const [quote, setQuote] = useState(null);
  const [nextSerial, setNextSerial] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("fiat");
  const [agree, setAgree] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [completedOrder, setCompletedOrder] = useState(null);
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
        const [pricingResponse, serialResponse] = await Promise.all([
          axios.get(`${API_BASE}/pricing`),
          axios.get(`${API_BASE}/serial/next`),
        ]);

        if (!active) {
          return;
        }

        setPricing(pricingResponse.data);
        setNextSerial(serialResponse.data.next_serial);
      } catch (requestError) {
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
  }, [checkoutDraft]);

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
      } catch (requestError) {
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
      });
    }
  };

  const handleCheckout = async () => {
    if (!checkoutDraft?.file) {
      setError("A live file must be attached before checkout can finish. Return to Mint to reattach the file for this protected order.");
      return;
    }

    if (!agree) {
      setError("You need to confirm the checkout and record policy before minting.");
      return;
    }

    setProcessing(true);
    setError("");
    setSuccess("");
    setCompletedOrder(null);

    try {
      const data = new FormData();
      data.append("name", checkoutDraft.name);
      data.append("email", checkoutDraft.email);
      data.append("nft_type", checkoutDraft.nft_type);
      data.append("file", checkoutDraft.file);
      data.append("metadata", checkoutDraft.metadata || "");
      data.append("package_tier", selections.package_tier);
      data.append("encryption", selections.encryption);
      data.append("chain", selections.chain);
      data.append("quantity", String(selections.quantity));
      data.append("payment_method", paymentMethod);

      const response = await axios.post(`${API_BASE}/mint`, data);
      setCompletedOrder(response.data);
      setSuccess(
        `Checkout complete. Invoice ${response.data.invoice_number} and mint serial ${response.data.serial} are now recorded.`,
      );
      clearCheckoutDraft();
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Checkout could not complete the mint request. Please try again.");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", background: colors.background, color: colors.text, py: 8 }}>
      <Container maxWidth="lg">
        <Typography variant="h4" fontWeight={700} gutterBottom sx={styles.title}>
          Checkout
        </Typography>
        <Typography variant="body1" sx={{ mb: 3, opacity: 0.84 }}>
          Review the mint request, select the package level, and confirm the final quote before submission.
        </Typography>
        <Alert severity="info" sx={{ mb: 3 }}>
          Pricing is set in {pricing.settlement?.display_currency || pricing.currency || "USD"}.
          {` `}
          If crypto is used for payment, it is only quoted as the fiat equivalent at the time of purchase.
          {` `}
          Customers do not connect a wallet. Minting is executed through the platform-managed wallet and Alchemy flow.
        </Alert>

        {!checkoutDraft && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            There is no mint request in progress yet. Start from the mint page first, then return here for checkout.
          </Alert>
        )}

        {(processing || quoteLoading) && <LinearProgress sx={{ mb: 3 }} />}
        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 3 }}>{success}</Alert>}
        {completedOrder && (
          <Alert severity="info" sx={{ mb: 3 }}>
            Invoice delivery: {completedOrder.invoice_email_status}.
            {` `}
            {completedOrder.invoice_email_detail}
          </Alert>
        )}

        <Stack direction={{ xs: "column", xl: "row" }} spacing={3}>
          <Box sx={{ flex: 1, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom>
              Order Summary
            </Typography>
            <Stack spacing={1.5}>
              <Typography><b>Name:</b> {checkoutDraft?.name || "Not provided yet"}</Typography>
              <Typography><b>Email:</b> {checkoutDraft?.email || "Not provided yet"}</Typography>
              <Typography><b>NFT Type:</b> {checkoutDraft?.nft_type || "Not selected yet"}</Typography>
              <Typography><b>File:</b> {checkoutDraft?.file?.name || checkoutDraft?.fileName || "No file attached"}</Typography>
              <Typography><b>Estimated file size:</b> {checkoutDraft ? `${(fileSizeGb * 1024).toFixed(2)} MB` : "N/A"}</Typography>
              <Typography><b>Preview serial:</b> {nextSerial || "Loading..."}</Typography>
              <Typography><b>Metadata:</b> {checkoutDraft?.metadata || "No metadata provided"}</Typography>
              {!checkoutDraft?.file && checkoutDraft?.fileName && (
                <Alert severity="warning">
                  This order was restored from the protected workspace. Reattach the original file in Mint before final checkout.
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
              Live Quote
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
                  Grand Total: ${Number(quote.grand_total ?? quote.total).toFixed(2)}
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
                A live quote will appear here after the backend pricing engine responds.
              </Typography>
            )}

            <FormControl sx={{ mt: 3, mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: colors.gold }}>
                Payment Path
              </Typography>
              <RadioGroup value={paymentMethod} onChange={(event) => setPaymentMethod(event.target.value)}>
                <FormControlLabel value="fiat" control={<Radio sx={{ color: colors.gold }} />} label="Fiat checkout in USD" />
                <FormControlLabel value="crypto" control={<Radio sx={{ color: colors.gold }} />} label="Crypto equivalent quote at time of purchase" />
              </RadioGroup>
            </FormControl>

            {paymentMethod === "crypto" && (
              <Alert severity="info" sx={{ mb: 2 }}>
                The customer still does not connect a wallet here. This option only means the order can be settled against a live crypto equivalent of the USD quote.
              </Alert>
            )}

            <FormControlLabel
              control={<Checkbox checked={agree} onChange={(event) => setAgree(event.target.checked)} sx={{ color: colors.gold }} />}
              label="I confirm the order details, pricing, record policy, and final submission."
            />

            <Stack spacing={2} sx={{ mt: 2 }}>
              <Button
                onClick={handleCheckout}
                disabled={processing || !checkoutDraft}
                variant="contained"
                sx={styles.primaryButton}
              >
                Confirm Checkout
              </Button>
              <Button component={RouterLink} to="/mint" variant="outlined" sx={styles.secondaryButton}>
                Back to Mint Form
              </Button>
              <Button component={RouterLink} to="/cart" variant="outlined" sx={{ borderColor: colors.neutral, color: colors.neutral, fontWeight: 700 }}>
                Open Cart Workspace
              </Button>
              {completedOrder?.vault_download_url && (
                <Button href={completedOrder.vault_download_url} variant="outlined" sx={styles.secondaryButton}>
                  Download Vault Package
                </Button>
              )}
              {completedOrder?.invoice_download_url && (
                <Button href={completedOrder.invoice_download_url} variant="outlined" sx={styles.secondaryButton}>
                  Download Invoice PDF
                </Button>
              )}
            </Stack>
          </Box>
        </Stack>
      </Container>
    </Box>
  );
}
