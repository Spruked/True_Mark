export const primaryLinks = [
  { label: "Home", to: "/" },
  { label: "Authenticate an Object", to: "/objects/new", requiresUserAuth: true },
  { label: "How It Works", to: "/about" },
  { label: "Certificates", to: "/demo-mint" },
  { label: "Verify", to: "/verify" },
  { label: "Object Types", to: "/use-cases" },
  { label: "Digital Extensions", to: "/investor", requiresUserAuth: true },
];

export const navInfoLinks = [
  { label: "Pricing", to: "/policies" },
  { label: "My Sanctum", to: "/sanctum", requiresUserAuth: true },
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
