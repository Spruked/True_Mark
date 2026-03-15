import React, { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Container,
  LinearProgress,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import axios from "axios";
import { Link as RouterLink } from "react-router-dom";
import { colors, styles } from "./designTokens";
import { getBackendApiBase } from "./apiBase";

const API_BASE = getBackendApiBase();

function numberValue(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

export default function AdminDashboard() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saveMessage, setSaveMessage] = useState("");
  const [records, setRecords] = useState({
    nfts: [],
    users: [],
    pricing: null,
    serial: null,
  });
  const [editablePricing, setEditablePricing] = useState(null);

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const [nfts, users, pricing, serial] = await Promise.all([
          axios.get(`${API_BASE}/admin/nfts`),
          axios.get(`${API_BASE}/admin/users`),
          axios.get(`${API_BASE}/admin/pricing`),
          axios.get(`${API_BASE}/admin/serial`),
        ]);

        if (!active) {
          return;
        }

        setRecords({
          nfts: nfts.data,
          users: users.data,
          pricing: pricing.data,
          serial: serial.data,
        });
        setEditablePricing(pricing.data);
      } catch (requestError) {
        if (active) {
          setError("The admin dashboard could not reach the backend right now.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      active = false;
    };
  }, []);

  const updatePriceField = (section, key, field, value) => {
    setEditablePricing((current) => ({
      ...current,
      [section]: {
        ...current[section],
        [key]: {
          ...current[section][key],
          [field]: numberValue(value),
        },
      },
    }));
  };

  const updateTopLevelField = (section, field, value) => {
    setEditablePricing((current) => ({
      ...current,
      [section]: {
        ...current[section],
        [field]: numberValue(value),
      },
    }));
  };

  const handleSavePricing = async () => {
    if (!editablePricing) {
      return;
    }

    setSaving(true);
    setSaveMessage("");
    setError("");

    try {
      const response = await axios.put(`${API_BASE}/admin/pricing`, editablePricing);
      setEditablePricing(response.data);
      setRecords((current) => ({
        ...current,
        pricing: response.data,
      }));
      setSaveMessage("Pricing was saved to the backend configuration and can be changed again anytime.");
    } catch (requestError) {
      setError("Pricing changes could not be saved.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", background: colors.background, color: colors.text, py: 8 }}>
      <Container maxWidth="lg">
        <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" spacing={2} sx={{ mb: 3 }}>
          <Box>
            <Typography variant="h4" fontWeight={700} sx={styles.title}>
              Admin Dashboard
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.84 }}>
              Live overview of minted objects, user submissions, serial progression, and editable pricing.
            </Typography>
          </Box>
          <Button component={RouterLink} to="/mint" variant="outlined" sx={{ alignSelf: "flex-start", ...styles.secondaryButton }}>
            Return to Mint Flow
          </Button>
        </Stack>

        {(loading || saving) && <LinearProgress sx={{ mb: 3 }} />}
        {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
        {saveMessage && <Alert severity="success" sx={{ mb: 3 }}>{saveMessage}</Alert>}

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "repeat(4, 1fr)" },
            gap: 2,
            mb: 4,
          }}
        >
          <Box sx={{ p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="overline" sx={{ color: "#C8CCD0" }}>Minted Records</Typography>
            <Typography variant="h4" fontWeight={700}>{records.nfts.length}</Typography>
          </Box>
          <Box sx={{ p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="overline" sx={{ color: "#C8CCD0" }}>Users Logged</Typography>
            <Typography variant="h4" fontWeight={700}>{records.users.length}</Typography>
          </Box>
          <Box sx={{ p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="overline" sx={{ color: "#C8CCD0" }}>Next Serial</Typography>
            <Typography variant="h5" fontWeight={700}>{records.serial?.next_serial || "Loading..."}</Typography>
          </Box>
          <Box sx={{ p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="overline" sx={{ color: "#C8CCD0" }}>Current Starter Price</Typography>
            <Typography variant="body1" fontWeight={700}>
              ${(records.pricing?.package_tiers?.starter?.price ?? 0).toFixed ? records.pricing?.package_tiers?.starter?.price.toFixed(2) : records.pricing?.package_tiers?.starter?.price ?? 0}
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.84 }}>
              {records.pricing?.settlement?.display_currency ?? "USD"} pricing only
            </Typography>
          </Box>
        </Box>

        <Stack direction={{ xs: "column", xl: "row" }} spacing={3} alignItems="stretch">
          <Box sx={{ flex: 1, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
              Pricing Controls
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.84, mb: 2 }}>
              These values are stored in the backend pricing config, so you can change them later without rewriting code.
            </Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              Customer pricing is fiat-only. Crypto is treated as a live equivalent of the fiat quote, and mint execution is handled through the platform MetaMask account and Alchemy.
            </Alert>

            {editablePricing && (
              <Stack spacing={3}>
                <Box>
                  <Typography fontWeight={700} sx={{ mb: 1 }}>NFT Base Prices</Typography>
                  <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
                    {Object.entries(editablePricing.nft_types).map(([key, value]) => (
                      <TextField
                        key={key}
                        label={key}
                        type="number"
                        value={value.price}
                        onChange={(event) => updatePriceField("nft_types", key, "price", event.target.value)}
                        fullWidth
                        InputLabelProps={{ style: { color: "#C8CCD0" } }}
                        InputProps={{ style: { color: "#F4F7F8" } }}
                      />
                    ))}
                  </Stack>
                </Box>

                <Box>
                  <Typography fontWeight={700} sx={{ mb: 1 }}>Package Tier Prices</Typography>
                  <Stack direction={{ xs: "column", md: "row" }} spacing={2} flexWrap="wrap">
                    {Object.entries(editablePricing.package_tiers).map(([key, value]) => (
                      <TextField
                        key={key}
                        label={`${value.name} (${value.layers} layers)`}
                        type="number"
                        value={value.price}
                        onChange={(event) => updatePriceField("package_tiers", key, "price", event.target.value)}
                        fullWidth
                        InputLabelProps={{ style: { color: "#C8CCD0" } }}
                        InputProps={{ style: { color: "#F4F7F8" } }}
                      />
                    ))}
                  </Stack>
                </Box>

                <Box>
                  <Typography fontWeight={700} sx={{ mb: 1 }}>Encryption and Chain Pricing</Typography>
                  <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
                    <TextField
                      label="ChaCha20 Add-on"
                      type="number"
                      value={editablePricing.encryption_options.chacha20.price}
                      onChange={(event) => updatePriceField("encryption_options", "chacha20", "price", event.target.value)}
                      fullWidth
                      InputLabelProps={{ style: { color: "#C8CCD0" } }}
                      InputProps={{ style: { color: "#F4F7F8" } }}
                    />
                    <TextField
                      label="Polygon Surcharge"
                      type="number"
                      value={editablePricing.chains.polygon.surcharge}
                      onChange={(event) => updatePriceField("chains", "polygon", "surcharge", event.target.value)}
                      fullWidth
                      InputLabelProps={{ style: { color: "#C8CCD0" } }}
                      InputProps={{ style: { color: "#F4F7F8" } }}
                    />
                    <TextField
                      label="Ethereum Surcharge"
                      type="number"
                      value={editablePricing.chains.ethereum.surcharge}
                      onChange={(event) => updatePriceField("chains", "ethereum", "surcharge", event.target.value)}
                      fullWidth
                      InputLabelProps={{ style: { color: "#C8CCD0" } }}
                      InputProps={{ style: { color: "#F4F7F8" } }}
                    />
                  </Stack>
                </Box>

                <Box>
                  <Typography fontWeight={700} sx={{ mb: 1 }}>Storage and Processing</Typography>
                  <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
                    <TextField
                      label="Included GB"
                      type="number"
                      value={editablePricing.storage.included_gb}
                      onChange={(event) => updateTopLevelField("storage", "included_gb", event.target.value)}
                      fullWidth
                      InputLabelProps={{ style: { color: "#C8CCD0" } }}
                      InputProps={{ style: { color: "#F4F7F8" } }}
                    />
                    <TextField
                      label="Additional $/GB"
                      type="number"
                      value={editablePricing.storage.additional_gb_price}
                      onChange={(event) => updateTopLevelField("storage", "additional_gb_price", event.target.value)}
                      fullWidth
                      InputLabelProps={{ style: { color: "#C8CCD0" } }}
                      InputProps={{ style: { color: "#F4F7F8" } }}
                    />
                    <TextField
                      label="Processing Fee %"
                      type="number"
                      value={editablePricing.processing_fee.percentage}
                      onChange={(event) => updateTopLevelField("processing_fee", "percentage", event.target.value)}
                      fullWidth
                      InputLabelProps={{ style: { color: "#C8CCD0" } }}
                      InputProps={{ style: { color: "#F4F7F8" } }}
                    />
                    <TextField
                      label="Processing Fixed"
                      type="number"
                      value={editablePricing.processing_fee.fixed}
                      onChange={(event) => updateTopLevelField("processing_fee", "fixed", event.target.value)}
                      fullWidth
                      InputLabelProps={{ style: { color: "#C8CCD0" } }}
                      InputProps={{ style: { color: "#F4F7F8" } }}
                    />
                  </Stack>
                </Box>

                <Button onClick={handleSavePricing} variant="contained" sx={styles.primaryButton}>
                  Save Pricing Changes
                </Button>
              </Stack>
            )}
          </Box>

          <Box sx={{ flex: 1, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
              Mint Log
            </Typography>
            {records.nfts.length === 0 ? (
              <Typography variant="body2" sx={{ opacity: 0.84 }}>
                No minted records yet. Submit a mint request to populate this dashboard.
              </Typography>
            ) : (
              <Stack spacing={2}>
                {records.nfts.map((record) => (
                  <Box key={record.serial} sx={{ p: 2, borderRadius: 2, background: "rgba(10, 15, 31, 0.55)" }}>
                    <Typography fontWeight={700}>{record.serial}</Typography>
                    <Typography variant="body2">
                      {record.nft_type} | {record.package_tier} | {record.chain}
                    </Typography>
                    <Typography variant="caption" sx={{ color: "#C8CCD0" }}>
                      Glyph: {record.glyph}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            )}

            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: colors.gold, mt: 4 }}>
              User Activity
            </Typography>
            {records.users.length === 0 ? (
              <Typography variant="body2" sx={{ opacity: 0.84 }}>
                No user submissions logged yet.
              </Typography>
            ) : (
              <Stack spacing={2}>
                {records.users.map((user, index) => (
                  <Box key={`${user.email}-${index}`} sx={{ p: 2, borderRadius: 2, background: "rgba(10, 15, 31, 0.55)" }}>
                    <Typography fontWeight={700}>{user.name}</Typography>
                    <Typography variant="body2">{user.email}</Typography>
                    <Typography variant="caption" sx={{ color: "#C8CCD0" }}>
                      Linked serial: {user.serial}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            )}
          </Box>
        </Stack>
      </Container>
    </Box>
  );
}
