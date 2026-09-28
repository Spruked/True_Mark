import React, { useState } from "react";
import axios from "axios";
import { colors } from "./designTokens";
import { getEscalationApiUrl } from "./escalationApi";
import { getUserAuthHeaders } from "./authStorage";

const API_URL = getEscalationApiUrl();

/** Human escalation channel; hidden until a governed case is authorized. */
export default function HumanSupportBubble({ visible = false, caseId = null, reasonCode = "CUSTOMER_REQUESTED_HUMAN" }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  if (!visible) return null;

  const sendMessage = async () => {
    const message = input.trim();
    if (!message || !caseId) return;
    setMessages((current) => [...current, { from: "customer", text: message }]);
    setInput("");
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/${caseId}/messages`, { message, reason_code: reasonCode }, { headers: getUserAuthHeaders() });
      if (response.data?.message) setMessages((current) => [...current, { from: "human", text: response.data.message }]);
    } catch {
      setMessages((current) => [...current, { from: "system", text: "Human Support is temporarily unavailable. Your case remains recorded." }]);
    } finally {
      setLoading(false);
    }
  };

  return <div style={{ position: "fixed", bottom: 24, right: 24, zIndex: 9999 }}>
    {!open && <button aria-label="Open Human Support" onClick={() => setOpen(true)} style={{ background: colors.gold, color: "#111111", border: "none", borderRadius: "50%", width: 56, height: 56, fontSize: 25, boxShadow: "0 2px 12px rgba(0,0,0,0.28)", cursor: "pointer" }}>◉</button>}
    {open && <div style={{ width: 340, background: colors.background, borderRadius: 16, boxShadow: "0 4px 24px rgba(0,0,0,0.3)", overflow: "hidden" }}>
      <div style={{ background: colors.background, color: colors.gold, padding: 16, fontWeight: 700, fontSize: 18, borderBottom: `1px solid ${colors.border}` }}>Human Support <span style={{ display: "block", color: colors.mutedText, fontSize: 11, fontWeight: 400, marginTop: 4 }}>Human-operated escalation channel</span><button aria-label="Close Human Support" onClick={() => setOpen(false)} style={{ float: "right", marginTop: -28, background: "none", border: "none", color: colors.gold, fontSize: 20, cursor: "pointer" }}>×</button></div>
      <div style={{ maxHeight: 320, overflowY: "auto", padding: 16, background: colors.surface, color: colors.text }}>
        {messages.length === 0 && <div style={{ color: colors.mutedText, fontSize: 13 }}>A human agent will see only the context authorized for this escalation case.</div>}
        {messages.map((message, index) => <div key={`${message.from}-${index}`} style={{ marginBottom: 12, textAlign: message.from === "customer" ? "right" : "left" }}><span style={{ display: "inline-block", background: message.from === "customer" ? colors.surfaceSolid : colors.input, color: colors.text, borderRadius: 12, padding: "8px 14px", maxWidth: 240, fontSize: 14, borderLeft: message.from === "human" ? `3px solid ${colors.gold}` : "none" }}>{message.text}</span></div>)}
        {loading && <div style={{ color: colors.goldDark }}>Connecting to Human Support…</div>}
      </div>
      <div style={{ display: "flex", borderTop: `1px solid ${colors.border}`, background: colors.surface }}><input type="text" value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => event.key === "Enter" && sendMessage()} placeholder="Message the human agent…" style={{ flex: 1, border: "none", padding: 12, fontSize: 15, outline: "none", background: colors.surface, color: colors.text }} disabled={loading || !caseId} aria-label="Message Human Support" /><button onClick={sendMessage} disabled={loading || !input.trim() || !caseId} style={{ background: colors.gold, color: "#111111", border: "none", padding: "0 18px", fontWeight: 700, cursor: "pointer" }}>Send</button></div>
    </div>}
  </div>;
}
