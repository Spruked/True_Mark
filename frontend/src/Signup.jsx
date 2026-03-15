import React, { useState } from "react";
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Checkbox,
  FormControlLabel,
  Link,
  Alert,
  Stack
} from "@mui/material";
import axios from "axios";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { saveStoredAccount, startUserSession } from "./authStorage";
import { getBackendApiBase } from "./apiBase";
import { colors, styles } from "./designTokens";

const API_BASE = getBackendApiBase();

export default function Signup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    address_line1: "",
    address_line2: "",
    city: "",
    state: "",
    postal_code: "",
    phone: "",
    dob: "",
    agree: false,
    marketing: false
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [createdAccount, setCreatedAccount] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (!form.name || !form.email || !form.password || !form.address_line1 || !form.city || !form.state || !form.postal_code || !form.phone || !form.dob) {
      setError("Name, email, password, address, phone, and date of birth are required.");
      return;
    }
    if (!form.agree) {
      setError("You must agree to the User Agreement and Privacy Policy.");
      return;
    }

    try {
      setSubmitting(true);
      const response = await axios.post(`${API_BASE}/accounts/signup`, {
        name: form.name.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
        address_line1: form.address_line1.trim(),
        address_line2: form.address_line2.trim(),
        city: form.city.trim(),
        state: form.state.trim().toUpperCase(),
        postal_code: form.postal_code.trim(),
        phone: form.phone.trim(),
        dob: form.dob,
        marketing: form.marketing,
      });

      saveStoredAccount(response.data);
      startUserSession(response.data);
      setCreatedAccount(response.data);
      setSuccess(`Account created for ${response.data.email}. Your onboarding details are now stored in the True Mark backend.`);
    } catch (requestError) {
      setError(requestError.response?.data?.detail || "Account creation failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box
      sx={{
        position: "relative",
        minHeight: "100vh",
        overflow: "hidden",
        backgroundColor: colors.background,
        color: colors.text,
        display: "flex",
        alignItems: "center",
        justifyContent: "center"
      }}
    >
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
      <Box sx={{ position: "relative", zIndex: 2, width: "100%" }}>
        <Container maxWidth="xs" sx={{ p: 4, borderRadius: 3, boxShadow: 3, background: colors.surfaceSolid }}>
          <Typography variant="h4" fontWeight={700} gutterBottom sx={styles.title}>
            Create Your Account
          </Typography>
          <Typography variant="body2" sx={{ mb: 2, opacity: 0.8 }}>
            Sign up to mint, manage, and preserve your digital legacy. <b>Josephine</b>, your chat assistant, is always available in the lower right corner to guide you through onboarding, privacy, and platform questions.
          </Typography>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
          <form onSubmit={handleSubmit}>
            <Stack spacing={2}>
              <TextField
                label="Full Name"
                name="name"
                value={form.name}
                onChange={handleChange}
                fullWidth
                required
                autoFocus
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
                label="Password"
                name="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                fullWidth
                required
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />
              <TextField
                label="Address Line 1"
                name="address_line1"
                value={form.address_line1}
                onChange={handleChange}
                fullWidth
                required
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />
              <TextField
                label="Address Line 2"
                name="address_line2"
                value={form.address_line2}
                onChange={handleChange}
                fullWidth
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />
              <TextField
                label="City"
                name="city"
                value={form.city}
                onChange={handleChange}
                fullWidth
                required
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />
              <TextField
                label="State"
                name="state"
                value={form.state}
                onChange={handleChange}
                fullWidth
                required
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />
              <TextField
                label="Postal Code"
                name="postal_code"
                value={form.postal_code}
                onChange={handleChange}
                fullWidth
                required
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />
              <TextField
                label="Telephone"
                name="phone"
                value={form.phone}
                onChange={handleChange}
                fullWidth
                required
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />
              <TextField
                label="Date of Birth"
                name="dob"
                type="date"
                value={form.dob}
                onChange={handleChange}
                fullWidth
                required
                InputLabelProps={{ shrink: true, style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />
              <FormControlLabel
                control={<Checkbox name="marketing" checked={form.marketing} onChange={handleChange} sx={{ color: colors.gold }} />}
                label={<Typography variant="body2">I agree to receive updates and marketing emails (never sold or shared).</Typography>}
              />
              <FormControlLabel
                control={<Checkbox name="agree" checked={form.agree} onChange={handleChange} sx={{ color: colors.gold }} required />}
                label={<Typography variant="body2">I agree to the <Link href="/user-agreement" target="_blank" sx={{ color: colors.gold }}>User Agreement</Link> and <Link href="/privacy-policy" target="_blank" sx={{ color: colors.gold }}>Privacy Policy</Link>.</Typography>}
              />
              <Button type="submit" variant="contained" fullWidth sx={styles.primaryButton} disabled={submitting}>
                {submitting ? "Creating Account..." : "Sign Up"}
              </Button>
              {createdAccount && (
                <>
                  <Alert severity="info">
                    Saved account: <b>{createdAccount.name}</b> ({createdAccount.email})
                  </Alert>
                  <Button
                    type="button"
                    variant="outlined"
                    fullWidth
                    onClick={() => navigate("/mint")}
                    sx={styles.secondaryButton}
                  >
                    Continue to Mint
                  </Button>
                  <Button
                    type="button"
                    component={RouterLink}
                    to="/login"
                    fullWidth
                    sx={{ color: "#F4F7F8" }}
                  >
                    Go to Login
                  </Button>
                </>
              )}
            </Stack>
          </form>
        </Container>
      </Box>
    </Box>
  );
}
