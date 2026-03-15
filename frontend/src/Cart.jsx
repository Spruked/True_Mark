import React from "react";
import {
  Alert,
  Box,
  Button,
  Container,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import { useMintFlow } from "./context/MintFlowContext";
import { colors, styles } from "./designTokens";

export default function Cart() {
  const { checkoutDraft, workspace, updateWorkspace } = useMintFlow();

  const fileSizeMb = checkoutDraft?.fileSize
    ? (checkoutDraft.fileSize / (1024 * 1024)).toFixed(2)
    : null;

  return (
    <Box sx={{ minHeight: "100vh", background: colors.background, color: colors.text, py: 8 }}>
      <Container maxWidth="lg">
        <Typography variant="h4" fontWeight={700} gutterBottom sx={styles.title}>
          User Cart and Temporary Workspace
        </Typography>
        <Typography variant="body1" sx={{ mb: 3, opacity: 0.84 }}>
          This protected workspace keeps your mint preparation details in a persistent browser folder so you can leave, come back, and keep gathering what you need.
        </Typography>

        <Stack direction={{ xs: "column", lg: "row" }} spacing={3}>
          <Box sx={{ flex: 1, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
              Current Cart Snapshot
            </Typography>
            {checkoutDraft ? (
              <Stack spacing={1.2}>
                <Typography><b>Name:</b> {checkoutDraft.name || "Not set"}</Typography>
                <Typography><b>Email:</b> {checkoutDraft.email || "Not set"}</Typography>
                <Typography><b>NFT Type:</b> {checkoutDraft.nft_type || "Not set"}</Typography>
                <Typography><b>File:</b> {checkoutDraft.file?.name || checkoutDraft.fileName || "No file attached yet"}</Typography>
                <Typography><b>Stored file size:</b> {fileSizeMb ? `${fileSizeMb} MB` : "Not available"}</Typography>
                <Typography><b>Metadata:</b> {checkoutDraft.metadata || "No metadata saved yet"}</Typography>
                {!checkoutDraft.file && checkoutDraft.fileName && (
                  <Alert severity="warning">
                    The file reference was saved, but the actual file must be reattached before final minting after a refresh or return visit.
                  </Alert>
                )}
              </Stack>
            ) : (
              <Alert severity="info">
                Your cart is empty right now. Start in Mint to prepare the protected order.
              </Alert>
            )}

            <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mt: 3 }}>
              <Button component={RouterLink} to="/mint" variant="contained" sx={styles.primaryButton}>
                Go to Mint
              </Button>
              <Button component={RouterLink} to="/checkout" variant="outlined" sx={styles.secondaryButton}>
                Continue to Checkout
              </Button>
            </Stack>
          </Box>

          <Box sx={{ flex: 1, p: 3, borderRadius: 3, background: "rgba(255,255,255,0.05)" }}>
            <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: colors.gold }}>
              Temporary Research Folder
            </Typography>
            <Stack spacing={2}>
              <TextField
                label="Notes"
                multiline
                minRows={5}
                value={workspace.notes}
                onChange={(event) => updateWorkspace({ notes: event.target.value })}
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />
              <TextField
                label="Links and Sources"
                multiline
                minRows={4}
                value={workspace.links}
                onChange={(event) => updateWorkspace({ links: event.target.value })}
                helperText="Paste URLs, document paths, or reminders for materials you still need to gather."
                FormHelperTextProps={{ style: { color: "#C8CCD0" } }}
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />
              <TextField
                label="Checklist"
                multiline
                minRows={4}
                value={workspace.checklist}
                onChange={(event) => updateWorkspace({ checklist: event.target.value })}
                helperText="Keep a simple return-later list for missing files, approvals, or metadata."
                FormHelperTextProps={{ style: { color: "#C8CCD0" } }}
                InputLabelProps={{ style: { color: "#C8CCD0" } }}
                InputProps={{ style: { color: "#F4F7F8" } }}
              />
              <Typography variant="caption" sx={{ color: "#C8CCD0" }}>
                Last saved: {workspace.updatedAt ? new Date(workspace.updatedAt).toLocaleString() : "Not saved yet"}
              </Typography>
            </Stack>
          </Box>
        </Stack>
      </Container>
    </Box>
  );
}
