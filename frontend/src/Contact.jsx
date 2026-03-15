import React, { useState } from "react";
import { Box, Typography, TextField, Button, Paper, Divider } from "@mui/material";
import { styles } from "./designTokens";

const Contact = () => {
  const [form, setForm] = useState({
    name: "",
    email: "",
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Connect to backend
    setSubmitted(true);
  };

  return (
    <Box
      sx={{
        position: "relative",
        minHeight: "100vh",
        overflow: "hidden",
        backgroundColor: "#0A0F1F",
        color: "#F4F7F8",
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
      <Box maxWidth={600} mx="auto" my={6} sx={{ position: "relative", zIndex: 2 }}>
        <Paper elevation={3} sx={{ p: { xs: 2, md: 5 } }}>
          <Typography variant="h3" gutterBottom fontWeight={700} align="center">
            Contact
          </Typography>
          <Divider sx={{ mb: 3 }} />
          <Typography paragraph align="center">
            For all general inquiries, please contact us at <a href="mailto:bryan@spruked.com">bryan@spruked.com</a> or use the form below.
          </Typography>
          {submitted ? (
            <Typography color="success.main" mt={3} align="center">
              Thank you for reaching out. We will respond as soon as possible.
            </Typography>
          ) : (
            <Box component="form" onSubmit={handleSubmit} mt={4}>
              <TextField
                label="Name"
                name="name"
                value={form.name}
                onChange={handleChange}
                fullWidth
                margin="normal"
                required
              />
              <TextField
                label="Email"
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                fullWidth
                margin="normal"
                required
              />
              <TextField
                label="Message"
                name="message"
                value={form.message}
                onChange={handleChange}
                fullWidth
                margin="normal"
                multiline
                minRows={4}
                required
              />
              <Button type="submit" variant="contained" sx={{ mt: 2, ...styles.primaryButton }} fullWidth>
                Send Message
              </Button>
            </Box>
          )}
          <Divider sx={{ my: 4 }} />
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 4 }}>
            Pro Prime Series company<br />
            © 2026 Spruked. All rights reserved. Unauthorized copying, reproduction, modification, or distribution of this content or associated materials is strictly prohibited.<br />
            © 2026 Spruked — Official Website of Bryan Spruk. All rights reserved.<br />
            © 2026 Spruked. Unauthorized reproduction or distribution is prohibited.
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
};

export default Contact;
