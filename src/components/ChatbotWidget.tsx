"use client";

import { useState, useRef, useEffect } from "react";
import { MessageCircle, X, Send, ChefHat } from "lucide-react";

const ML_BACKEND_URL =
  process.env.NEXT_PUBLIC_ML_BACKEND_URL || "http://localhost:8000";

interface ChatMessage {
  role: "user" | "bot";
  content: string;
}

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !loading) {
      sendMessage();
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 bg-gradient-to-r from-black to-gray-800 text-yellow-400 hover:from-gray-800 hover:to-black border-2 border-black rounded-full p-4 shadow-xl hover:shadow-2xl transition-all duration-300 z-50 hover:scale-105"
        title="Chat with ChefGPT"
      >
        {isOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <MessageCircle className="h-6 w-6" />
        )}
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-white/95 backdrop-blur-sm border border-black/10 rounded-2xl shadow-2xl flex flex-col z-50">
          {/* Header */}
          <div className="bg-gradient-to-r from-yellow-400 to-yellow-500 border-b border-black/10 p-6 rounded-t-2xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-black/10 rounded-xl">
                  <ChefHat className="h-5 w-5 text-black" />
                </div>
                <div>
                  <h3 className="font-bold text-black text-lg">
                    ChefGPT Assistant
                  </h3>
                  <p className="text-xs text-black/70">
                    AI-powered cooking help
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-black hover:text-gray-700 transition-colors p-1 hover:bg-black/10 rounded-lg"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-yellow-50/50 to-white">
            {messages.length === 0 ? (
              <div className="text-center text-black py-8">
                <div className="p-4 bg-yellow-100 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                  <ChefHat className="h-8 w-8 text-black" />
                </div>
                <h3 className="font-semibold text-black mb-2">
                  Welcome to ChefGPT!
                </h3>
                <p className="text-sm text-black/60">
                  Ask me anything about cooking, recipes, or ingredients.
                </p>
              </div>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl p-4 shadow-sm ${
                      message.role === "user"
                        ? "bg-gradient-to-r from-black to-gray-800 text-yellow-400"
                        : "bg-white text-black border border-black/10 shadow-md"
                    }`}
                  >
                    <div className="markdown-content text-sm leading-relaxed">
                      {message.content}
                    </div>
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white text-black border border-black/10 rounded-2xl p-4 shadow-md">
                  <div className="flex items-center space-x-3">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-black"></div>
                    <span className="text-sm font-medium">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-black/10 p-6 bg-white/80 backdrop-blur-sm rounded-b-2xl">
            <form onSubmit={handleSubmit} className="flex space-x-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about cooking..."
                className="flex-1 px-4 py-3 border-2 border-black/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:border-transparent text-black placeholder-black/50 font-medium"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="bg-gradient-to-r from-black to-gray-800 text-yellow-400 hover:from-gray-800 hover:to-black disabled:bg-gray-400 disabled:text-gray-600 px-4 py-3 rounded-xl border-2 border-black shadow-lg hover:shadow-xl transition-all duration-200 font-semibold"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
