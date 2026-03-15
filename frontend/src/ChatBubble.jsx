import React, { useState } from "react";
import axios from "axios";
import { colors } from "./designTokens";
import { getAssistantApiUrl } from "./assistantApi";

const API_URL = getAssistantApiUrl();

export default function ChatBubble() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { from: "josephine", text: "Hi, I'm Josephine. How can I help you today?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setMessages([...messages, { from: "user", text: input }]);
    setLoading(true);
    try {
      const res = await axios.post(API_URL, { message: input });
      setMessages((msgs) => [...msgs, { from: "josephine", text: res.data.response }]);
    } catch (e) {
      setMessages((msgs) => [...msgs, { from: "josephine", text: "Sorry, I couldn't reach the assistant." }]);
    }
    setInput("");
    setLoading(false);
  };

  return (
    <div style={{ position: "fixed", bottom: 24, right: 24, zIndex: 9999 }}>
      {!open && (
        <button
          aria-label="Open Josephine Chat"
          style={{
            background: colors.gold,
            color: "#111111",
            border: "none",
            borderRadius: "50%",
            width: 56,
            height: 56,
            fontSize: 32,
            boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
            cursor: "pointer"
          }}
          onClick={() => setOpen(true)}
        >
          💬
        </button>
      )}
      {open && (
        <div style={{
          width: 340,
          background: colors.background,
          borderRadius: 16,
          boxShadow: "0 4px 24px rgba(0,0,0,0.18)",
          padding: 0,
          overflow: "hidden"
        }}>
          <div style={{ background: colors.background, color: colors.gold, padding: 16, fontWeight: 700, fontSize: 18, borderBottom: `1px solid ${colors.border}` }}>
            Josephine
            <button
              aria-label="Close Josephine Chat"
              style={{ float: "right", background: "none", border: "none", color: colors.gold, fontSize: 20, cursor: "pointer" }}
              onClick={() => setOpen(false)}
            >×</button>
          </div>
          <div style={{ maxHeight: 320, overflowY: "auto", padding: 16, background: colors.surface, color: colors.text }}>
            {messages.map((msg, i) => (
              <div key={i} style={{
                marginBottom: 12,
                textAlign: msg.from === "user" ? "right" : "left"
              }}>
                <span style={{
                  display: "inline-block",
                  background: msg.from === "user" ? colors.surfaceSolid : colors.input,
                  color: colors.text,
                  borderRadius: 12,
                  padding: "8px 14px",
                  maxWidth: 220,
                  fontSize: 15,
                  borderLeft: msg.from === "josephine" ? `3px solid ${colors.gold}` : "none",
                  boxShadow: "0 1px 4px rgba(0,0,0,0.16)"
                }}>{msg.text}</span>
              </div>
            ))}
            {loading && <div style={{ color: colors.goldDark }}>Josephine is typing…</div>}
          </div>
          <div style={{ display: "flex", borderTop: `1px solid ${colors.border}`, background: colors.surface }}>
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && sendMessage()}
              placeholder="Type your question…"
              style={{ flex: 1, border: "none", padding: 12, fontSize: 15, outline: "none", background: colors.surface, color: colors.text }}
              disabled={loading}
              aria-label="Type your question to Josephine"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              style={{ background: colors.gold, color: "#111111", border: "none", padding: "0 18px", fontWeight: 700, fontSize: 15, cursor: "pointer", borderRadius: 0 }}
              aria-label="Send message to Josephine"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
