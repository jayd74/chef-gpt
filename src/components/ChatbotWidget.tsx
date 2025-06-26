"use client";

import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send } from "lucide-react";

const ML_BACKEND_URL =
  process.env.NEXT_PUBLIC_ML_BACKEND_URL || "http://localhost:8000";

interface ChatMessage {
  role: "user" | "bot";
  content: string;
}

export default function ChatbotWidget() {
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, open]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMessage: ChatMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(`${ML_BACKEND_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });
      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [
          ...prev,
          {
            role: "bot",
            content: data.response || data.message || "(No response)",
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: "bot",
            content: "Sorry, there was an error with the chat service.",
          },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "Network error. Please try again later." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !loading) {
      sendMessage();
    }
  };

  return (
    <>
      {/* Floating Button */}
      {!open && (
        <button
          className="fixed bottom-6 right-6 z-50 bg-orange-600 hover:bg-orange-700 text-white rounded-full p-4 shadow-lg flex items-center justify-center transition"
          onClick={() => setOpen(true)}
          aria-label="Open chatbot"
        >
          <MessageCircle className="h-7 w-7" />
        </button>
      )}

      {/* Chat Window */}
      {open && (
        <div className="fixed bottom-6 right-6 z-50 w-80 max-w-[95vw] bg-white rounded-xl shadow-2xl flex flex-col border border-orange-200">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b bg-orange-600 rounded-t-xl">
            <div className="flex items-center gap-2 text-white font-semibold">
              <MessageCircle className="h-5 w-5" />
              ChefGPT Chatbot
            </div>
            <button onClick={() => setOpen(false)} aria-label="Close chatbot">
              <X className="h-5 w-5 text-white" />
            </button>
          </div>

          {/* Messages */}
          <div
            className="flex-1 overflow-y-auto px-4 py-3 space-y-3 bg-orange-50"
            style={{ minHeight: 200, maxHeight: 320 }}
          >
            {messages.length === 0 && (
              <div className="text-center text-gray-400 text-sm mt-8">
                Ask me anything about recipes, ingredients, or cooking!
              </div>
            )}
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`px-3 py-2 rounded-lg max-w-[80%] text-sm shadow-sm ${
                    msg.role === "user"
                      ? "bg-orange-600 text-white rounded-br-none"
                      : "bg-white text-gray-800 border border-orange-200 rounded-bl-none"
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="flex items-center gap-2 px-4 py-3 border-t bg-white rounded-b-xl">
            <input
              type="text"
              className="flex-1 px-3 py-2 rounded-full border border-gray-200 outline-none text-sm"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button
              className="bg-orange-600 hover:bg-orange-700 text-white rounded-full p-2 flex items-center justify-center disabled:opacity-50"
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              aria-label="Send message"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
