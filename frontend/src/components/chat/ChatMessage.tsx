import React from "react";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  onFollowUpClick?: (question: string) => void;
}

export function ChatMessage({
  role,
  content,
  timestamp,
  onFollowUpClick,
}: ChatMessageProps) {
  const isUser = role === "user";

  // Parse follow-up prompts from assistant messages
  const parseFollowUpPrompts = (content: string) => {
    const followUpSection = content.split(
      "💡 **Follow-up Questions You Might Find Interesting:**"
    );
    if (followUpSection.length !== 2) {
      return { mainContent: content, followUps: [] };
    }

    const mainContent = followUpSection[0].trim();
    const followUpText = followUpSection[1].trim();

    // Extract numbered questions
    const followUpLines = followUpText
      .split("\n")
      .filter((line) => line.trim());
    const followUps = followUpLines
      .map((line) => {
        const match = line.match(/^\d+\.\s*(.+)$/);
        return match ? match[1].trim() : null;
      })
      .filter(Boolean) as string[];

    return { mainContent, followUps };
  };

  const { mainContent, followUps } = isUser
    ? { mainContent: content, followUps: [] }
    : parseFollowUpPrompts(content);

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md xl:max-w-lg ${isUser ? "order-2" : "order-1"}`}
      >
        <div
          className={`rounded-lg px-4 py-2 ${
            isUser ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
          }`}
        >
          <div className="whitespace-pre-wrap">{mainContent}</div>

          {/* Follow-up prompts */}
          {followUps.length > 0 && (
            <div className="mt-4 pt-3 border-t border-gray-200">
              <div className="text-sm font-medium text-gray-700 mb-2">
                💡 Follow-up Questions:
              </div>
              <div className="space-y-2">
                {followUps.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => onFollowUpClick?.(question)}
                    className="block w-full text-left text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 px-2 py-1 rounded transition-colors duration-200"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        <div
          className={`text-xs text-gray-500 mt-1 ${isUser ? "text-right" : "text-left"}`}
        >
          {new Date(timestamp).toLocaleTimeString()}
        </div>
      </div>

      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center mx-2 ${isUser ? "order-1" : "order-2"}`}
      >
        {isUser ? (
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">U</span>
          </div>
        ) : (
          <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
            <svg
              className="w-4 h-4 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
          </div>
        )}
      </div>
    </div>
  );
}
