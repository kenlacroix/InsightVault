"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import ProgrammingAnalytics from "@/components/ProgrammingAnalytics";
import { useAuth } from "@/contexts/AuthContext";

export default function ProgrammingAnalyticsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/auth");
    }
  }, [isAuthenticated, isLoading, router]);

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
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Programming Analytics</h1>
        <p className="text-muted-foreground">
          Detailed analysis of your programming conversations and learning
          patterns
        </p>
      </div>

      <ProgrammingAnalytics />
    </div>
  );
}
