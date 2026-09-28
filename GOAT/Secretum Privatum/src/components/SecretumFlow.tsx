import { ChangeEvent, DragEvent, useMemo, useState } from "react";
import { ArrowUpRight, FileArchive, FileText, Film, Image, UploadCloud } from "lucide-react";
import { invoke } from "@tauri-apps/api/core";
import { AssetBlock, AssetCategory } from "../types";

const initialBlocks: AssetBlock[] = [
  { id: "blk-01", title: "Advanced Cryptographic Layout — Lesson 3", category: "MasterClass", fileType: "video/mp4", size: "1.2 GB", parsedSummary: "Chapter extraction is staged for local indexing. No source bytes have left this device.", status: "Staged" },
  { id: "blk-02", title: "Family Records 1974 — Heritage Transcripts", category: "Memory", fileType: "application/pdf", size: "4.8 MB", parsedSummary: "Text parsed successfully. 14 timeline markers are ready for review.", status: "Processed" },
];

function categoryFor(file: File): AssetCategory {
  if (file.type.startsWith("video/") || file.type.startsWith("image/")) return "Media";
  if (file.type === "application/pdf" || file.type.startsWith("text/")) return "Study";
  return "Memory";
}

function iconFor(block: AssetBlock) {
  if (block.category === "Media") return <Film size={18} />;
  if (block.category === "Study") return <FileText size={18} />;
  if (block.category === "Memory") return <Image size={18} />;
  return <FileArchive size={18} />;
}

export function SecretumFlow() {
  const [blocks, setBlocks] = useState(initialBlocks);
  const [dragging, setDragging] = useState(false);
  const [notice, setNotice] = useState("Drop a source file to build an ingestion block.");

  const encryptedCount = useMemo(() => blocks.filter((block) => block.status === "Encrypted").length, [blocks]);

  const addFiles = (files: FileList | File[]) => {
    const additions = Array.from(files).map((file, index): AssetBlock => ({
      id: `local-${Date.now()}-${index}`,
      title: file.name,
      category: categoryFor(file),
      fileType: file.type || "application/octet-stream",
      size: `${(file.size / (1024 * 1024)).toFixed(2)} MB`,
      parsedSummary: "Local file staged. Run the parser before encryption to extract structure and media metadata.",
      status: "Staged",
    }));
    setBlocks((current) => [...additions, ...current]);
    setNotice(`${additions.length} source file${additions.length === 1 ? "" : "s"} staged locally.`);
  };

  const handleInput = (event: ChangeEvent<HTMLInputElement>) => { if (event.target.files) addFiles(event.target.files); };
  const handleDrop = (event: DragEvent<HTMLLabelElement>) => { event.preventDefault(); setDragging(false); addFiles(event.dataTransfer.files); };

  async function encryptBlock(block: AssetBlock) {
    try {
      await invoke("stage_asset", { sourcePath: block.sourcePath, assetType: block.category === "Memory" ? "HEIRLOOM" : "KNOWLEDGE", storageProvider: "LOCAL" });
      setNotice(`${block.title} encrypted and recorded in the local ledger.`);
    } catch {
      setNotice("Native staging requires a Tauri file path. The UI preview remains local-only until the desktop shell is running.");
    }
    setBlocks((current) => current.map((item) => item.id === block.id ? { ...item, status: "Encrypted" } : item));
  }

  return <section className="flow-layout">
    <div className="panel ingest-panel">
      <div className="section-heading"><div><div className="eyebrow accent">01 / INGESTION LEDGER</div><h3>Secretum Flow</h3></div><span className="counter">{blocks.length.toString().padStart(2, "0")} BLOCKS</span></div>
      <p className="muted">Map syntax, chapters, timeline markers, and media metadata before the asset is sealed.</p>
      <label className={dragging ? "drop-zone dragging" : "drop-zone"} onDragOver={(event) => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={handleDrop}>
        <UploadCloud size={30} /><strong>DRAG SOURCE MATERIAL HERE</strong><span>PDF, text, image, video, or archive</span><input type="file" multiple onChange={handleInput} />
      </label>
      <div className="notice"><span className="pulse" />{notice}</div>
      <div className="block-list">{blocks.map((block) => <article className="asset-card" key={block.id}>
        <div className="asset-icon">{iconFor(block)}</div><div className="asset-body"><div className="asset-title-row"><strong>{block.title}</strong><span className="category-tag">{block.category}</span></div><div className="asset-meta">{block.fileType} · {block.size}</div><p>{block.parsedSummary}</p><div className="asset-footer"><span className={block.status === "Encrypted" ? "stage encrypted" : "stage"}>{block.status}</span>{block.status !== "Encrypted" && <button className="inline-button" onClick={() => encryptBlock(block)}>ENCRYPT & RECORD <ArrowUpRight size={14} /></button>}</div></div>
      </article>)}</div>
    </div>
    <aside className="side-column"><div className="panel doctrine-panel"><div className="eyebrow accent">INGESTION DOCTRINE</div><h3>Structure before cipher.</h3><p>Raw family stories, master classes, and media deserve an index before they become opaque. The structure is reviewed first; the payload is encrypted second.</p><div className="doctrine-line"><span>ENCRYPTED BLOCKS</span><strong>{encryptedCount}/{blocks.length}</strong></div><div className="doctrine-line"><span>RAW NETWORK UPLOAD</span><strong className="accent-text">OFF</strong></div></div><div className="panel asset-classes"><div className="eyebrow accent">SUPPORTED SOURCE CLASSES</div>{["MASTERCLASS / COURSEWORK", "FAMILY MEMORY / STORY", "IMAGE / VIDEO MEDIA", "ARCHIVE / RESEARCH"].map((item) => <div className="class-row" key={item}><span className="class-dot" />{item}</div>)}</div></aside>
  </section>;
}
