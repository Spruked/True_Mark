import React, { useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Container,
  Divider,
  Stack,
  Typography,
} from "@mui/material";
import { colors, styles } from "./designTokens";

const sampleImage = "/assets/CertificateKNFTsample.png";

const demoRecord = {
  owner: "Jane Doe",
  title: "Knowledge Preservation Demonstration Record",
  objectType: "Research Record",
  certificateProfile: "5-Layer Certificate",
  serial: "TM-DEMO-OBJECT-2026-00001",
  institution: "Jane Doe Research Group",
  anchor: "ipfs://QmDemoJaneDoeKnowledgeAnchor2026",
  glyph: "9b04f2fbc11d6e2c4b9a1d7aef5f0d34",
  timestamp: "2026-03-14T11:32:00Z",
  chain: "Polygon Demo Flow",
};

export default function DemoMint() {
  const [showMockup, setShowMockup] = useState(false);

  const printMarkup = useMemo(() => `
    <html>
      <head>
        <title>True Mark Demo Certificate - Jane Doe</title>
        <style>
          body { font-family: Inter, system-ui, sans-serif; margin: 0; padding: 32px; background: #f5f1e8; color: #111; }
          .page { max-width: 960px; margin: 0 auto; border: 1px solid #c9a227; padding: 24px; background: #fffdf7; }
          .header { display: flex; justify-content: space-between; align-items: flex-start; gap: 24px; }
          .meta { flex: 1; }
          .meta h1 { margin: 0 0 8px; font-size: 34px; }
          .meta p { margin: 6px 0; font-size: 15px; line-height: 1.6; }
          .sample { width: 320px; border: 1px solid #d1d5db; }
          .sample img { width: 100%; display: block; }
          .section { margin-top: 28px; padding-top: 20px; border-top: 1px solid #d1d5db; }
          .label { color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
          .value { font-weight: 700; margin-bottom: 10px; }
          .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
          .footer { margin-top: 28px; font-size: 13px; color: #4b5563; }
        </style>
      </head>
      <body>
        <div class="page">
          <div class="header">
            <div class="meta">
              <h1>Demo Certificate Mockup</h1>
          <p>This printable mockup mirrors the intended True Mark object-authentication flow for investor and user demonstration. Digital extensions are optional after certification.</p>
              <div class="section">
                <div class="grid">
                  <div><div class="label">Owner</div><div class="value">${demoRecord.owner}</div></div>
                  <div><div class="label">Object Type</div><div class="value">${demoRecord.objectType}</div></div>
                  <div><div class="label">Asset Title</div><div class="value">${demoRecord.title}</div></div>
                  <div><div class="label">Serial</div><div class="value">${demoRecord.serial}</div></div>
                  <div><div class="label">Institution</div><div class="value">${demoRecord.institution}</div></div>
                  <div><div class="label">Certificate Profile</div><div class="value">${demoRecord.certificateProfile}</div></div>
                  <div><div class="label">Anchor</div><div class="value">${demoRecord.anchor}</div></div>
                  <div><div class="label">Timestamp</div><div class="value">${demoRecord.timestamp}</div></div>
                </div>
              </div>
              <div class="section">
                <div class="label">Glyph Trace</div>
                <div class="value">${demoRecord.glyph}</div>
                <p>The owner prepares an object record, reviews the evidence, authorizes Commit, seals the record, and receives a verifiable Prime Layer Certificate.</p>
              </div>
            </div>
            <div class="sample">
              <img src="${sampleImage}" alt="Demo certificate sample" />
            </div>
          </div>
          <div class="footer">
            True Mark object-authentication demonstration. Sample data only. Not a live certificate issuance.
          </div>
        </div>
      </body>
    </html>
  `, []);

  const handlePrint = () => {
    const printWindow = window.open("", "_blank", "width=1100,height=900");

    if (!printWindow) {
      return;
    }

    printWindow.document.open();
    printWindow.document.write(printMarkup);
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
  };

  return (
    <Box sx={{ minHeight: "100vh", background: colors.background, color: colors.text, py: 8 }}>
      <Container maxWidth="xl">
        <Typography variant="h3" fontWeight={700} gutterBottom sx={styles.title}>
          Demo Object Authentication
        </Typography>
        <Typography variant="body1" sx={{ color: colors.neutral, maxWidth: 900, lineHeight: 1.8 }}>
          This public demo shows the intended True Mark workflow without requiring login: Object → Evidence → Commit → Sealed Record → Prime Layer Certificate → Verify.
        </Typography>

        <Alert severity="info" sx={{ mt: 3, mb: 4 }}>
          This is a visible demonstration flow only. It does not write to the protected record system or issue a live certificate.
        </Alert>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", lg: "1.1fr 0.9fr" },
            gap: 3,
          }}
        >
          <Box sx={{ ...styles.panel, p: 4 }}>
            <Typography variant="h5" fontWeight={700} sx={{ color: colors.gold, mb: 2 }}>
              Object Authentication Demo
            </Typography>
            <Stack spacing={2}>
              <Box>
                <Typography sx={{ color: colors.mutedText, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  Step 1
                </Typography>
                <Typography fontWeight={700}>Account and Submission Context</Typography>
                <Typography sx={{ color: colors.neutral }}>
                  Owner: {demoRecord.owner} | Institution: {demoRecord.institution}
                </Typography>
              </Box>
              <Box>
                <Typography sx={{ color: colors.mutedText, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  Step 2
                </Typography>
                <Typography fontWeight={700}>Asset Preparation</Typography>
                <Typography sx={{ color: colors.neutral }}>
                  {demoRecord.title} is prepared as a {demoRecord.objectType} and routed into the governed evidence workflow.
                </Typography>
              </Box>
              <Box>
                <Typography sx={{ color: colors.mutedText, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  Step 3
                </Typography>
                <Typography fontWeight={700}>Certificate and NFT Face</Typography>
                <Typography sx={{ color: colors.neutral }}>
                  The system produces a certificate image and uses that certificate render as the NFT face for the public object.
                </Typography>
              </Box>
            </Stack>

            <Divider sx={{ my: 3, borderColor: colors.border }} />

            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "1fr", md: "repeat(2, minmax(0, 1fr))" },
                gap: 2,
              }}
            >
              {[
                ["Owner", demoRecord.owner],
                ["Object Type", demoRecord.objectType],
                ["Serial", demoRecord.serial],
                ["Anchor", demoRecord.anchor],
                ["Timestamp", demoRecord.timestamp],
                ["Glyph", demoRecord.glyph],
              ].map(([label, value]) => (
                <Box key={label} sx={{ p: 2, borderRadius: 2, background: colors.input, border: `1px solid ${colors.border}` }}>
                  <Typography sx={{ color: colors.mutedText, fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    {label}
                  </Typography>
                  <Typography sx={{ color: colors.text, fontWeight: 700, wordBreak: "break-word" }}>
                    {value}
                  </Typography>
                </Box>
              ))}
            </Box>

            <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mt: 4 }}>
              <Button variant="contained" sx={styles.primaryButton} onClick={() => setShowMockup(true)}>
                Generate Demo Mockup
              </Button>
              <Button variant="outlined" sx={styles.secondaryButton} onClick={handlePrint}>
                Print Jane Doe Mockup
              </Button>
            </Stack>
          </Box>

          <Box sx={{ ...styles.panel, p: 3 }}>
            <Typography variant="h5" fontWeight={700} sx={{ color: colors.gold, mb: 2 }}>
              Certificate Sample
            </Typography>
            <Box
              component="img"
              src={sampleImage}
              alt="Certificate sample used as NFT face"
              sx={{
                width: "100%",
                display: "block",
                borderRadius: 2,
                border: `1px solid ${colors.border}`,
                boxShadow: "0 18px 40px rgba(0,0,0,0.22)",
              }}
            />
            <Typography variant="body2" sx={{ mt: 2, color: colors.neutral, lineHeight: 1.7 }}>
              This sample certificate represents the sealed-record outcome. The certificate remains independently verifiable, while digital extensions remain optional.
            </Typography>
          </Box>
        </Box>

        {showMockup && (
          <Box sx={{ ...styles.panel, mt: 4, p: 4 }}>
            <Typography variant="h5" fontWeight={700} sx={{ color: colors.gold, mb: 2 }}>
              Printable Certificate Mockup
            </Typography>
            <Box
              sx={{
                display: "grid",
                gridTemplateColumns: { xs: "1fr", lg: "1fr 360px" },
                gap: 3,
              }}
            >
              <Box>
                <Typography variant="h4" fontWeight={700} sx={{ mb: 2 }}>
                  Demo Certificate of Authenticity and Preservation
                </Typography>
                <Typography sx={{ color: colors.neutral, mb: 3 }}>
                  This print mockup is intentionally simple and visible so users and investors can immediately understand the certification outcome.
                </Typography>
                <Stack spacing={1.4}>
                  <Typography><b>Owner:</b> {demoRecord.owner}</Typography>
                  <Typography><b>Asset Title:</b> {demoRecord.title}</Typography>
                  <Typography><b>Object Type:</b> {demoRecord.objectType}</Typography>
                  <Typography><b>Certificate:</b> {demoRecord.certificateProfile}</Typography>
                  <Typography><b>Serial:</b> {demoRecord.serial}</Typography>
                  <Typography><b>Institution:</b> {demoRecord.institution}</Typography>
                  <Typography><b>Anchor:</b> {demoRecord.anchor}</Typography>
                  <Typography><b>Issued:</b> {demoRecord.timestamp}</Typography>
                  <Typography><b>Glyph Trace:</b> {demoRecord.glyph}</Typography>
                </Stack>
              </Box>
              <Box
                component="img"
                src={sampleImage}
                alt="Jane Doe certificate sample"
                sx={{
                  width: "100%",
                  borderRadius: 2,
                  border: `1px solid ${colors.border}`,
                }}
              />
            </Box>
          </Box>
        )}
      </Container>
    </Box>
  );
}
