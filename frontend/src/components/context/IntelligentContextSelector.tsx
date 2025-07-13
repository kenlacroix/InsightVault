"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Brain,
  Target,
  Eye,
  EyeOff,
  Settings,
  CheckCircle,
  AlertCircle,
  Info,
  Zap,
  Clock,
  TrendingUp,
} from "lucide-react";

interface ContextSelectionData {
  selected_context: {
    historical_context: Array<{
      id: number;
      type: string;
      content: string;
      title?: string;
      created_at: string;
      relevance_score: number;
    }>;
    recent_context: Array<{
      id: number;
      type: string;
      question: string;
      answer: string;
      created_at: string;
      relevance_score: number;
    }>;
    growth_insights: Array<{
      id: number;
      type: string;
      content: string;
      confidence_score: number;
    }>;
    use_case: any;
    context_summary: string;
    total_length: number;
    selection_method: string;
  };
  use_case_detected: string;
  context_breakdown: {
    historical_conversations: number;
    recent_interactions: number;
    historical_topics: string[];
    session_active: boolean;
  };
  transparency_info: {
    selection_method: string;
    use_case_detected: string;
    context_sources: {
      historical_conversations: number;
      recent_interactions: number;
      growth_insights: number;
    };
    relevance_scoring: string;
    context_length: number;
    max_allowed_length: number;
  };
  user_controls: {
    can_adjust_context_length: boolean;
    can_override_use_case: boolean;
    can_filter_context_types: boolean;
    can_provide_feedback: boolean;
    available_use_cases: string[];
  };
}

interface IntelligentContextSelectorProps {
  question: string;
  onContextSelected: (context: ContextSelectionData) => void;
  onUseCaseDetected?: (useCase: string) => void;
  showTransparency?: boolean;
  maxContextLength?: number;
}

const IntelligentContextSelector: React.FC<IntelligentContextSelectorProps> = ({
  question,
  onContextSelected,
  onUseCaseDetected,
  showTransparency = true,
  maxContextLength,
}) => {
  const [contextData, setContextData] = useState<ContextSelectionData | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [useCaseOverride, setUseCaseOverride] = useState<string | null>(null);

  useEffect(() => {
    if (question.trim()) {
      selectIntelligentContext();
    }
  }, [question, useCaseOverride]);

  const selectIntelligentContext = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        "/api/advanced-context/select-intelligent-context",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            question,
            use_case: useCaseOverride,
            max_context_length: maxContextLength,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setContextData(data);
        onContextSelected(data);

        if (onUseCaseDetected) {
          onUseCaseDetected(data.use_case_detected);
        }
      } else {
        throw new Error("Failed to select intelligent context");
      }
    } catch (err) {
      setError("Failed to select intelligent context");
      console.error("Error selecting context:", err);
    } finally {
      setLoading(false);
    }
  };

  const detectUseCase = async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/advanced-context/detect-use-case", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({ question }),
      });

      if (response.ok) {
        const data = await response.json();
        setUseCaseOverride(data.use_case);
      }
    } catch (err) {
      console.error("Error detecting use case:", err);
    } finally {
      setLoading(false);
    }
  };

  const provideFeedback = async (feedback: any) => {
    if (!contextData) return;

    try {
      await fetch("/api/advanced-context/context-feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          interaction_id: null, // This would come from the current interaction
          feedback,
        }),
      });
    } catch (err) {
      console.error("Error providing feedback:", err);
    }
  };

  const getUseCaseColor = (useCase: string) => {
    switch (useCase) {
      case "therapy":
        return "bg-purple-100 text-purple-800";
      case "data_analysis":
        return "bg-blue-100 text-blue-800";
      case "personal_growth":
        return "bg-green-100 text-green-800";
      case "business":
        return "bg-orange-100 text-orange-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getContextTypeIcon = (type: string) => {
    switch (type) {
      case "conversation":
        return <Clock className="h-4 w-4" />;
      case "interaction":
        return <Zap className="h-4 w-4" />;
      default:
        return <Info className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="text-center">
              <Brain className="h-8 w-8 animate-pulse mx-auto mb-2" />
              <p className="text-sm text-gray-600">
                Selecting intelligent context...
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!contextData) {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* Context Summary Card */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Brain className="h-5 w-5" />
              Intelligent Context Selection
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge className={getUseCaseColor(contextData.use_case_detected)}>
                {contextData.use_case_detected.replace("_", " ")}
              </Badge>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
              >
                {showDetails ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {/* Context Breakdown */}
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="text-center">
                <div className="font-semibold text-blue-600">
                  {contextData.context_breakdown.historical_conversations}
                </div>
                <div className="text-gray-500">Historical</div>
              </div>
              <div className="text-center">
                <div className="font-semibold text-green-600">
                  {contextData.context_breakdown.recent_interactions}
                </div>
                <div className="text-gray-500">Recent</div>
              </div>
              <div className="text-center">
                <div className="font-semibold text-purple-600">
                  {contextData.selected_context.growth_insights.length}
                </div>
                <div className="text-gray-500">Insights</div>
              </div>
            </div>

            {/* Context Length Indicator */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Context Length</span>
                <span>
                  {contextData.transparency_info.context_length.toLocaleString()}{" "}
                  /{" "}
                  {contextData.transparency_info.max_allowed_length.toLocaleString()}{" "}
                  chars
                </span>
              </div>
              <Progress
                value={
                  (contextData.transparency_info.context_length /
                    contextData.transparency_info.max_allowed_length) *
                  100
                }
                className="h-2"
              />
            </div>

            {/* Selection Method */}
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Target className="h-4 w-4" />
              <span>
                Method: {contextData.transparency_info.selection_method}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Context View */}
      {showDetails && (
        <div className="space-y-4">
          {/* Historical Context */}
          {contextData.selected_context.historical_context.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Clock className="h-4 w-4" />
                  Historical Context (
                  {contextData.selected_context.historical_context.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {contextData.selected_context.historical_context.map(
                    (item) => (
                      <div key={item.id} className="border rounded-lg p-3">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium text-sm">
                            {item.title || "Untitled Conversation"}
                          </h4>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-500">
                              {Math.round(item.relevance_score * 100)}% relevant
                            </span>
                            <Badge variant="outline" className="text-xs">
                              {item.type}
                            </Badge>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 line-clamp-2">
                          {item.content}
                        </p>
                        <div className="text-xs text-gray-500 mt-2">
                          {new Date(item.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    )
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recent Context */}
          {contextData.selected_context.recent_context.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Zap className="h-4 w-4" />
                  Recent Context (
                  {contextData.selected_context.recent_context.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {contextData.selected_context.recent_context.map((item) => (
                    <div key={item.id} className="border rounded-lg p-3">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <p className="font-medium text-sm mb-1">
                            Q: {item.question}
                          </p>
                          <p className="text-sm text-gray-600 line-clamp-2">
                            A: {item.answer}
                          </p>
                        </div>
                        <div className="flex items-center gap-2 ml-2">
                          <span className="text-xs text-gray-500">
                            {Math.round(item.relevance_score * 100)}% relevant
                          </span>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(item.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Growth Insights */}
          {contextData.selected_context.growth_insights.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <TrendingUp className="h-4 w-4" />
                  Growth Insights (
                  {contextData.selected_context.growth_insights.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {contextData.selected_context.growth_insights.map(
                    (insight) => (
                      <div key={insight.id} className="border rounded-lg p-3">
                        <div className="flex items-start justify-between mb-2">
                          <Badge variant="outline" className="text-xs">
                            {insight.type}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {Math.round(insight.confidence_score * 100)}%
                            confidence
                          </span>
                        </div>
                        <p className="text-sm text-gray-700">
                          {insight.content}
                        </p>
                      </div>
                    )
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Transparency Information */}
          {showTransparency && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Eye className="h-4 w-4" />
                  Transparency Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="font-medium">Selection Method:</span>
                      <p className="text-gray-600">
                        {contextData.transparency_info.selection_method}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium">Use Case Detected:</span>
                      <p className="text-gray-600">
                        {contextData.transparency_info.use_case_detected}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium">Relevance Scoring:</span>
                      <p className="text-gray-600">
                        {contextData.transparency_info.relevance_scoring}
                      </p>
                    </div>
                    <div>
                      <span className="font-medium">Context Length:</span>
                      <p className="text-gray-600">
                        {contextData.transparency_info.context_length.toLocaleString()}{" "}
                        /{" "}
                        {contextData.transparency_info.max_allowed_length.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* User Controls */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Settings className="h-4 w-4" />
                User Controls
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={detectUseCase}
                    disabled={loading}
                  >
                    <Target className="h-4 w-4 mr-2" />
                    Re-detect Use Case
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      provideFeedback({
                        type: "positive",
                        message: "Context was helpful",
                      })
                    }
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Provide Feedback
                  </Button>
                </div>

                <div className="text-sm text-gray-600">
                  <p>
                    Available use cases:{" "}
                    {contextData.user_controls.available_use_cases.join(", ")}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default IntelligentContextSelector;
