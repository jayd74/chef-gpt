"use client";

import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send } from "lucide-react";
import ReactMarkdown from "react-markdown";

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
        body: JSON.stringify({
          type: "human",
          content: input,
          session_id: "default",
        }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      // Handle streaming response
      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let botMessage = "";
      let isFirstMessage = true;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6)); // Remove 'data: ' prefix

                if (data.type === "human" && isFirstMessage) {
                  // Skip the initial human message echo
                  isFirstMessage = false;
                  continue;
                }

                if (data.type === "ai") {
                  // Add or update bot message
                  botMessage = data.content;
                  setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (lastMessage && lastMessage.role === "bot") {
                      lastMessage.content = botMessage;
                    } else {
                      newMessages.push({ role: "bot", content: botMessage });
                    }
                    return newMessages;
                  });
                }

                if (data.type === "token") {
                  // Stream individual tokens
                  botMessage += data.content;
                  setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastMessage = newMessages[newMessages.length - 1];
                    if (lastMessage && lastMessage.role === "bot") {
                      lastMessage.content = botMessage;
                    } else {
                      newMessages.push({ role: "bot", content: botMessage });
                    }
                    return newMessages;
                  });
                }

                if (data.type === "end") {
                  // Stream ended
                  break;
                }

                if (data.type === "error") {
                  throw new Error(data.content);
                }
              } catch (parseError) {
                console.error("Error parsing SSE data:", parseError);
              }
            }
          }
        }
      }
    } catch (err) {
      console.log({ err });
      console.error("Chat error:", err);
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
        <div className="fixed bottom-6 right-6 z-50 w-96 max-w-[95vw] bg-white rounded-xl shadow-2xl flex flex-col border border-orange-200 h-[500px]">
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
            style={{ minHeight: 250, maxHeight: 400 }}
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
                  {msg.role === "user" ? (
                    msg.content
                  ) : (
                    <div className="markdown-content">
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => (
                            <p className="mb-2 last:mb-0">{children}</p>
                          ),
                          code: ({ children }) => (
                            <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono">
                              {children}
                            </code>
                          ),
                          pre: ({ children }) => (
                            <pre className="bg-gray-100 p-2 rounded text-xs font-mono overflow-x-auto mb-2">
                              {children}
                            </pre>
                          ),
                          ul: ({ children }) => (
                            <ul className="list-disc list-inside mb-2 space-y-1">
                              {children}
                            </ul>
                          ),
                          ol: ({ children }) => (
                            <ol className="list-decimal list-inside mb-2 space-y-1">
                              {children}
                            </ol>
                          ),
                          li: ({ children }) => (
                            <li className="text-sm">{children}</li>
                          ),
                          strong: ({ children }) => (
                            <strong className="font-semibold">
                              {children}
                            </strong>
                          ),
                          em: ({ children }) => (
                            <em className="italic">{children}</em>
                          ),
                          h1: ({ children }) => (
                            <h1 className="text-lg font-bold mb-2">
                              {children}
                            </h1>
                          ),
                          h2: ({ children }) => (
                            <h2 className="text-base font-bold mb-2">
                              {children}
                            </h2>
                          ),
                          h3: ({ children }) => (
                            <h3 className="text-sm font-bold mb-1">
                              {children}
                            </h3>
                          ),
                          blockquote: ({ children }) => (
                            <blockquote className="border-l-4 border-orange-300 pl-3 italic text-gray-600 mb-2">
                              {children}
                            </blockquote>
                          ),
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  )}
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
