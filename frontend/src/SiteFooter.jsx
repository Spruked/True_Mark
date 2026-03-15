import React from "react";
import { Box, Container, Stack, Typography } from "@mui/material";
import { Link as RouterLink } from "react-router-dom";
import { primaryLinks, infoLinks, accountLinks } from "./siteLinks";
import { isUserAuthenticated } from "./authStorage";
import { colors } from "./designTokens";

function FooterLink({ to, label }) {
  return (
    <Typography
      component={RouterLink}
      to={to}
      sx={{
        color: colors.mutedText,
        textDecoration: "none",
        fontSize: 14,
        "&:hover": {
          color: colors.gold,
        },
      }}
    >
      {label}
    </Typography>
  );
}

function LinkGroup({ title, links }) {
  return (
    <Box>
      <Typography sx={{ color: colors.gold, fontWeight: 700, mb: 1.5 }}>
        {title}
      </Typography>
      <Stack spacing={1}>
        {links.map((link) => (
          <FooterLink key={link.to} to={link.to} label={link.label} />
        ))}
      </Stack>
    </Box>
  );
}

export default function SiteFooter() {
  const signedInUser = isUserAuthenticated();
  const visiblePrimaryLinks = primaryLinks.filter((link) => !link.requiresUserAuth || signedInUser);
  const visibleInfoLinks = infoLinks.filter((link) => !link.requiresUserAuth || signedInUser);

  return (
    <Box
      component="footer"
      sx={{
        background: "#08101E",
        borderTop: `1px solid ${colors.border}`,
        color: colors.text,
        mt: "auto",
      }}
    >
      <Container sx={{ py: 5 }}>
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "repeat(4, 1fr)" },
            gap: 3,
            alignItems: "start",
          }}
        >
          <Box>
            <Typography sx={{ color: colors.gold, fontWeight: 800, letterSpacing: "0.12em", mb: 1.5 }}>
              TRUE MARK
            </Typography>
            <Typography variant="body2" sx={{ color: colors.mutedText, lineHeight: 1.7 }}>
              True Mark Mint Engine is a forensic-grade vault for certified digital objects,
              legacy records, and institutional knowledge.
            </Typography>
          </Box>
          <LinkGroup title="Explore" links={visiblePrimaryLinks} />
          <LinkGroup title="Information" links={visibleInfoLinks} />
          <LinkGroup title="Access" links={accountLinks} />
        </Box>
      </Container>
    </Box>
  );
}
