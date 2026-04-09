"use client";

import { FormEvent, useState } from "react";

type ChatMsg = { role: "user" | "assistant"; content: string };

export default function HomePage() {
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    const nextMessages = [...messages, { role: "user" as const, content: text }];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: nextMessages }),
      });
      const data = (await res.json()) as { text: string };
      setMessages((prev) => [...prev, { role: "assistant", content: data.text }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1>Polymarket Research Agent</h1>
      <p className="subtitle">Research markets by chat. Execution requires explicit `CONFIRM BET &lt;id&gt;`.</p>

      <section className="chat">
        {messages.map((m, idx) => (
          <div key={idx} className={`msg ${m.role}`}>
            <strong>{m.role === "user" ? "You" : "Agent"}:</strong> {m.content}
          </div>
        ))}
      </section>

      <form onSubmit={onSubmit} className="composer">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about markets, draft bets, or confirm with: CONFIRM BET <id>"
        />
        <button type="submit" disabled={loading}>{loading ? "Thinking..." : "Send"}</button>
      </form>
    </main>
  );
}
