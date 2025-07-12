"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/Button";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  setInputValue?: (
    setter: React.Dispatch<React.SetStateAction<string>>
  ) => void;
}

export function ChatInput({
  onSendMessage,
  isLoading = false,
  placeholder = "Ask me about your conversations...",
  setInputValue,
}: ChatInputProps) {
  const [message, setMessage] = useState<string>("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Expose setMessage function to parent component
  useEffect(() => {
    if (setInputValue) {
      setInputValue(setMessage);
    }
  }, [setInputValue]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedMessage = message?.trim() || "";
    if (trimmedMessage && !isLoading) {
      onSendMessage(trimmedMessage);
      setMessage("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-gray-200 p-4 bg-white"
    >
      <div className="flex items-end space-x-2">
        <div className="flex-1">
          <textarea
            ref={textareaRef}
            value={message || ""}
            onChange={(e) => setMessage(e.target.value || "")}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={isLoading}
            className="w-full resize-none border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
            rows={1}
            maxLength={1000}
          />
        </div>
        <Button
          type="submit"
          disabled={!message?.trim() || isLoading}
          isLoading={isLoading}
          size="sm"
          className="px-4 py-2"
        >
          Send
        </Button>
      </div>
      <div className="text-xs text-gray-500 mt-1">
        Press Enter to send, Shift+Enter for new line
      </div>
    </form>
  );
}
