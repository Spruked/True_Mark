import { useState } from "react";
import { CheckCircle2, ClipboardCopy, FileJson, LockKeyhole, PackageCheck } from "lucide-react";

const organizedPackage = {
  schema_version: "perpetuum.organizer.v1",
  package_type: "structured_archive",
  source_classes: ["course_study", "family_memory", "media_asset"],
  encryption: "ChaCha20-Poly1305",
  integrity: "SHA-256",
  handoff_status: "LOCAL_ONLY",
};

export function PackageReview() {
  const [copied, setCopied] = useState(false);
  const copyPackage = async () => {
    await navigator.clipboard?.writeText(JSON.stringify(organizedPackage, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };

  return <section className="deck-layout">
    <div className="panel deck-main">
      <div className="section-heading"><div><div className="eyebrow accent">02 / STRUCTURED HANDOFF</div><h3>Package Review</h3></div><span className="status-pill">LOCAL ONLY</span></div>
      <div className="manifest-preview"><div className="manifest-orbit"><FileJson size={42} /><span>JSON</span></div><div><div className="eyebrow">ORGANIZER PACKAGE</div><h4>Structured Archive Payload</h4><p>A clean, predictable package of chapters, timeline entries, media attributes, checksums, and encrypted local references.</p></div></div>
      <div className="fact-grid">{[["SCHEMA", organizedPackage.schema_version], ["CIPHER", organizedPackage.encryption], ["INTEGRITY", organizedPackage.integrity], ["NETWORK", organizedPackage.handoff_status]].map(([label, value]) => <div className="fact" key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
      <div className="action-row"><button className="primary-button" onClick={copyPackage}>{copied ? <CheckCircle2 size={16} /> : <ClipboardCopy size={16} />}{copied ? "COPIED" : "COPY PACKAGE JSON"}</button><button className="secondary-button" disabled><PackageCheck size={16} /> EXPORT PACKAGE</button></div>
    </div>
    <aside className="side-column"><div className="panel checklist"><div className="eyebrow accent">PACKAGE READINESS</div><h3>Review before handoff</h3>{[[<CheckCircle2 />, "Source structure reviewed", true], [<LockKeyhole />, "Payload encrypted locally", true], [<FileJson />, "Manifest schema valid", true], [<PackageCheck />, "External handoff authorized", false]].map(([icon, label, done]) => <div className="check-row" key={String(label)}><span className={done ? "check-icon done" : "check-icon"}>{icon}</span><span>{label}</span><small>{done ? "READY" : "LOCAL"}</small></div>)}</div><div className="panel hash-card"><div className="eyebrow accent">NEXT SYSTEM BOUNDARY</div><p>This repository prepares and organizes the payload. The receiving certificate or records service owns any later issuance workflow.</p></div></aside>
  </section>;
}
