import { useState } from "react";
import { KeyRound, LockKeyhole, ShieldCheck, Vault } from "lucide-react";
import { PackageReview } from "./components/PackageReview";
import { PerpetuumFlow } from "./components/PerpetuumFlow";

const navItems = ["Perpetuum Flow", "Package Review", "Local Ledger"];

export default function App() {
  const [activeTab, setActiveTab] = useState("Perpetuum Flow");

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark"><Vault size={20} /></div>
          <div>
          <div className="eyebrow">PERPETUUM / LOCAL ORGANIZER</div>
            <h1>PERPETUUM</h1>
          </div>
        </div>
        <div className="security-badge"><ShieldCheck size={15} /> LOCAL-FIRST / ENCRYPTION READY</div>
      </header>

      <section className="hero-grid">
        <div>
          <div className="eyebrow accent">H-NFT + K-NFT ARCHIVE WORKSPACE</div>
          <h2>Turn living knowledge into a guarded digital heirloom.</h2>
          <p className="hero-copy">Ingest source material locally. Build structure before encryption. Keep the cleartext on-device until you explicitly choose how to custody the finished record.</p>
        </div>
        <div className="hero-stats">
          <div><span className="stat-value">0</span><span className="stat-label">NETWORK DISPATCHES</span></div>
          <div><span className="stat-value">AES?</span><span className="stat-label">NO — CHACHA20-POLY1305</span></div>
          <div><span className="stat-value">SQL</span><span className="stat-label">LOCAL LEDGER</span></div>
        </div>
      </section>

      <nav className="tabs" aria-label="Workspace sections">
        {navItems.map((item) => <button className={activeTab === item ? "tab active" : "tab"} key={item} onClick={() => setActiveTab(item)}>{item}</button>)}
      </nav>

      {activeTab === "Perpetuum Flow" && <PerpetuumFlow />}
      {activeTab === "Package Review" && <PackageReview />}
      {activeTab === "Local Ledger" && (
        <section className="panel ledger-panel">
          <div className="section-heading"><div><div className="eyebrow accent">PERSISTENT LOCAL STATE</div><h3>Perpetuum Ledger</h3></div><KeyRound size={22} /></div>
          <p>The SQLite ledger is created in the Tauri application data directory. It records asset identity, local encrypted path, content-addressed hash, nonce, and eventual storage reference. Encryption keys are never written to this database.</p>
          <div className="ledger-row"><LockKeyhole size={18} /><span>Ledger initialization occurs on first native staging operation.</span><span className="status-pill">READY</span></div>
        </section>
      )}

      <footer><span>PERPETUUM ORGANIZER / GOAT ISOLATED REPOSITORY</span><span>THE ORGANIZED PACKAGE STAYS LOCAL UNTIL YOU EXPORT IT.</span></footer>
    </main>
  );
}
