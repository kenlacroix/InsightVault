"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/Button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/contexts/AuthContext";

interface ContextData {
  historical_context: {
    conversations: Array<{
      id: string;
      title: string;
      content_preview: string;
      created_at: string;
      topics: string[];
      sentiment: string;
    }>;
    total_count: number;
    topics: string[];
    sentiment: string;
  };
  recent_context: {
    interactions: Array<{
      id: string;
      question: string;
      answer: string;
      created_at: string;
    }>;
    total_count: number;
    session_active: boolean;
    session_info: any;
  };
  combined_summary: string;
}

interface ContextFusionDisplayProps {
  onContextUpdate?: (contextData: ContextData) => void;
}

export default function ContextFusionDisplay({
  onContextUpdate,
}: ContextFusionDisplayProps) {
  const { token } = useAuth();
  const [contextData, setContextData] = useState<ContextData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    console.log("🔍 ContextFusion: Component mounted/updated");
    console.log("🔍 ContextFusion: Token changed:", !!token);

    if (token) {
      console.log("🔍 ContextFusion: Token available, fetching data...");
      fetchContextData();
    } else {
      console.log("🔍 ContextFusion: No token available, skipping fetch");
    }
  }, [token]);

  const fetchContextData = async () => {
    try {
      setLoading(true);
      console.log("🔍 ContextFusion: Starting fetch...");
      console.log("🔍 ContextFusion: Token available:", !!token);
      console.log("🔍 ContextFusion: Token length:", token?.length || 0);

      if (!token) {
        console.error("❌ ContextFusion: No token available");
        throw new Error("No authentication token available");
      }

      console.log("🔍 ContextFusion: Making request to /api/context/fusion");
      const response = await fetch("/api/context/fusion", {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      console.log("🔍 ContextFusion: Response status:", response.status);
      console.log(
        "🔍 ContextFusion: Response headers:",
        Object.fromEntries(response.headers.entries())
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error(
          "❌ ContextFusion: Response not OK:",
          response.status,
          errorText
        );
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log("🔍 ContextFusion: Response data:", result);

      if (result.success) {
        console.log("✅ ContextFusion: Success! Setting data");
        setContextData(result.data);
        onContextUpdate?.(result.data);
      } else {
        console.error("❌ ContextFusion: API returned success: false", result);
        throw new Error(result.message || "Failed to fetch context data");
      }
    } catch (err) {
      console.error("❌ ContextFusion: Error in fetchContextData:", err);
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case "positive":
        return "bg-green-100 text-green-800";
      case "negative":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg">Context Fusion</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg">Context Fusion</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-red-600 text-sm mb-2">{error}</div>
          <div className="text-xs text-gray-500 mb-2">
            <strong>Debug Info:</strong>
            <br />
            Token available: {token ? "Yes" : "No"}
            <br />
            Token length: {token?.length || 0}
            <br />
            Check browser console for detailed logs
          </div>
          <Button
            onClick={fetchContextData}
            className="mt-2"
            variant="outline"
            size="sm"
          >
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!contextData) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg">Context Fusion</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-gray-500 text-sm mb-2">
            No context data available
          </div>
          <div className="text-xs text-gray-500">
            <strong>Debug Info:</strong>
            <br />
            Token available: {token ? "Yes" : "No"}
            <br />
            Token length: {token?.length || 0}
            <br />
            Loading: {loading ? "Yes" : "No"}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Context Fusion</CardTitle>
          <Button
            onClick={() => setIsExpanded(!isExpanded)}
            variant="outline"
            size="sm"
          >
            {isExpanded ? "Collapse" : "Expand"}
          </Button>
        </div>
        <div className="text-sm text-gray-600">
          {contextData.combined_summary}
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent>
          <Tabs defaultValue="historical" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="historical">
                Historical ({contextData.historical_context.total_count})
              </TabsTrigger>
              <TabsTrigger value="recent">
                Recent ({contextData.recent_context.total_count})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="historical" className="space-y-3">
              {contextData.historical_context.conversations.length > 0 ? (
                <>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {contextData.historical_context.topics
                      .slice(0, 5)
                      .map((topic, index) => (
                        <Badge
                          key={index}
                          variant="secondary"
                          className="text-xs"
                        >
                          {topic}
                        </Badge>
                      ))}
                  </div>

                  {contextData.historical_context.conversations.map(
                    (conversation) => (
                      <div
                        key={conversation.id}
                        className="border rounded-lg p-3 space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <h4 className="font-medium text-sm">
                            {conversation.title}
                          </h4>
                          <Badge
                            className={`text-xs ${getSentimentColor(conversation.sentiment)}`}
                          >
                            {conversation.sentiment}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 line-clamp-2">
                          {conversation.content_preview}
                        </p>
                        <div className="text-xs text-gray-500">
                          {formatDate(conversation.created_at)}
                        </div>
                      </div>
                    )
                  )}
                </>
              ) : (
                <div className="text-gray-500 text-sm text-center py-4">
                  No historical conversations found
                </div>
              )}
            </TabsContent>

            <TabsContent value="recent" className="space-y-3">
              {contextData.recent_context.interactions.length > 0 ? (
                contextData.recent_context.interactions.map((interaction) => (
                  <div
                    key={interaction.id}
                    className="border rounded-lg p-3 space-y-2"
                  >
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-gray-900">
                        Q: {interaction.question}
                      </p>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        A: {interaction.answer}
                      </p>
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatDate(interaction.created_at)}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-gray-500 text-sm text-center py-4">
                  No recent interactions found
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      )}
    </Card>
  );
}
