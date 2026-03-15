import React, { useState } from "react";
import {
  AppBar,
  Box,
  Button,
  Drawer,
  List,
  ListItemButton,
  ListItemText,
  Stack,
  Toolbar,
  Typography,
} from "@mui/material";
import { Link as RouterLink, useLocation, useNavigate } from "react-router-dom";
import { accountLinks, allNavLinks, navInfoLinks, primaryLinks } from "./siteLinks";
import { clearAdminSession, clearUserSession, getActiveUser, isAdminAuthenticated, isUserAuthenticated } from "./authStorage";
import tmLogo from "../assets/TMlogotrans512 - Copy.png";
import { colors, styles } from "./designTokens";

function isRouteActive(pathname, to) {
  if (to === "/") {
    return pathname === "/";
  }

  if (to === "/admin/login") {
    return pathname.startsWith("/admin");
  }

  return pathname === to;
}

export default function SiteNav() {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const signedInUser = isUserAuthenticated();
  const signedInAdmin = isAdminAuthenticated();
  const activeUser = getActiveUser();
  const visiblePrimaryLinks = primaryLinks.filter((link) => !link.requiresUserAuth || signedInUser);
  const visibleInfoLinks = navInfoLinks.filter((link) => !link.requiresUserAuth || signedInUser);
  const visibleDrawerLinks = allNavLinks.filter((link) => !link.requiresUserAuth || signedInUser);

  const linkStyles = (to) => ({
    color: isRouteActive(location.pathname, to) ? colors.gold : colors.text,
    backgroundColor: "transparent",
    fontWeight: 700,
    borderRadius: 0,
    px: 1.25,
    borderBottom: isRouteActive(location.pathname, to) ? `2px solid ${colors.gold}` : "2px solid transparent",
  });

  const handleSignOut = () => {
    clearUserSession();
    clearAdminSession();
    navigate("/");
  };

  return (
    <>
      <AppBar
        position="sticky"
        elevation={0}
        sx={{
          background: "rgba(11, 18, 32, 0.94)",
          borderBottom: `1px solid ${colors.border}`,
          backdropFilter: "blur(12px)",
        }}
      >
        <Toolbar sx={{ minHeight: 76, gap: 2 }}>
          <Box
            component={RouterLink}
            to="/"
            sx={{
              textDecoration: "none",
              flexGrow: { xs: 1, lg: 0 },
              display: "inline-flex",
              alignItems: "center",
            }}
          >
            <Box
              component="img"
              src={tmLogo}
              alt="True Mark TM logo"
              sx={{
                height: { xs: 56, md: 72 },
                width: "auto",
                display: "block",
              }}
            />
          </Box>

          {activeUser?.name && (
            <Typography sx={{ ...styles.mutedLabel, display: { xs: "none", lg: "block" } }}>
              Signed in as {activeUser.name}
            </Typography>
          )}

          <Stack
            direction="row"
            spacing={1}
            sx={{
              display: { xs: "none", xl: "flex" },
              flexGrow: 1,
              flexWrap: "wrap",
              rowGap: 1,
            }}
          >
            {[...visiblePrimaryLinks, ...visibleInfoLinks].map((link) => (
              <Button key={link.to} component={RouterLink} to={link.to} sx={linkStyles(link.to)}>
                {link.label}
              </Button>
            ))}
          </Stack>

          <Stack direction="row" spacing={1} sx={{ display: { xs: "none", lg: "flex" } }}>
            {accountLinks.map((link) => (
              <Button
                key={link.to}
                component={RouterLink}
                to={link.to}
                variant={link.to === "/admin/login" ? "outlined" : "text"}
                sx={{
                  ...linkStyles(link.to),
                  borderColor: link.to === "/admin/login" ? colors.gold : "transparent",
                }}
              >
                {link.label}
              </Button>
            ))}
            {(signedInUser || signedInAdmin) && (
              <Button
                onClick={handleSignOut}
                variant="outlined"
                sx={styles.utilityButton}
              >
                Sign Out
              </Button>
            )}
          </Stack>

          <Button
            onClick={() => setOpen(true)}
            variant="outlined"
            sx={styles.utilityButton}
          >
            Menu
          </Button>
        </Toolbar>
      </AppBar>

      <Drawer anchor="right" open={open} onClose={() => setOpen(false)}>
        <Box sx={{ width: 320, minHeight: "100%", background: colors.background, color: colors.text, pt: 2 }}>
          <Typography sx={{ px: 3, pb: 2, color: colors.gold, fontWeight: 800, letterSpacing: "0.12em" }}>
            TRUE MARK NAVIGATION
          </Typography>
          <List>
            {visibleDrawerLinks.map((link) => (
              <ListItemButton
                key={link.to}
                component={RouterLink}
                to={link.to}
                onClick={() => setOpen(false)}
                sx={{
                  color: colors.text,
                  backgroundColor: isRouteActive(location.pathname, link.to) ? "rgba(201, 162, 39, 0.10)" : "transparent",
                  borderLeft: isRouteActive(location.pathname, link.to) ? `3px solid ${colors.gold}` : "3px solid transparent",
                }}
              >
                <ListItemText primary={link.label} />
              </ListItemButton>
            ))}
            {(signedInUser || signedInAdmin) && (
              <ListItemButton onClick={() => { setOpen(false); handleSignOut(); }} sx={{ color: colors.text }}>
                <ListItemText primary="Sign Out" />
              </ListItemButton>
            )}
          </List>
        </Box>
      </Drawer>
    </>
  );
}
