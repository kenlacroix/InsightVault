import React from "react";

interface ProcessingStage {
  stage: string;
  status: string;
  icon: string;
}

interface AIProcessingIndicatorProps {
  isVisible: boolean;
  currentStage?: ProcessingStage;
  className?: string;
}

const stageConfig = {
  cache_check: {
    color: "text-blue-500",
    bgColor: "bg-blue-50",
    borderColor: "border-blue-200",
    lightbulbColor: "text-blue-400",
  },
  analysis: {
    color: "text-purple-500",
    bgColor: "bg-purple-50",
    borderColor: "border-purple-200",
    lightbulbColor: "text-purple-400",
  },
  context: {
    color: "text-indigo-500",
    bgColor: "bg-indigo-50",
    borderColor: "border-indigo-200",
    lightbulbColor: "text-indigo-400",
  },
  openai: {
    color: "text-green-500",
    bgColor: "bg-green-50",
    borderColor: "border-green-200",
    lightbulbColor: "text-green-400",
  },
  generation: {
    color: "text-yellow-500",
    bgColor: "bg-yellow-50",
    borderColor: "border-yellow-200",
    lightbulbColor: "text-yellow-400",
  },
  formatting: {
    color: "text-orange-500",
    bgColor: "bg-orange-50",
    borderColor: "border-orange-200",
    lightbulbColor: "text-orange-400",
  },
  complete: {
    color: "text-emerald-500",
    bgColor: "bg-emerald-50",
    borderColor: "border-emerald-200",
    lightbulbColor: "text-emerald-400",
  },
};

export function AIProcessingIndicator({
  isVisible,
  currentStage,
  className = "",
}: AIProcessingIndicatorProps) {
  if (!isVisible) return null;

  const config = currentStage
    ? stageConfig[currentStage.stage as keyof typeof stageConfig] ||
      stageConfig.generation
    : stageConfig.generation;

  return (
    <div
      className={`flex items-center space-x-3 p-3 rounded-lg border ${config.bgColor} ${config.borderColor} ${className}`}
    >
      {/* Animated Lightbulb */}
      <div className="relative">
        <div
          className={`text-2xl ${config.lightbulbColor} ${
            currentStage?.stage === "complete" ? "" : "animate-pulse"
          }`}
        >
          {currentStage?.icon || "💡"}
        </div>

        {/* Glow effect for active stages */}
        {currentStage?.stage !== "complete" && (
          <div
            className={`absolute inset-0 rounded-full ${config.bgColor} animate-ping opacity-20`}
            style={{ animationDuration: "2s" }}
          />
        )}
      </div>

      {/* Status Text */}
      <div className="flex-1">
        <div className={`text-sm font-medium ${config.color}`}>
          {currentStage?.status || "AI is thinking..."}
        </div>

        {/* Progress indicator */}
        {currentStage?.stage !== "complete" && (
          <div className="mt-1">
            <div className="w-full bg-gray-200 rounded-full h-1">
              <div
                className={`h-1 rounded-full ${config.color.replace("text-", "bg-")} transition-all duration-500`}
                style={{
                  width: getProgressWidth(currentStage?.stage || "cache_check"),
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Stage indicator */}
      <div className={`text-xs ${config.color} font-medium`}>
        {getStageNumber(currentStage?.stage || "cache_check")}/6
      </div>
    </div>
  );
}

function getProgressWidth(stage: string): string {
  const stageProgress = {
    cache_check: "16%",
    analysis: "33%",
    context: "50%",
    openai: "66%",
    generation: "83%",
    formatting: "100%",
    complete: "100%",
  };
  return stageProgress[stage as keyof typeof stageProgress] || "16%";
}

function getStageNumber(stage: string): number {
  const stageNumbers = {
    cache_check: 1,
    analysis: 2,
    context: 3,
    openai: 4,
    generation: 5,
    formatting: 6,
    complete: 6,
  };
  return stageNumbers[stage as keyof typeof stageNumbers] || 1;
}
