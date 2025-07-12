import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000"
  ),
  title: "InsightVault - AI-Powered Personal Growth Assistant",
  description:
    "Transform your ChatGPT conversations into actionable insights and personal growth opportunities",
  keywords: ["AI", "personal growth", "insights", "chatgpt", "reflection"],
  authors: [{ name: "InsightVault Team" }],
  creator: "InsightVault",
  openGraph: {
    title: "InsightVault - AI-Powered Personal Growth Assistant",
    description:
      "Transform your ChatGPT conversations into actionable insights",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        <AuthProvider>
          <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
            {children}
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
