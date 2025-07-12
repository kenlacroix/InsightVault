"use client";

import React, { useState, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/Button";

interface ChunkedFileUploadProps {
  onUploadSuccess?: (data: any) => void;
  onUploadError?: (error: string) => void;
}

interface UploadResponse {
  message: string;
  file_id: number;
  filename: string;
  conversations_count: number;
  uploaded_at: string;
}

const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB chunks

export function ChunkedFileUpload({
  onUploadSuccess,
  onUploadError,
}: ChunkedFileUploadProps) {
  const { token } = useAuth();
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentChunk, setCurrentChunk] = useState(0);
  const [totalChunks, setTotalChunks] = useState(0);

  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const generateUploadId = () => {
    return `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const uploadChunk = async (
    chunk: Blob,
    chunkIndex: number,
    totalChunks: number,
    filename: string,
    uploadId: string
  ): Promise<void> => {
    const formData = new FormData();
    formData.append("chunk", chunk);
    formData.append("chunk_index", chunkIndex.toString());
    formData.append("total_chunks", totalChunks.toString());
    formData.append("filename", filename);
    formData.append("upload_id", uploadId);

    const response = await fetch(`${API_BASE_URL}/files/upload-chunk`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Chunk upload failed");
    }
  };

  const completeUpload = async (uploadId: string): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("upload_id", uploadId);

    const response = await fetch(`${API_BASE_URL}/files/complete-upload`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Upload completion failed");
    }

    return response.json();
  };

  const handleFileUpload = async (file: File) => {
    if (!token) {
      onUploadError?.("Authentication required");
      return;
    }

    // Validate file type
    const allowedTypes = [".json", ".txt", ".md"];
    const fileExtension = file.name
      .toLowerCase()
      .substring(file.name.lastIndexOf("."));

    if (!allowedTypes.includes(fileExtension)) {
      onUploadError?.(`Invalid file type. Allowed: ${allowedTypes.join(", ")}`);
      return;
    }

    // Check if file needs chunked upload (larger than 50MB)
    const needsChunkedUpload = file.size > 50 * 1024 * 1024;

    if (needsChunkedUpload && file.size > 100 * 1024 * 1024) {
      onUploadError?.("File size too large. Maximum 100MB allowed.");
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setCurrentChunk(0);

    try {
      if (needsChunkedUpload) {
        // Use chunked upload for large files
        const uploadId = generateUploadId();
        const chunks = Math.ceil(file.size / CHUNK_SIZE);
        setTotalChunks(chunks);

        // Upload chunks
        for (let i = 0; i < chunks; i++) {
          const start = i * CHUNK_SIZE;
          const end = Math.min(start + CHUNK_SIZE, file.size);
          const chunk = file.slice(start, end);

          await uploadChunk(chunk, i, chunks, file.name, uploadId);

          setCurrentChunk(i + 1);
          setUploadProgress(((i + 1) / chunks) * 90); // 90% for chunk uploads
        }

        // Complete the upload
        const result = await completeUpload(uploadId);
        setUploadProgress(100);
        onUploadSuccess?.(result);
      } else {
        // Use regular upload for smaller files
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_BASE_URL}/files/upload`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || "Upload failed");
        }

        const data: UploadResponse = await response.json();
        setUploadProgress(100);
        onUploadSuccess?.(data);
      }

      // Reset form
      const fileInput = document.getElementById(
        "file-input"
      ) as HTMLInputElement;
      if (fileInput) {
        fileInput.value = "";
      }
    } catch (error) {
      onUploadError?.(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      setCurrentChunk(0);
      setTotalChunks(0);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragOver
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {isUploading ? (
          <div className="space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <div>
              <p className="text-lg font-medium text-gray-900">Uploading...</p>
              {totalChunks > 0 ? (
                <p className="text-sm text-gray-500">
                  Chunk {currentChunk} of {totalChunks} (Chunked upload for
                  large file)
                </p>
              ) : (
                <p className="text-sm text-gray-500">Processing your file</p>
              )}
            </div>
            {uploadProgress > 0 && (
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            )}
            {totalChunks > 0 && (
              <p className="text-xs text-gray-500">
                {Math.round(uploadProgress)}% complete
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
              <svg
                className="w-6 h-6 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>

            <div>
              <p className="text-lg font-medium text-gray-900">
                Upload ChatGPT Export
              </p>
              <p className="text-sm text-gray-500">
                Drag and drop your file here, or click to browse
              </p>
            </div>

            <div className="text-xs text-gray-400 space-y-1">
              <p>Supported formats: JSON, TXT, MD</p>
              <p>Maximum file size: 100MB (chunked upload for large files)</p>
            </div>

            <div className="flex justify-center">
              <input
                id="file-input"
                type="file"
                accept=".json,.txt,.md"
                onChange={handleFileSelect}
                className="hidden"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={() => document.getElementById("file-input")?.click()}
              >
                Choose File
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
