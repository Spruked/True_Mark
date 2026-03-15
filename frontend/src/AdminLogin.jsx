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
import { useLocation, useNavigate } from "react-router-dom";
import { startAdminSession } from "./authStorage";
import { colors, styles } from "./designTokens";

export default function AdminLogin() {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");

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

    if (!form.email || !form.password) {
      setError("Enter admin credentials to continue.");
      return;
    }

    startAdminSession({ email: form.email.trim().toLowerCase() });
    navigate(location.state?.from || "/admin/dashboard");
  };

  return (
    <Box sx={{ minHeight: "100vh", background: colors.background, color: colors.text, py: 8 }}>
      <Container maxWidth="sm">
        <Typography variant="h4" fontWeight={700} gutterBottom sx={styles.title}>
          Admin Login
        </Typography>
        <Typography variant="body1" sx={{ mb: 3, opacity: 0.84 }}>
          Enter the admin portal to review minted records, user activity, pricing data, and the next serial number.
        </Typography>
        {location.state?.from && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Admin sign-in is required before you can access {location.state.from}.
          </Alert>
        )}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <Alert severity="info" sx={{ mb: 3 }}>
          Administrator access to the True Mark operational dashboard.
        </Alert>
        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            <TextField
              label="Admin Email"
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
              Enter Admin Dashboard
            </Button>
          </Stack>
        </form>
      </Container>
    </Box>
  );
}
