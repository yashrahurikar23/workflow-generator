import { Bot, MessageCircle, Send, User } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";
import { API_ENDPOINTS, apiGet, apiPost } from "../config/api";

interface Message {
  message_id: string;
  thread_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  metadata: any;
  created_at: string;
  tokens_used?: number;
  response_time_ms?: number;
  model_used?: string;
}

interface Thread {
  thread_id: string;
  title?: string;
  status: string;
  created_at: string;
  updated_at: string;
  last_activity: string;
  message_count: number;
}

interface ChatPanelProps {
  className?: string;
}

export function ChatPanel({ className = "" }: ChatPanelProps) {
  const [currentThread, setCurrentThread] = useState<Thread | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Create a new thread when component mounts
    createNewThread();
  }, []);

  const createNewThread = async () => {
    try {
      const response = await apiPost(API_ENDPOINTS.chatThreads, {
        title: "Workflow Assistant Chat",
        metadata: { created_from: "ui" },
      });

      if (response.ok) {
        const thread = await response.json();
        setCurrentThread(thread);
        setMessages([]);
        setError(null);
      } else {
        setError("Failed to create chat thread");
      }
    } catch (err) {
      setError("Failed to connect to chat service");
      console.error("Error creating thread:", err);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentThread || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setIsLoading(true);
    setError(null);

    // Add user message to UI immediately
    const tempUserMessage: Message = {
      message_id: `temp-${Date.now()}`,
      thread_id: currentThread.thread_id,
      role: "user",
      content: userMessage,
      metadata: {},
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);

    try {
      const response = await apiPost(
        API_ENDPOINTS.chatInThread(currentThread.thread_id),
        {
          message_content: userMessage,
          use_context: true,
        }
      );

      if (response.ok) {
        const chatResponse = await response.json();
        const assistantMessage = chatResponse.message;

        // Update messages with the actual server response
        setMessages((prev) => {
          // Remove temp message and add both user and assistant messages
          const withoutTemp = prev.filter(
            (m) => m.message_id !== tempUserMessage.message_id
          );
          return [...withoutTemp, assistantMessage];
        });

        // Fetch updated messages to get the user message from server
        await fetchMessages();
      } else {
        setError("Failed to send message");
        // Remove the temporary user message on error
        setMessages((prev) =>
          prev.filter((m) => m.message_id !== tempUserMessage.message_id)
        );
      }
    } catch (err) {
      setError("Failed to send message");
      console.error("Error sending message:", err);
      // Remove the temporary user message on error
      setMessages((prev) =>
        prev.filter((m) => m.message_id !== tempUserMessage.message_id)
      );
    } finally {
      setIsLoading(false);
    }
  };

  const fetchMessages = async () => {
    if (!currentThread) return;

    try {
      const response = await apiGet(
        API_ENDPOINTS.threadMessages(currentThread.thread_id)
      );

      if (response.ok) {
        const fetchedMessages = await response.json();
        setMessages(fetchedMessages);
      }
    } catch (err) {
      console.error("Error fetching messages:", err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getMessageIcon = (role: string) => {
    switch (role) {
      case "user":
        return <User className="w-4 h-4" />;
      case "assistant":
        return <Bot className="w-4 h-4" />;
      default:
        return <MessageCircle className="w-4 h-4" />;
    }
  };

  const getMessageBgColor = (role: string) => {
    switch (role) {
      case "user":
        return "bg-blue-500 text-white";
      case "assistant":
        return "bg-gray-200 text-gray-800";
      default:
        return "bg-yellow-100 text-yellow-800";
    }
  };

  return (
    <div
      className={`flex flex-col h-full bg-white border-l border-gray-200 ${className}`}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <MessageCircle className="w-5 h-5 text-blue-600" />
            <h3 className="font-semibold text-gray-800">Workflow Assistant</h3>
          </div>
          <button
            onClick={createNewThread}
            className="text-sm text-blue-600 hover:text-blue-800"
            disabled={isLoading}
          >
            New Chat
          </button>
        </div>
        {currentThread && (
          <p className="text-xs text-gray-500 mt-1">
            Thread: {currentThread.thread_id.slice(0, 8)}...
          </p>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-3 bg-red-50 border-b border-red-200">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <Bot className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium">
              Welcome to Workflow Assistant!
            </p>
            <p className="text-sm mt-1">
              Ask me about workflows, or request help creating new ones.
            </p>
            <div className="mt-4 text-xs space-y-1">
              <p>💡 Try asking:</p>
              <p>"Show me the available workflows"</p>
              <p>"Create a workflow for email processing"</p>
              <p>"Explain the customer onboarding flow"</p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.message_id}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${getMessageBgColor(
                  message.role
                )}`}
              >
                <div className="flex items-center space-x-2 mb-1">
                  {getMessageIcon(message.role)}
                  <span className="text-xs font-medium">
                    {message.role === "user" ? "You" : "Assistant"}
                  </span>
                  <span className="text-xs opacity-70">
                    {formatTime(message.created_at)}
                  </span>
                </div>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                {message.response_time_ms && (
                  <div className="text-xs opacity-70 mt-1">
                    Response time: {message.response_time_ms}ms
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-800 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <Bot className="w-4 h-4" />
                <span className="text-xs font-medium">Assistant</span>
              </div>
              <div className="flex items-center space-x-1 mt-1">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-pulse"></div>
                  <div
                    className="w-2 h-2 bg-gray-500 rounded-full animate-pulse"
                    style={{ animationDelay: "0.1s" }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-gray-500 rounded-full animate-pulse"
                    style={{ animationDelay: "0.2s" }}
                  ></div>
                </div>
                <span className="text-xs text-gray-500">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about workflows or request help..."
            className="flex-1 p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={1}
            style={{ minHeight: "44px", maxHeight: "120px" }}
            disabled={isLoading || !currentThread}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading || !currentThread}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
