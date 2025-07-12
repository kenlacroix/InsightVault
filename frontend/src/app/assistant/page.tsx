"use client";

import React from "react";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { Button } from "@/components/ui/Button";
import { useRouter } from "next/navigation";

export default function AssistantPage() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push("/dashboard")}
              >
                Back to Dashboard
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg h-[600px] overflow-hidden">
          <ChatInterface />
        </div>

        {/* Help Section */}
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            How to use the AI Assistant
          </h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">
                Ask for Summaries
              </h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• "Give me a summary of my conversations"</li>
                <li>• "What are the main topics I discuss?"</li>
                <li>• "Show me an overview of my chat history"</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">
                Analyze Patterns
              </h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• "What patterns do you see in my conversations?"</li>
                <li>• "How has my sentiment changed over time?"</li>
                <li>• "What are my most common topics?"</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">
                Specific Insights
              </h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• "Analyze my programming conversations"</li>
                <li>• "What insights can you find about my goals?"</li>
                <li>• "Tell me about my learning patterns"</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">
                Conversation Details
              </h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• "What's the longest conversation I've had?"</li>
                <li>• "Which conversations are most positive?"</li>
                <li>• "Show me conversations about [topic]"</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
