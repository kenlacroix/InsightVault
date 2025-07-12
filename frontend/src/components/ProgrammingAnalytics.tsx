"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts";

interface ProgrammingAnalytics {
  summary: {
    total_programming_conversations: number;
    total_words: number;
    average_sentiment: string;
    sentiment_score: number;
    date_range: {
      earliest: string | null;
      latest: string | null;
    };
  };
  languages: {
    top_languages: Array<{ language: string; count: number }>;
    total_unique_languages: number;
    sentiment_by_language: Record<
      string,
      {
        positive_pct: number;
        negative_pct: number;
        neutral_pct: number;
        total_conversations: number;
      }
    >;
  };
  technologies: {
    top_technologies: Array<{ technology: string; count: number }>;
    total_unique_technologies: number;
  };
  concepts: {
    top_concepts: Array<{ concept: string; count: number }>;
    total_unique_concepts: number;
  };
  difficulty_analysis: {
    current_distribution: Record<string, number>;
    learning_progression: {
      early_period: Record<string, number>;
      recent_period: Record<string, number>;
    };
  };
  activity_trends: {
    monthly_activity: Array<[string, number]>;
    most_active_month: string | null;
  };
  insights: {
    primary_focus: string;
    technology_stack: string[];
    key_learning_areas: string[];
    learning_pattern: string;
  };
}

const COLORS = [
  "#0088FE",
  "#00C49F",
  "#FFBB28",
  "#FF8042",
  "#8884D8",
  "#82CA9D",
];

export default function ProgrammingAnalytics() {
  const [analytics, setAnalytics] = useState<ProgrammingAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProgrammingAnalytics();
  }, []);

  const fetchProgrammingAnalytics = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/chat/programming-analytics", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch programming analytics");
      }

      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading programming analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">No programming analytics available</div>
      </div>
    );
  }

  const sentimentData = Object.entries(
    analytics.languages.sentiment_by_language
  ).map(([lang, data]) => ({
    language: lang,
    positive: data.positive_pct,
    negative: data.negative_pct,
    neutral: data.neutral_pct,
  }));

  const difficultyData = Object.entries(
    analytics.difficulty_analysis.current_distribution
  ).map(([level, count]) => ({
    level: level.charAt(0).toUpperCase() + level.slice(1),
    count,
  }));

  const monthlyData = analytics.activity_trends.monthly_activity.map(
    ([month, count]) => ({
      month,
      conversations: count,
    })
  );

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Conversations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics.summary.total_programming_conversations}
            </div>
            <p className="text-xs text-muted-foreground">
              Programming-related chats
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Words</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics.summary.total_words.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              In programming conversations
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Languages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics.languages.total_unique_languages}
            </div>
            <p className="text-xs text-muted-foreground">
              Programming languages discussed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sentiment</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analytics.summary.average_sentiment}
            </div>
            <p className="text-xs text-muted-foreground">
              Overall programming mood
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Key Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Key Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold mb-2">Primary Focus</h4>
              <Badge variant="secondary" className="text-lg px-3 py-1">
                {analytics.insights.primary_focus}
              </Badge>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Learning Pattern</h4>
              <Badge variant="outline" className="text-lg px-3 py-1">
                {analytics.insights.learning_pattern}
              </Badge>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Technology Stack</h4>
              <div className="flex flex-wrap gap-2">
                {analytics.insights.technology_stack.map((tech) => (
                  <Badge key={tech} variant="secondary">
                    {tech}
                  </Badge>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Key Learning Areas</h4>
              <div className="flex flex-wrap gap-2">
                {analytics.insights.key_learning_areas.map((concept) => (
                  <Badge key={concept} variant="outline">
                    {concept}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Analytics Tabs */}
      <Tabs defaultValue="languages" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="languages">Languages</TabsTrigger>
          <TabsTrigger value="technologies">Technologies</TabsTrigger>
          <TabsTrigger value="concepts">Concepts</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="languages" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Top Programming Languages</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analytics.languages.top_languages}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="language" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#0088FE" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Sentiment by Language</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={sentimentData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="language" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="positive" stackId="a" fill="#00C49F" />
                    <Bar dataKey="neutral" stackId="a" fill="#FFBB28" />
                    <Bar dataKey="negative" stackId="a" fill="#FF8042" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="technologies" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Top Technologies & Frameworks</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart
                  data={analytics.technologies.top_technologies}
                  layout="horizontal"
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="technology" type="category" width={100} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884D8" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="concepts" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Top Programming Concepts</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={analytics.concepts.top_concepts}
                    layout="horizontal"
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="concept" type="category" width={100} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#82CA9D" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Difficulty Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={difficultyData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ level, percent }) =>
                        `${level} ${(percent * 100).toFixed(0)}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {difficultyData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Monthly Activity Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={monthlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="conversations"
                    stroke="#0088FE"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
