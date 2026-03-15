import React from "react";
import { Container, Typography, Box, Button } from "@mui/material";

export default function App() {
  return (
    <Container maxWidth="md" sx={{ py: 8 }}>
      <Box textAlign="center" mb={6}>
        <Typography variant="h2" fontWeight={700} gutterBottom>
          True Mark Mint Engine
        </Typography>
        <Typography variant="h5" color="text.secondary" gutterBottom>
          Mint Knowledge, Heirloom, Legacy, and Custom NFTs with forensic-grade certificates and seamless checkout.
        </Typography>
        <Button variant="contained" size="large" sx={{ mt: 4 }}>
          Get Started
        </Button>
      </Box>
      {/* NFT minting UI, certificate options, and checkout will go here */}
    </Container>
  );
}
