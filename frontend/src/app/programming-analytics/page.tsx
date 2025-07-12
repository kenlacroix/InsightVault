"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ProgrammingAnalytics from "@/components/ProgrammingAnalytics";

export default function ProgrammingAnalyticsPage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    setIsAuthenticated(true);
    setLoading(false);
  }, [router]);

  if (loading) {
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
