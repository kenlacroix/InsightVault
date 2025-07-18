"use client";

import React, { useState, useEffect, useRef } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { AIProcessingIndicator } from "./AIProcessingIndicator";
import { RecentInteractions } from "./RecentInteractions";
import ContextFusionDisplay from "../context/ContextFusionDisplay";
import { useAuth } from "@/contexts/AuthContext";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface ProcessingStage {
  stage: string;
  status: string;
  icon: string;
}

interface ChatInterfaceProps {
  className?: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function ChatInterface({ className = "" }: ChatInterfaceProps) {
  const { token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStage, setCurrentStage] = useState<
    ProcessingStage | undefined
  >();
  const [setInputValue, setSetInputValue] = useState<React.Dispatch<
    React.SetStateAction<string>
  > | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle follow-up prompt clicks
  const handleFollowUpClick = (question: string) => {
    if (setInputValue) {
      setInputValue(question);
    }
  };

  // Add welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: "welcome",
          role: "assistant",
          content:
            "Hello! I'm your AI assistant. I can help you analyze your ChatGPT conversations and provide insights. You can ask me about:\n\n• Summaries and overviews of your conversations\n• Topics and themes across your chats\n• Sentiment analysis and patterns\n• Specific conversation details\n\nWhat would you like to know about your conversations?",
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  }, [messages.length]);

  const sendMessage = async (content: string) => {
    if (!token) {
      console.error("No authentication token");
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };

    // Optimistic update - add user message immediately
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setCurrentStage(undefined);

    // Add a temporary loading message
    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, loadingMessage]);

    try {
      // Use streaming endpoint for real-time status updates
      const response = await fetch(`${API_BASE_URL}/chat/send-stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: content,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No response body");
      }

      const decoder = new TextDecoder();
      let finalMessage = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.error) {
                // Show the error as an assistant message in the chat
                const errorMessage: Message = {
                  id: (Date.now() + 2).toString(),
                  role: "assistant",
                  content: data.error,
                  timestamp: new Date().toISOString(),
                };
                setMessages((prev) => {
                  const filtered = prev.filter(
                    (msg) => msg.id !== loadingMessage.id
                  );
                  return [...filtered, errorMessage];
                });
                setIsLoading(false);
                setCurrentStage(undefined);
                return; // Stop processing further
              }

              if (data.stage) {
                setCurrentStage({
                  stage: data.stage,
                  status: data.status,
                  icon: data.icon,
                });
              }

              if (data.message) {
                finalMessage = data.message;
              }
            } catch (e) {
              console.error("Error parsing streaming data:", e);
            }
          }
        }
      }

      const assistantMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: "assistant",
        content: finalMessage,
        timestamp: new Date().toISOString(),
      };

      // Replace loading message with actual response
      setMessages((prev) => {
        const filtered = prev.filter((msg) => msg.id !== loadingMessage.id);
        return [...filtered, assistantMessage];
      });

      // Trigger refresh of recent interactions
      setRefreshTrigger((prev) => prev + 1);
    } catch (error) {
      console.error("Error sending message:", error);

      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: "assistant",
        content:
          "Sorry, I encountered an error while processing your request. Please try again.",
        timestamp: new Date().toISOString(),
      };

      // Replace loading message with error
      setMessages((prev) => {
        const filtered = prev.filter((msg) => msg.id !== loadingMessage.id);
        return [...filtered, errorMessage];
      });
    } finally {
      // Wait 500ms before hiding the status indicator so users can see the 'complete' stage
      setTimeout(() => {
        setIsLoading(false);
        setCurrentStage(undefined);
      }, 500);
    }
  };

  return (
    <div className={`flex h-full bg-gray-50 ${className}`}>
      {/* Context Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h3 className="text-sm font-medium text-gray-900">Context Fusion</h3>
          <p className="text-xs text-gray-500 mt-1">
            Historical conversations + recent interactions
          </p>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <ContextFusionDisplay />
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">
              Session Memory
            </h4>
            <RecentInteractions
              onInteractionClick={(question) => {
                if (setInputValue) {
                  setInputValue(question);
                }
              }}
              className="border-0 rounded-none"
              refreshTrigger={refreshTrigger}
            />
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center mr-3">
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                AI Assistant
              </h2>
              <p className="text-sm text-gray-500">
                Ask me about your conversations
              </p>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              role={message.role}
              content={message.content}
              timestamp={message.timestamp}
              onFollowUpClick={handleFollowUpClick}
            />
          ))}

          {/* AI Processing Indicator */}
          <AIProcessingIndicator
            isVisible={isLoading}
            currentStage={currentStage}
            className="mx-4"
          />

          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input */}
        <ChatInput
          onSendMessage={sendMessage}
          isLoading={isLoading}
          placeholder="Ask me about your conversations..."
          setInputValue={setSetInputValue}
        />
      </div>
    </div>
  );
}
