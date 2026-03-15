

# True Mark Mint Engine

**Brand:** True Mark Mint Engine  
**Style:** Elegant, secure, institutional, and legacy-focused  
**Assistant:** Josephine — Your Trusted Chat Bubble Guide

---

## System Summary & Outline

- **Purpose:** Forensic-grade, institutional digital object minting and certification (not a public NFT marketplace).
- **Core Components:**
  - Smart contracts (ERC-721/ERC-1155, EIP-2981)
  - Python/FastAPI backend
  - React frontend (with Josephine, the branded chat bubble assistant)
  - Admin dashboard & persistent NFT vault
  - Off-chain storage (IPFS/Arweave/local)
  - Optional encryption (ChaCha20-Poly1305)
  - Forensic certificate generation (PDF)
- **Supported NFT Types:**
  - K-NFT (Knowledge)
  - H-NFT (Heirloom)
  - L-NFT (Legacy)
  - C-NFT (Custom)

## Features
- Mint K-NFTs (Knowledge NFTs), H-NFTs (Heirloom), L-NFTs (Legacy), and C-NFTs (Custom)
- Saleable, licenseable, inheritable NFTs
- 1.5% royalty for minter on sales, 3% on licensing
- Off-chain storage (IPFS/Arweave/local)
- Optional ChaCha20-Poly1305 encryption
- Forensic-grade, printable certificates
- Dynamic pricing based on storage, certificate, and encryption
- Polygon as default chain, Ethereum as upgrade/enterprise
- Seamless checkout: pay in crypto (auto-quoted to USD) or fiat (no wallet required)
- Admin wallet for minting and management
- Extensible for future NFT types and payment methods
- **Josephine Chat Assistant:** Always available in the lower right corner to guide users and admins, answer questions, and provide real-time support.

## Privacy & Security
- All personal information is used solely for account management and platform communications.
- No data is ever sold, shared, or disclosed to third parties.
- All files uploaded for minting are purged after download; only account info is retained for communications and marketing.
- NFT records are permanently logged with a glyph trace and stored in a secure vault for audit and accounting (no personal data included).
- All data is encrypted in transit and at rest.
- All sales are final except for technical errors.

## Tech Stack
- Solidity (ERC-721/ERC-1155, EIP-2981)
- Python/FastAPI backend
- React frontend
- Stripe & Coinbase Commerce for payments
- CoinGecko/CoinMarketCap API for rates
- PDF generation for certificates

## WSL And Tunnel Ports
- Frontend default port: `3300`
- Backend default port: `13000`
- Josephine chat assistant default port: `3301`
- Local frontend API fallback: `http://localhost:13000`
- Local Josephine API fallback: `http://localhost:3301/chat`
- Active public frontend hostname: `true_mark.spruked.com`
- Recommended public API hostname: `truemark-api.spruked.com`
- Active public Josephine hostname: `truemark-chat-assistant.spruked.com`

For the current Cloudflare Tunnel deployment, use these mappings:
- `true_mark.spruked.com` -> `http://localhost:3300`
- `truemark-api.spruked.com` -> `http://localhost:13000`
- `truemark-chat-assistant.spruked.com` -> `http://localhost:3301`

Do not use `http://3300` or `http://3301` by themselves in Cloudflare. Those service URLs need the `localhost` host included.
Hyphenated hostnames are still preferred for long-term compatibility, but the app now supports the underscore hostname you are using.

## Procedures Overview
See [ProceduresOverview.md](ProceduresOverview.md) for a summary of user/admin procedures, security, and compliance.

## User Guide & Manual
- [UserGuide.md](UserGuide.md) (full user guide)
- Downloadable PDF versions coming soon

## Getting Started
1. Install frontend dependencies in `frontend` with `npm install`
2. Install backend dependencies with `pip install -r backend/requirements.txt`
3. Create `backend/.env` from `backend/.env.example` and set the admin email, admin password, and session secret
4. Run the FastAPI backend on port `13000`
5. Run the Josephine assistant API on port `3301`
6. Run the Vite frontend on port `3300`
7. Access the website for user-facing minting and checkout

---

For support, contact: bryan@spruked.com
