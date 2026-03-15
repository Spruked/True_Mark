export const primaryLinks = [
  { label: "Home", to: "/" },
  { label: "About", to: "/about" },
  { label: "Demo Mint", to: "/demo-mint" },
  { label: "Why Now", to: "/why-now" },
  { label: "Use Cases", to: "/use-cases" },
  { label: "Mint", to: "/mint", requiresUserAuth: true },
  { label: "Cart", to: "/cart", requiresUserAuth: true },
  { label: "Checkout", to: "/checkout", requiresUserAuth: true },
];

export const navInfoLinks = [
  { label: "Contact", to: "/contact" },
  { label: "Investor", to: "/investor", requiresUserAuth: true },
];

export const accountLinks = [
  { label: "User Login", to: "/login" },
  { label: "Create Account", to: "/signup" },
  { label: "Admin", to: "/admin/login" },
];

export const infoLinks = [
  { label: "Policies", to: "/policies" },
  { label: "Privacy", to: "/privacy-policy" },
  { label: "User Agreement", to: "/user-agreement" },
  { label: "Contact", to: "/contact" },
  { label: "Investor", to: "/investor", requiresUserAuth: true },
];

export const allNavLinks = [
  ...primaryLinks,
  ...navInfoLinks,
  ...infoLinks,
  ...accountLinks,
];
