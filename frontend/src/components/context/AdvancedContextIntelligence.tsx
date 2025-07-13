"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Brain,
  TrendingUp,
  Target,
  Settings,
  Eye,
  EyeOff,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Info,
} from "lucide-react";

interface UseCaseProfile {
  id: number;
  use_case_name: string;
  context_preferences: any;
  topic_weights: Record<string, number>;
  is_active: boolean;
  created_at: string;
  last_used?: string;
}

interface GrowthInsight {
  id: number;
  type: string;
  content: string;
  confidence_score: number;
  detected_at: string;
  related_conversations: number[];
  related_interactions: number[];
  metadata: any;
}

interface ConversationCluster {
  id: number;
  name: string;
  type: string;
  description: string;
  member_count: number;
  members: Array<{
    id: number;
    title: string;
    membership_score: number;
    created_at: string;
  }>;
  metadata: any;
  created_at: string;
  last_updated: string;
}

interface ContextTransparency {
  recent_selections: Array<{
    id: number;
    selection_method: string;
    selected_context: any;
    relevance_scores: any;
    user_feedback: any;
    created_at: string;
  }>;
  system_statistics: {
    total_conversations: number;
    total_interactions: number;
    total_growth_insights: number;
  };
  transparency_features: {
    context_selection_logging: boolean;
    user_feedback_collection: boolean;
    selection_method_disclosure: boolean;
    relevance_score_visibility: boolean;
  };
}

const AdvancedContextIntelligence: React.FC = () => {
  const [activeTab, setActiveTab] = useState("overview");
  const [useCaseProfiles, setUseCaseProfiles] = useState<UseCaseProfile[]>([]);
  const [growthInsights, setGrowthInsights] = useState<GrowthInsight[]>([]);
  const [conversationClusters, setConversationClusters] = useState<
    ConversationCluster[]
  >([]);
  const [transparency, setTransparency] = useState<ContextTransparency | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvancedControls, setShowAdvancedControls] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load use case profiles
      const profilesResponse = await fetch(
        "/api/advanced-context/use-case-profiles",
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );

      if (profilesResponse.ok) {
        const profilesData = await profilesResponse.json();
        setUseCaseProfiles(profilesData.data);
      }

      // Load growth insights
      const insightsResponse = await fetch(
        "/api/advanced-context/growth-insights?limit=10",
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );

      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setGrowthInsights(insightsData.data);
      }

      // Load conversation clusters
      const clustersResponse = await fetch(
        "/api/advanced-context/clusters/me",
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );

      if (clustersResponse.ok) {
        const clustersData = await clustersResponse.json();
        setConversationClusters(clustersData.data);
      }

      // Load transparency data
      const transparencyResponse = await fetch(
        "/api/advanced-context/context-transparency",
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );

      if (transparencyResponse.ok) {
        const transparencyData = await transparencyResponse.json();
        setTransparency(transparencyData.data);
      }
    } catch (err) {
      setError("Failed to load advanced context data");
      console.error("Error loading data:", err);
    } finally {
      setLoading(false);
    }
  };

  const detectGrowthPatterns = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        "/api/advanced-context/detect-growth-patterns",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            user_id: 1, // This should come from user context
            force_refresh: true,
          }),
        }
      );

      if (response.ok) {
        // Reload insights after detection
        await loadData();
      }
    } catch (err) {
      setError("Failed to detect growth patterns");
      console.error("Error detecting patterns:", err);
    } finally {
      setLoading(false);
    }
  };

  const createConversationClusters = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        "/api/advanced-context/create-conversation-clusters",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            user_id: 1, // This should come from user context
          }),
        }
      );

      if (response.ok) {
        // Reload clusters after creation
        await loadData();
      }
    } catch (err) {
      setError("Failed to create conversation clusters");
      console.error("Error creating clusters:", err);
    } finally {
      setLoading(false);
    }
  };

  const getInsightTypeColor = (type: string) => {
    switch (type) {
      case "breakthrough":
        return "bg-green-100 text-green-800";
      case "pattern":
        return "bg-blue-100 text-blue-800";
      case "milestone":
        return "bg-purple-100 text-purple-800";
      case "theme":
        return "bg-orange-100 text-orange-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getClusterTypeColor = (type: string) => {
    switch (type) {
      case "topic":
        return "bg-blue-100 text-blue-800";
      case "emotion":
        return "bg-red-100 text-red-800";
      case "temporal":
        return "bg-green-100 text-green-800";
      case "contextual":
        return "bg-purple-100 text-purple-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Loading advanced context intelligence...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Advanced Context Intelligence</h1>
          <p className="text-gray-600 mt-2">
            Sophisticated topic detection, dynamic context selection, and
            machine learning capabilities
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => setShowAdvancedControls(!showAdvancedControls)}
        >
          {showAdvancedControls ? (
            <EyeOff className="h-4 w-4 mr-2" />
          ) : (
            <Eye className="h-4 w-4 mr-2" />
          )}
          {showAdvancedControls ? "Hide" : "Show"} Advanced Controls
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {showAdvancedControls && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Advanced Controls
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              <Button onClick={detectGrowthPatterns} disabled={loading}>
                <Brain className="h-4 w-4 mr-2" />
                Detect Growth Patterns
              </Button>
              <Button onClick={createConversationClusters} disabled={loading}>
                <Target className="h-4 w-4 mr-2" />
                Create Conversation Clusters
              </Button>
              <Button onClick={loadData} disabled={loading}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh Data
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="insights">Growth Insights</TabsTrigger>
          <TabsTrigger value="clusters">Conversation Clusters</TabsTrigger>
          <TabsTrigger value="transparency">Transparency</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Use Case Profiles */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Use Case Profiles
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {useCaseProfiles.map((profile) => (
                    <div
                      key={profile.id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div>
                        <p className="font-medium">{profile.use_case_name}</p>
                        <p className="text-sm text-gray-500">
                          Created{" "}
                          {new Date(profile.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <Badge
                        variant={profile.is_active ? "default" : "secondary"}
                      >
                        {profile.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                  ))}
                  {useCaseProfiles.length === 0 && (
                    <p className="text-gray-500 text-center py-4">
                      No use case profiles found
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* System Statistics */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  System Statistics
                </CardTitle>
              </CardHeader>
              <CardContent>
                {transparency && (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span>Conversations</span>
                      <span className="font-bold">
                        {transparency.system_statistics.total_conversations}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Interactions</span>
                      <span className="font-bold">
                        {transparency.system_statistics.total_interactions}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Growth Insights</span>
                      <span className="font-bold">
                        {transparency.system_statistics.total_growth_insights}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Clusters</span>
                      <span className="font-bold">
                        {conversationClusters.length}
                      </span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="h-5 w-5" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                {transparency && transparency.recent_selections.length > 0 ? (
                  <div className="space-y-3">
                    {transparency.recent_selections
                      .slice(0, 3)
                      .map((selection) => (
                        <div key={selection.id} className="text-sm">
                          <p className="font-medium">
                            {selection.selection_method}
                          </p>
                          <p className="text-gray-500">
                            {new Date(
                              selection.created_at
                            ).toLocaleDateString()}
                          </p>
                        </div>
                      ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">
                    No recent activity
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                Growth Insights & Patterns
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {growthInsights.map((insight) => (
                  <div key={insight.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <Badge className={getInsightTypeColor(insight.type)}>
                        {insight.type}
                      </Badge>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-500">
                          Confidence:
                        </span>
                        <Progress
                          value={insight.confidence_score * 100}
                          className="w-20"
                        />
                        <span className="text-sm font-medium">
                          {Math.round(insight.confidence_score * 100)}%
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-700 mb-2">{insight.content}</p>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>
                        Detected:{" "}
                        {new Date(insight.detected_at).toLocaleDateString()}
                      </span>
                      <span>
                        Related: {insight.related_conversations.length}{" "}
                        conversations
                      </span>
                    </div>
                  </div>
                ))}
                {growthInsights.length === 0 && (
                  <div className="text-center py-8">
                    <Brain className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-500">
                      No growth insights detected yet
                    </p>
                    <Button onClick={detectGrowthPatterns} className="mt-4">
                      Detect Patterns
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="clusters" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Conversation Clusters
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {conversationClusters.map((cluster) => (
                  <div key={cluster.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="font-semibold">{cluster.name}</h3>
                        <p className="text-sm text-gray-600">
                          {cluster.description}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getClusterTypeColor(cluster.type)}>
                          {cluster.type}
                        </Badge>
                        <span className="text-sm text-gray-500">
                          {cluster.member_count} members
                        </span>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <p className="text-sm font-medium">Recent Members:</p>
                      {cluster.members.slice(0, 3).map((member) => (
                        <div
                          key={member.id}
                          className="flex items-center justify-between text-sm"
                        >
                          <span className="truncate">
                            {member.title || "Untitled"}
                          </span>
                          <span className="text-gray-500">
                            {Math.round(member.membership_score * 100)}% match
                          </span>
                        </div>
                      ))}
                    </div>

                    <div className="mt-3 text-xs text-gray-500">
                      Updated:{" "}
                      {new Date(cluster.last_updated).toLocaleDateString()}
                    </div>
                  </div>
                ))}
                {conversationClusters.length === 0 && (
                  <div className="text-center py-8">
                    <Target className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-500">
                      No conversation clusters found
                    </p>
                    <Button
                      onClick={createConversationClusters}
                      className="mt-4"
                    >
                      Create Clusters
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="transparency" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Context Selection Transparency
              </CardTitle>
            </CardHeader>
            <CardContent>
              {transparency ? (
                <div className="space-y-6">
                  {/* Transparency Features */}
                  <div>
                    <h3 className="font-semibold mb-3">
                      Transparency Features
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(transparency.transparency_features).map(
                        ([feature, enabled]) => (
                          <div
                            key={feature}
                            className="flex items-center gap-2"
                          >
                            {enabled ? (
                              <CheckCircle className="h-4 w-4 text-green-500" />
                            ) : (
                              <AlertCircle className="h-4 w-4 text-red-500" />
                            )}
                            <span className="text-sm">
                              {feature
                                .replace(/_/g, " ")
                                .replace(/\b\w/g, (l) => l.toUpperCase())}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  </div>

                  {/* Recent Context Selections */}
                  <div>
                    <h3 className="font-semibold mb-3">
                      Recent Context Selections
                    </h3>
                    <div className="space-y-3">
                      {transparency.recent_selections.map((selection) => (
                        <div
                          key={selection.id}
                          className="border rounded-lg p-3"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">
                              {selection.selection_method}
                            </span>
                            <span className="text-sm text-gray-500">
                              {new Date(selection.created_at).toLocaleString()}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600">
                            <p>
                              Historical:{" "}
                              {selection.relevance_scores?.historical_count ||
                                0}
                            </p>
                            <p>
                              Recent:{" "}
                              {selection.relevance_scores?.recent_count || 0}
                            </p>
                            <p>
                              Insights:{" "}
                              {selection.relevance_scores?.insights_count || 0}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">
                  No transparency data available
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdvancedContextIntelligence;
