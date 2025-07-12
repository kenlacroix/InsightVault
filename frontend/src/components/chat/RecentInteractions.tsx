"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";

interface Interaction {
  id: number;
  user_question: string;
  ai_response: string;
  context_used: string[] | null;
  created_at: string;
  interaction_metadata: any;
}

interface Session {
  id: number;
  session_start: string;
  session_end: string | null;
  context_summary: string | null;
  interaction_count: number;
}

interface RecentInteractionsData {
  session: Session;
  interactions: Interaction[];
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RecentInteractionsProps {
  className?: string;
  onInteractionClick?: (question: string) => void;
}

export function RecentInteractions({
  className = "",
  onInteractionClick,
}: RecentInteractionsProps) {
  const { token } = useAuth();
  const [recentData, setRecentData] = useState<RecentInteractionsData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const fetchRecentInteractions = async () => {
    if (!token) return;

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/sessions/recent?limit=5`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setRecentData(data);
      }
    } catch (error) {
      console.error("Error fetching recent interactions:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecentInteractions();
  }, [token]);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  const truncateText = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + "...";
  };

  if (recentData.length === 0 && !isLoading) {
    return null; // Don't show anything if no recent interactions
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 ${className}`}>
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">
            Recent Questions
          </h3>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-gray-500 hover:text-gray-700"
          >
            {isExpanded ? "Show less" : "Show more"}
          </button>
        </div>
      </div>

      <div className="max-h-96 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-gray-500">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600 mx-auto"></div>
            <p className="mt-2 text-xs">Loading recent interactions...</p>
          </div>
        ) : (
          recentData.map((data) =>
            data.interactions
              .slice(0, isExpanded ? undefined : 3)
              .map((interaction) => (
                <div
                  key={interaction.id}
                  className="p-4 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() =>
                    onInteractionClick?.(interaction.user_question)
                  }
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center">
                        <svg
                          className="w-3 h-3 text-purple-600"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                          />
                        </svg>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900">
                          {truncateText(interaction.user_question, 80)}
                        </p>
                        <span className="text-xs text-gray-400">
                          {formatTime(interaction.created_at)}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">
                        {truncateText(interaction.ai_response, 60)}
                      </p>
                      {interaction.context_used &&
                        interaction.context_used.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {interaction.context_used.map((context, index) => (
                              <span
                                key={index}
                                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                              >
                                {context}
                              </span>
                            ))}
                          </div>
                        )}
                    </div>
                  </div>
                </div>
              ))
          )
        )}
      </div>

      {!isLoading && recentData.length > 0 && (
        <div className="p-3 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>
              Session started{" "}
              {formatTime(recentData[0]?.session.session_start || "")}
            </span>
            <span>
              {recentData[0]?.session.interaction_count || 0} interactions
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
