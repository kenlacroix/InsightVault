"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  CheckCircle,
  AlertCircle,
  Eye,
  EyeOff,
  Settings,
  Key,
  Brain,
} from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface SettingsState {
  openaiApiKey: string;
  model: string;
  maxTokens: number;
  temperature: number;
  isTesting: boolean;
  testResult: "success" | "error" | null;
  testMessage: string;
}

export default function SettingsPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [showApiKey, setShowApiKey] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [settings, setSettings] = useState<SettingsState>({
    openaiApiKey: "",
    model: "gpt-4",
    maxTokens: 1500,
    temperature: 0.7,
    isTesting: false,
    testResult: null,
    testMessage: "",
  });

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/auth");
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    // Load current settings
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/settings`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setSettings((prev) => ({
          ...prev,
          openaiApiKey: data.openai_api_key || "",
          model: data.model || "gpt-4",
          maxTokens: data.max_tokens || 1500,
          temperature: data.temperature || 0.7,
        }));
      }
    } catch (error) {
      console.error("Error loading settings:", error);
    }
  };

  const testApiKey = async () => {
    setSettings((prev) => ({
      ...prev,
      isTesting: true,
      testResult: null,
      testMessage: "",
    }));

    try {
      const response = await fetch(`${API_BASE_URL}/settings/test-api-key`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
        },
        body: JSON.stringify({
          api_key: settings.openaiApiKey,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSettings((prev) => ({
          ...prev,
          testResult: "success",
          testMessage: "API key is valid and working!",
        }));
      } else {
        setSettings((prev) => ({
          ...prev,
          testResult: "error",
          testMessage: data.detail || "API key test failed",
        }));
      }
    } catch (error) {
      setSettings((prev) => ({
        ...prev,
        testResult: "error",
        testMessage: "Network error - please check your connection",
      }));
    } finally {
      setSettings((prev) => ({ ...prev, isTesting: false }));
    }
  };

  const saveSettings = async () => {
    setIsSaving(true);

    try {
      const response = await fetch(`${API_BASE_URL}/settings`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
        },
        body: JSON.stringify({
          openai_api_key: settings.openaiApiKey,
          model: settings.model,
          max_tokens: settings.maxTokens,
          temperature: settings.temperature,
        }),
      });

      if (response.ok) {
        alert("Settings saved successfully!");
      } else {
        const data = await response.json();
        alert(`Error saving settings: ${data.detail || "Unknown error"}`);
      }
    } catch (error) {
      alert("Error saving settings. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Settings className="w-8 h-8 text-gray-900 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.push("/dashboard")}
            >
              Back to Dashboard
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {/* OpenAI API Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Brain className="w-5 h-5 mr-2" />
                OpenAI API Configuration
              </CardTitle>
              <CardDescription>
                Configure your OpenAI API key to enable ChatGPT-powered features
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="api-key">OpenAI API Key</Label>
                <div className="relative mt-1">
                  <Input
                    id="api-key"
                    type={showApiKey ? "text" : "password"}
                    value={settings.openaiApiKey}
                    onChange={(e) =>
                      setSettings((prev) => ({
                        ...prev,
                        openaiApiKey: e.target.value,
                      }))
                    }
                    placeholder="sk-..."
                    className="pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showApiKey ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                <p className="text-sm text-gray-500 mt-1">
                  Get your API key from{" "}
                  <a
                    href="https://platform.openai.com/api-keys"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    OpenAI Platform
                  </a>
                </p>
              </div>

              <div className="flex space-x-2">
                <Button
                  onClick={testApiKey}
                  disabled={!settings.openaiApiKey || settings.isTesting}
                  variant="outline"
                >
                  {settings.isTesting ? "Testing..." : "Test API Key"}
                </Button>
                <Button onClick={saveSettings} disabled={isSaving}>
                  {isSaving ? "Saving..." : "Save Settings"}
                </Button>
              </div>

              {/* Test Result */}
              {settings.testResult && (
                <Alert
                  className={
                    settings.testResult === "success"
                      ? "border-green-200 bg-green-50"
                      : "border-red-200 bg-red-50"
                  }
                >
                  {settings.testResult === "success" ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-red-600" />
                  )}
                  <AlertDescription
                    className={
                      settings.testResult === "success"
                        ? "text-green-800"
                        : "text-red-800"
                    }
                  >
                    {settings.testMessage}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Model Configuration */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Key className="w-5 h-5 mr-2" />
                Model Configuration
              </CardTitle>
              <CardDescription>
                Configure the AI model and response parameters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="model">Model</Label>
                  <select
                    id="model"
                    value={settings.model}
                    onChange={(e) =>
                      setSettings((prev) => ({
                        ...prev,
                        model: e.target.value,
                      }))
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  </select>
                </div>

                <div>
                  <Label htmlFor="max-tokens">Max Tokens</Label>
                  <Input
                    id="max-tokens"
                    type="number"
                    value={settings.maxTokens}
                    onChange={(e) =>
                      setSettings((prev) => ({
                        ...prev,
                        maxTokens: parseInt(e.target.value),
                      }))
                    }
                    min="100"
                    max="4000"
                    step="100"
                  />
                </div>

                <div>
                  <Label htmlFor="temperature">Temperature</Label>
                  <Input
                    id="temperature"
                    type="number"
                    value={settings.temperature}
                    onChange={(e) =>
                      setSettings((prev) => ({
                        ...prev,
                        temperature: parseFloat(e.target.value),
                      }))
                    }
                    min="0"
                    max="2"
                    step="0.1"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Help Section */}
          <Card>
            <CardHeader>
              <CardTitle>How to Get Your API Key</CardTitle>
            </CardHeader>
            <CardContent>
              <ol className="list-decimal list-inside space-y-2 text-sm text-gray-600">
                <li>
                  Go to{" "}
                  <a
                    href="https://platform.openai.com/api-keys"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800"
                  >
                    OpenAI Platform
                  </a>
                </li>
                <li>Sign in or create an account</li>
                <li>Click "Create new secret key"</li>
                <li>Copy the key (it starts with "sk-")</li>
                <li>Paste it in the field above</li>
                <li>Click "Test API Key" to verify it works</li>
                <li>Click "Save Settings" to store it</li>
              </ol>

              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                <p className="text-sm text-blue-800">
                  <strong>Note:</strong> Your API key is stored securely and
                  only used to communicate with OpenAI's servers. We never store
                  or log your conversations.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
