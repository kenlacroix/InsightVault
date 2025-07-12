"use client";

import React, { useState } from "react";
import { ChunkedFileUpload } from "@/components/upload/ChunkedFileUpload";
import { Button } from "@/components/ui/Button";
import { useRouter } from "next/navigation";

interface UploadResult {
  message: string;
  file_id: number;
  filename: string;
  conversations_count: number;
  uploaded_at: string;
}

export default function UploadPage() {
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleUploadSuccess = (data: UploadResult) => {
    setUploadResult(data);
    setError(null);
  };

  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
    setUploadResult(null);
  };

  const handleViewAnalytics = () => {
    router.push("/dashboard");
  };

  const handleUploadAnother = () => {
    setUploadResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Upload Files</h1>
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
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {!uploadResult ? (
            <div className="space-y-8">
              {/* Instructions */}
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-lg font-medium text-gray-900 mb-4">
                  How to Export from ChatGPT
                </h2>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">
                      Method 1: ChatGPT Web
                    </h3>
                    <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
                      <li>Go to ChatGPT and open your conversation</li>
                      <li>Click the three dots menu (⋮) in the top right</li>
                      <li>Select "Export data"</li>
                      <li>Choose "Export" to download your conversations</li>
                    </ol>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 mb-2">
                      Method 2: Manual Export
                    </h3>
                    <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
                      <li>Copy your conversation text</li>
                      <li>Save it as a .txt or .md file</li>
                      <li>Upload the file here</li>
                    </ol>
                  </div>
                </div>
              </div>

              {/* Upload Component */}
              <ChunkedFileUpload
                onUploadSuccess={handleUploadSuccess}
                onUploadError={handleUploadError}
              />

              {/* Error Display */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg
                        className="h-5 w-5 text-red-400"
                        viewBox="0 0 20 20"
                        fill="currentColor"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-red-800">
                        Upload Error
                      </h3>
                      <p className="text-sm text-red-700 mt-1">{error}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Success Display */
            <div className="bg-white p-8 rounded-lg shadow max-w-2xl mx-auto">
              <div className="text-center">
                <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                  <svg
                    className="w-8 h-8 text-green-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </div>

                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Upload Successful!
                </h2>

                <p className="text-gray-600 mb-6">
                  Your file has been processed and conversations have been
                  extracted.
                </p>

                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">File Name</p>
                      <p className="font-medium">{uploadResult.filename}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Conversations</p>
                      <p className="font-medium">
                        {uploadResult.conversations_count}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Upload Time</p>
                      <p className="font-medium">
                        {new Date(uploadResult.uploaded_at).toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">File ID</p>
                      <p className="font-medium">{uploadResult.file_id}</p>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <Button
                    onClick={handleViewAnalytics}
                    className="w-full sm:w-auto"
                  >
                    View Analytics
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleUploadAnother}
                    className="w-full sm:w-auto"
                  >
                    Upload Another File
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
