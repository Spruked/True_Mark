import React, { useState } from "react";
import {
  Alert,
  Box,
  Button,
  Container,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Link as RouterLink, useLocation, useNavigate } from "react-router-dom";
import { getStoredAccount, startUserSession } from "./authStorage";
import { colors, styles } from "./designTokens";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");
    const redirectTarget = location.state?.from || "/cart";

    if (!form.email || !form.password) {
      setError("Enter your email address and password to continue.");
      return;
    }

    const storedAccount = getStoredAccount();

    if (storedAccount) {
      const normalizedEmail = form.email.trim().toLowerCase();

      if (storedAccount.email !== normalizedEmail || storedAccount.password !== form.password) {
        setError("That email and password do not match the account created in this browser.");
        return;
      }

      startUserSession(storedAccount);
      setSuccess(`Welcome back, ${storedAccount.name}. Your account has been restored for this session.`);
      navigate(redirectTarget);
      return;
    }

    window.sessionStorage.setItem("tm-user-session", JSON.stringify({
      email: form.email.trim().toLowerCase(),
      startedAt: new Date().toISOString(),
    }));
    setSuccess("Signed in for this session. No saved local account was found, so this access is temporary.");
    navigate(redirectTarget);
  };

  return (
    <Box sx={{ minHeight: "100vh", background: colors.background, color: colors.text, py: 8 }}>
      <Container maxWidth="sm">
        <Typography variant="h4" fontWeight={700} gutterBottom sx={styles.title}>
          User Login
        </Typography>
        <Typography variant="body1" sx={{ mb: 3, opacity: 0.84 }}>
          Sign in to manage your mint requests, continue to checkout, and access your account workflow.
        </Typography>
        {location.state?.from && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Sign in is required before you can access {location.state.from}.
          </Alert>
        )}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            <TextField
              label="Email Address"
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
              required
              fullWidth
              InputLabelProps={{ style: { color: "#C8CCD0" } }}
              InputProps={{ style: { color: "#F4F7F8" } }}
            />
            <TextField
              label="Password"
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
              required
              fullWidth
              InputLabelProps={{ style: { color: "#C8CCD0" } }}
              InputProps={{ style: { color: "#F4F7F8" } }}
            />
            <Button type="submit" variant="contained" sx={styles.primaryButton}>
              Sign In
            </Button>
            <Button component={RouterLink} to="/mint" variant="outlined" sx={styles.secondaryButton}>
              Go to Mint
            </Button>
            <Button component={RouterLink} to="/signup" sx={{ color: "#F4F7F8" }}>
              Need an account? Create one here.
            </Button>
            {success && (
              <Button
                onClick={() => navigate("/checkout")}
                variant="outlined"
                sx={styles.secondaryButton}
              >
                Continue to Checkout
              </Button>
            )}
          </Stack>
        </form>
      </Container>
    </Box>
  );
}
