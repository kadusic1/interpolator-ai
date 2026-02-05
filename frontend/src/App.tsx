import { useState, useRef, useEffect } from "react";
import Header from "./components/Header";
import InputBar from "./components/InputBar";
import MessageBubble from "./components/MessageBubble";
import type { AgentQuery, Message } from "./types";
import { Bot } from "lucide-react";

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleClear = () => {
    setMessages([]);
  };

  const handleSend = async (query: AgentQuery) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: query.user_input,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(query),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();

      // The backend returns either a list of interpolation responses OR a string message
      // We need to handle both cases safely.
      // Based on API signature: Union[List[InterpolationResponseWithMetadata], str]

      const aiContent = data;

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: aiContent,
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content:
          "I'm sorry, I encountered an error communicating with the server. Please ensure the backend is running.",
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#f0f4f9]">
      <Header onClear={handleClear} />

      <main className="flex-1 overflow-y-auto pt-16 pb-32">
        <div className="max-w-4xl mx-auto w-full">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[60vh] text-center px-4 animate-in fade-in zoom-in-95 duration-500">
              <div className="w-16 h-16 bg-white rounded-2xl shadow-sm flex items-center justify-center mb-6">
                <Bot size={32} className="text-primary" />
              </div>
              <h1 className="text-2xl md:text-3xl font-medium text-gray-800 mb-2">
                How can I help you calculate today?
              </h1>
              <p className="text-gray-500 max-w-md">
                I can interpolate data points using Lagrange, Newton, or Direct
                methods. Just type your points like{" "}
                <code className="bg-white px-1.5 py-0.5 rounded border border-gray-200 text-sm font-mono">
                  (1,2), (3,4)
                </code>
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-2 py-6">
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}

              {/* Loading Indicator */}
              {isLoading && (
                <div className="flex w-full gap-4 p-4 md:px-8">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center animate-pulse">
                    <Bot size={18} />
                  </div>
                  <div className="flex items-center">
                    <div className="flex space-x-1.5 bg-transparent px-0 py-2">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </main>

      <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-[#f0f4f9] via-[#f0f4f9] to-transparent pt-10 z-10">
        <InputBar onSend={handleSend} isLoading={isLoading} />
      </div>
    </div>
  );
}

export default App;
