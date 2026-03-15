

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
- Backend default port: `3301`
- Local frontend API fallback: `http://localhost:3301`
- Recommended public frontend hostname: `true-mark.spruked.com`
- Recommended public API hostname: `api.true-mark.spruked.com`

For a Cloudflare Tunnel deployment, point the frontend hostname to `http://localhost:3300` and the API hostname to `http://localhost:3301`.
Using hyphens in the hostname is recommended over underscores for compatibility.

## Procedures Overview
See [ProceduresOverview.md](ProceduresOverview.md) for a summary of user/admin procedures, security, and compliance.

## User Guide & Manual
- [UserGuide.md](UserGuide.md) (full user guide)
- Downloadable PDF versions coming soon

## Getting Started
1. Install frontend dependencies in `frontend` with `npm install`
2. Install backend dependencies with `pip install -r backend/requirements.txt`
3. Run the FastAPI backend on port `3301`
4. Run the Vite frontend on port `3300`
5. Access the website for user-facing minting and checkout

---

For support, contact: bryan@spruked.com
