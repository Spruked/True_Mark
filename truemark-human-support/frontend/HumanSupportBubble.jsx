import React, { useState } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_HUMAN_SUPPORT_API || "http://localhost:3300/api/escalations";

export default function HumanSupportBubble({ visible = false, caseId = null }) {
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
      await axios.post(`${API_URL}/${caseId}/messages`, { message });
    } catch {
      setMessages((current) => [...current, { from: "system", text: "Your message could not be queued. The case remains recorded." }]);
    } finally {
      setLoading(false);
    }
  };

  return <div className="human-support-bubble">
    {!open && <button aria-label="Open Human Support" onClick={() => setOpen(true)}>◉</button>}
    {open && <section className="human-support-panel"><header>Human Support <small>Human-operated escalation channel</small><button aria-label="Close Human Support" onClick={() => setOpen(false)}>×</button></header><div className="human-support-messages">{messages.length === 0 && <p>A human agent will see only the context authorized for this escalation case.</p>}{messages.map((item, index) => <div className={item.from === "customer" ? "customer-message" : "agent-message"} key={index}>{item.text}</div>)}{loading && <p>Message queued for a human agent…</p>}</div><footer><input value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => event.key === "Enter" && sendMessage()} placeholder="Message the human agent…" disabled={loading || !caseId} aria-label="Message Human Support" /><button onClick={sendMessage} disabled={loading || !input.trim() || !caseId}>Send</button></footer></section>}
  </div>;
}
