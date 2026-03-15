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
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { clearAdminSession, getAdminAuthHeaders } from "./authStorage";
import { colors, styles } from "./designTokens";
import { getBackendApiBase } from "./apiBase";

const API_BASE = getBackendApiBase();

function numberValue(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function MetricCard({ label, value, note }) {
  return (
    <Box sx={{ p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
      <Typography variant="overline" sx={{ color: "#C8CCD0" }}>{label}</Typography>
      <Typography variant="h4" fontWeight={700}>{value}</Typography>
      {note && (
        <Typography variant="body2" sx={{ opacity: 0.84, mt: 0.75 }}>
          {note}
        </Typography>
      )}
    </Box>
  );
}

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [downloadingInvoice, setDownloadingInvoice] = useState("");
  const [error, setError] = useState("");
  const [saveMessage, setSaveMessage] = useState("");
  const [records, setRecords] = useState({
    orders: [],
    mints: [],
    accounts: [],
    pricing: null,
    serial: null,
    analytics: null,
    taxTable: null,
    market: null,
  });
  const [editablePricing, setEditablePricing] = useState(null);
  const [editableTaxTable, setEditableTaxTable] = useState(null);
  const [newTaxState, setNewTaxState] = useState("");
  const [newTaxRate, setNewTaxRate] = useState("");

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      setLoading(true);
      setError("");

      try {
        const adminRequestConfig = {
          headers: getAdminAuthHeaders(),
        };

        const [orders, mints, accounts, pricing, serial, analytics, taxTable, market] = await Promise.all([
          axios.get(`${API_BASE}/admin/orders`, adminRequestConfig),
          axios.get(`${API_BASE}/admin/nfts`, adminRequestConfig),
          axios.get(`${API_BASE}/admin/accounts`, adminRequestConfig),
          axios.get(`${API_BASE}/admin/pricing`, adminRequestConfig),
          axios.get(`${API_BASE}/admin/serial`, adminRequestConfig),
          axios.get(`${API_BASE}/admin/analytics`, adminRequestConfig),
          axios.get(`${API_BASE}/admin/tax-table`, adminRequestConfig),
          axios.get(`${API_BASE}/admin/market`, adminRequestConfig),
        ]);

        if (!active) {
          return;
        }

        setRecords({
          orders: orders.data,
          mints: mints.data,
          accounts: accounts.data,
          pricing: pricing.data,
          serial: serial.data,
          analytics: analytics.data,
          taxTable: taxTable.data,
          market: market.data,
        });
        setEditablePricing(pricing.data);
        setEditableTaxTable(taxTable.data);
      } catch (requestError) {
        if (active) {
          if (requestError.response?.status === 401) {
            clearAdminSession();
            navigate("/admin/login", { replace: true, state: { from: "/admin/dashboard" } });
            return;
          }

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
  }, [navigate]);

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

  const updateTaxDefaultRate = (value) => {
    setEditableTaxTable((current) => ({
      ...current,
      default_rate: numberValue(value),
    }));
  };

  const updateTaxNote = (value) => {
    setEditableTaxTable((current) => ({
      ...current,
      notes: value,
    }));
  };

  const updateStateRate = (stateCode, value) => {
    const normalizedState = stateCode.trim().toUpperCase();
    setEditableTaxTable((current) => ({
      ...current,
      state_rates: {
        ...current.state_rates,
        [normalizedState]: numberValue(value),
      },
    }));
  };

  const removeStateRate = (stateCode) => {
    setEditableTaxTable((current) => {
      const nextStateRates = { ...current.state_rates };
      delete nextStateRates[stateCode];
      return {
        ...current,
        state_rates: nextStateRates,
      };
    });
  };

  const addStateRate = () => {
    if (!newTaxState.trim()) {
      return;
    }

    updateStateRate(newTaxState, newTaxRate);
    setNewTaxState("");
    setNewTaxRate("");
  };

  const handleSavePricing = async () => {
    if (!editablePricing) {
      return;
    }

    setSaving(true);
    setSaveMessage("");
    setError("");

    try {
      const response = await axios.put(`${API_BASE}/admin/pricing`, editablePricing, {
        headers: getAdminAuthHeaders(),
      });
      setEditablePricing(response.data);
      setRecords((current) => ({
        ...current,
        pricing: response.data,
      }));
      setSaveMessage("Pricing was saved to the backend configuration.");
    } catch (requestError) {
      if (requestError.response?.status === 401) {
        clearAdminSession();
        navigate("/admin/login", { replace: true, state: { from: "/admin/dashboard" } });
        return;
      }

      setError("Pricing changes could not be saved.");
    } finally {
      setSaving(false);
    }
  };

  const handleSaveTaxTable = async () => {
    if (!editableTaxTable) {
      return;
    }

    setSaving(true);
    setSaveMessage("");
    setError("");

    try {
      const response = await axios.put(`${API_BASE}/admin/tax-table`, editableTaxTable, {
        headers: getAdminAuthHeaders(),
      });
      setEditableTaxTable(response.data);
      setRecords((current) => ({
        ...current,
        taxTable: response.data,
      }));
      setSaveMessage("Tax table saved successfully.");
    } catch (requestError) {
      if (requestError.response?.status === 401) {
        clearAdminSession();
        navigate("/admin/login", { replace: true, state: { from: "/admin/dashboard" } });
        return;
      }

      setError("Tax table changes could not be saved.");
    } finally {
      setSaving(false);
    }
  };

  const handleInvoiceDownload = async (invoiceNumber) => {
    if (!invoiceNumber) {
      return;
    }

    setDownloadingInvoice(invoiceNumber);
    setError("");

    try {
      const response = await axios.get(`${API_BASE}/admin/invoices/${invoiceNumber}/download`, {
        headers: getAdminAuthHeaders(),
        responseType: "blob",
      });
      const blobUrl = window.URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `${invoiceNumber}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (requestError) {
      if (requestError.response?.status === 401) {
        clearAdminSession();
        navigate("/admin/login", { replace: true, state: { from: "/admin/dashboard" } });
        return;
      }

      setError(`Invoice ${invoiceNumber} could not be downloaded right now.`);
    } finally {
      setDownloadingInvoice("");
    }
  };

  const analytics = records.analytics || {};
  const lifetime = analytics.lifetime || {};
  const daily = analytics.daily || {};
  const weekly = analytics.weekly || {};
  const monthly = analytics.monthly || {};
  const marketAssets = records.market?.assets || {};

  return (
    <Box sx={{ minHeight: "100vh", background: colors.background, color: colors.text, py: 8 }}>
      <Container maxWidth="xl">
        <Stack direction={{ xs: "column", md: "row" }} justifyContent="space-between" spacing={2} sx={{ mb: 3 }}>
          <Box>
            <Typography variant="h4" fontWeight={700} sx={styles.title}>
              Admin Dashboard
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.84 }}>
              Pricing, revenue, tax, crypto monitoring, order history, mint registry, and persistent user account management.
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
            gridTemplateColumns: { xs: "1fr", md: "repeat(3, 1fr)", xl: "repeat(6, 1fr)" },
            gap: 2,
            mb: 4,
          }}
        >
          <MetricCard label="Lifetime Revenue" value={`$${Number(lifetime.gross_revenue_usd || 0).toFixed(2)}`} note={`${lifetime.orders_count || 0} total orders`} />
          <MetricCard label="Daily Revenue" value={`$${Number(daily.gross_revenue_usd || 0).toFixed(2)}`} note={`${daily.orders_count || 0} orders in 24h`} />
          <MetricCard label="Weekly Revenue" value={`$${Number(weekly.gross_revenue_usd || 0).toFixed(2)}`} note={`${weekly.orders_count || 0} orders in 7d`} />
          <MetricCard label="Monthly Revenue" value={`$${Number(monthly.gross_revenue_usd || 0).toFixed(2)}`} note={`${monthly.orders_count || 0} orders in 30d`} />
          <MetricCard label="Taxes Collected" value={`$${Number(lifetime.taxes_collected_usd || 0).toFixed(2)}`} note="Lifetime tax estimate" />
          <MetricCard label="Net Revenue" value={`$${Number(lifetime.net_revenue_usd || 0).toFixed(2)}`} note={`Avg order $${Number(lifetime.average_order_usd || 0).toFixed(2)}`} />
        </Box>

        <Stack direction={{ xs: "column", xl: "row" }} spacing={3} alignItems="stretch" sx={{ mb: 4 }}>
          <Box sx={{ flex: 1, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
              Live Crypto Monitor
            </Typography>
            <Stack spacing={2}>
              <Box sx={{ p: 2, borderRadius: 2, background: "rgba(10, 15, 31, 0.55)" }}>
                <Typography fontWeight={700}>Polygon</Typography>
                <Typography variant="h5">${Number(marketAssets.polygon?.usd || 0).toFixed(4)}</Typography>
                <Typography variant="body2" sx={{ color: Number(marketAssets.polygon?.usd_24h_change || 0) >= 0 ? "#7DD3FC" : "#FCA5A5" }}>
                  24h: {Number(marketAssets.polygon?.usd_24h_change || 0).toFixed(2)}%
                </Typography>
              </Box>
              <Box sx={{ p: 2, borderRadius: 2, background: "rgba(10, 15, 31, 0.55)" }}>
                <Typography fontWeight={700}>Ethereum</Typography>
                <Typography variant="h5">${Number(marketAssets.ethereum?.usd || 0).toFixed(2)}</Typography>
                <Typography variant="body2" sx={{ color: Number(marketAssets.ethereum?.usd_24h_change || 0) >= 0 ? "#7DD3FC" : "#FCA5A5" }}>
                  24h: {Number(marketAssets.ethereum?.usd_24h_change || 0).toFixed(2)}%
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ opacity: 0.84 }}>
                Updated: {records.market?.updated_at ? new Date(records.market.updated_at).toLocaleString() : "Not available"}
              </Typography>
            </Stack>
          </Box>

          <Box sx={{ flex: 2, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
              Pricing Controls
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.84, mb: 2 }}>
              Adjust mint pricing, package tiers, storage, and chain surcharges without rewriting code.
            </Typography>

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
        </Stack>

        <Stack direction={{ xs: "column", xl: "row" }} spacing={3} alignItems="stretch" sx={{ mb: 4 }}>
          <Box sx={{ flex: 1, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
              Tax Table
            </Typography>
            {editableTaxTable && (
              <Stack spacing={2}>
                <TextField
                  label="Default Tax Rate"
                  type="number"
                  value={editableTaxTable.default_rate}
                  onChange={(event) => updateTaxDefaultRate(event.target.value)}
                  fullWidth
                  InputLabelProps={{ style: { color: "#C8CCD0" } }}
                  InputProps={{ style: { color: "#F4F7F8" } }}
                />
                <TextField
                  label="Tax Notes"
                  multiline
                  minRows={3}
                  value={editableTaxTable.notes || ""}
                  onChange={(event) => updateTaxNote(event.target.value)}
                  fullWidth
                  InputLabelProps={{ style: { color: "#C8CCD0" } }}
                  InputProps={{ style: { color: "#F4F7F8" } }}
                />
                {Object.entries(editableTaxTable.state_rates || {}).map(([stateCode, rate]) => (
                  <Stack key={stateCode} direction={{ xs: "column", sm: "row" }} spacing={2}>
                    <TextField
                      label="State"
                      value={stateCode}
                      fullWidth
                      InputLabelProps={{ style: { color: "#C8CCD0" } }}
                      InputProps={{ readOnly: true, style: { color: "#F4F7F8" } }}
                    />
                    <TextField
                      label="Rate"
                      type="number"
                      value={rate}
                      onChange={(event) => updateStateRate(stateCode, event.target.value)}
                      fullWidth
                      InputLabelProps={{ style: { color: "#C8CCD0" } }}
                      InputProps={{ style: { color: "#F4F7F8" } }}
                    />
                    <Button variant="outlined" onClick={() => removeStateRate(stateCode)} sx={styles.secondaryButton}>
                      Remove
                    </Button>
                  </Stack>
                ))}
                <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
                  <TextField
                    label="New State"
                    value={newTaxState}
                    onChange={(event) => setNewTaxState(event.target.value.toUpperCase())}
                    fullWidth
                    InputLabelProps={{ style: { color: "#C8CCD0" } }}
                    InputProps={{ style: { color: "#F4F7F8" } }}
                  />
                  <TextField
                    label="New Rate"
                    type="number"
                    value={newTaxRate}
                    onChange={(event) => setNewTaxRate(event.target.value)}
                    fullWidth
                    InputLabelProps={{ style: { color: "#C8CCD0" } }}
                    InputProps={{ style: { color: "#F4F7F8" } }}
                  />
                  <Button variant="outlined" onClick={addStateRate} sx={styles.secondaryButton}>
                    Add State
                  </Button>
                </Stack>
                <Button onClick={handleSaveTaxTable} variant="contained" sx={styles.primaryButton}>
                  Save Tax Table
                </Button>
              </Stack>
            )}
          </Box>

          <Box sx={{ flex: 1.4, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
              Cost Analysis
            </Typography>
            <Stack spacing={1.5}>
              <Typography><b>Gross Revenue:</b> ${Number(lifetime.gross_revenue_usd || 0).toFixed(2)}</Typography>
              <Typography><b>Taxes Collected:</b> ${Number(lifetime.taxes_collected_usd || 0).toFixed(2)}</Typography>
              <Typography><b>Processing Fees:</b> ${Number(lifetime.processing_fees_usd || 0).toFixed(2)}</Typography>
              <Typography><b>Discounts Issued:</b> ${Number(lifetime.discounts_usd || 0).toFixed(2)}</Typography>
              <Typography><b>Net Revenue:</b> ${Number(lifetime.net_revenue_usd || 0).toFixed(2)}</Typography>
              <Typography><b>Average Order Value:</b> ${Number(lifetime.average_order_usd || 0).toFixed(2)}</Typography>
              <Typography><b>Next Serial:</b> {records.serial?.next_serial || "Loading..."}</Typography>
            </Stack>
          </Box>
        </Stack>

        <Stack direction={{ xs: "column", xl: "row" }} spacing={3} alignItems="stretch">
          <Box sx={{ flex: 1.1, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
              Recent Orders
            </Typography>
            {records.orders.length === 0 ? (
              <Typography variant="body2" sx={{ opacity: 0.84 }}>
                No recorded orders yet.
              </Typography>
            ) : (
              <Stack spacing={2}>
                {records.orders.map((order) => (
                  <Box key={order.id} sx={{ p: 2, borderRadius: 2, background: "rgba(10, 15, 31, 0.55)" }}>
                    <Typography fontWeight={700}>{order.serial}</Typography>
                    <Typography variant="body2" sx={{ color: colors.gold }}>
                      {order.nft_identifier || "Identifier pending"}
                    </Typography>
                    <Typography variant="body2">
                      {order.user_name} | {order.nft_type} | {order.chain} | {order.payment_method}
                    </Typography>
                    <Typography variant="body2">
                      {order.type_code || "NFT"} | Node {order.node_id || "TM01"} | Region {order.region_code || "US"} | Registrant {order.registrant_code || "PUBLIC"}
                    </Typography>
                    <Typography variant="body2">
                      Total ${Number(order.total_usd || 0).toFixed(2)} | Tax ${Number(order.tax_amount_usd || 0).toFixed(2)}
                    </Typography>
                    <Typography variant="body2">
                      Payment {order.payment_reference || "N/A"} | Receipt {order.receipt_number || "N/A"} | Status {order.status || "minted"}
                    </Typography>
                    <Typography variant="body2">
                      Invoice {order.invoice_number || "Pending"} | Delivery {order.invoice_email_status || "pending"}
                    </Typography>
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1} sx={{ mt: 1.5 }}>
                      <Button
                        variant="outlined"
                        onClick={() => handleInvoiceDownload(order.invoice_number)}
                        disabled={!order.invoice_number || downloadingInvoice === order.invoice_number}
                        sx={styles.secondaryButton}
                      >
                        {downloadingInvoice === order.invoice_number ? "Preparing Invoice..." : "Download Invoice"}
                      </Button>
                    </Stack>
                    <Typography variant="caption" sx={{ color: "#C8CCD0" }}>
                      {new Date(order.created_at).toLocaleString()}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            )}
          </Box>

          <Box sx={{ flex: 1, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
              Persistent User Accounts
            </Typography>
            {records.accounts.length === 0 ? (
              <Typography variant="body2" sx={{ opacity: 0.84 }}>
                No user accounts saved yet.
              </Typography>
            ) : (
              <Stack spacing={2}>
                {records.accounts.map((account) => (
                  <Box key={account.id} sx={{ p: 2, borderRadius: 2, background: "rgba(10, 15, 31, 0.55)" }}>
                    <Typography fontWeight={700}>{account.name}</Typography>
                    <Typography variant="body2">{account.email}</Typography>
                    <Typography variant="body2">
                      {account.address_line1 || "No address on file"}
                      {account.city || account.state || account.postal_code
                        ? ` | ${[account.city, account.state, account.postal_code].filter(Boolean).join(", ")}`
                        : ""}
                    </Typography>
                    <Typography variant="caption" sx={{ color: "#C8CCD0", display: "block" }}>
                      Phone: {account.phone || "Not provided"} | DOB: {account.dob || "Not provided"}
                    </Typography>
                  </Box>
                ))}
              </Stack>
            )}
          </Box>
        </Stack>

        <Box sx={{ mt: 3, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
          <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
            Mint Registry
          </Typography>
          {records.mints.length === 0 ? (
            <Typography variant="body2" sx={{ opacity: 0.84 }}>
              No mint events recorded yet.
            </Typography>
          ) : (
            <Stack spacing={2}>
              {records.mints.map((mintEvent) => (
                <Box key={mintEvent.id} sx={{ p: 2, borderRadius: 2, background: "rgba(10, 15, 31, 0.55)" }}>
                  <Typography fontWeight={700}>{mintEvent.nft_identifier}</Typography>
                  <Typography variant="body2">
                    Serial {mintEvent.serial} | Invoice {mintEvent.invoice_number || "Pending"} | Payment {mintEvent.payment_reference || "N/A"}
                  </Typography>
                  <Typography variant="body2">
                    {mintEvent.user_name || "Customer"} | {mintEvent.user_email || "No email"} | {mintEvent.nft_type}
                  </Typography>
                  <Typography variant="body2">
                    {mintEvent.type_code || "NFT"} | Node {mintEvent.node_id || "TM01"} | Region {mintEvent.region_code || "US"} | Registrant {mintEvent.registrant_code || "PUBLIC"}
                  </Typography>
                  <Stack direction={{ xs: "column", sm: "row" }} spacing={1} sx={{ mt: 1.5 }}>
                    <Button
                      variant="outlined"
                      onClick={() => handleInvoiceDownload(mintEvent.invoice_number)}
                      disabled={!mintEvent.invoice_number || downloadingInvoice === mintEvent.invoice_number}
                      sx={styles.secondaryButton}
                    >
                      {downloadingInvoice === mintEvent.invoice_number ? "Preparing Invoice..." : "Download Invoice"}
                    </Button>
                  </Stack>
                  <Typography variant="caption" sx={{ color: "#C8CCD0" }}>
                    {new Date(mintEvent.minted_at).toLocaleString()}
                  </Typography>
                </Box>
              ))}
            </Stack>
          )}
        </Box>
      </Container>
    </Box>
  );
}
