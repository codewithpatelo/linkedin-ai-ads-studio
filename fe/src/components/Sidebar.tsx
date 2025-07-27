import React, { useEffect, useRef } from "react";
import {
  X,
  Eye,
  EyeOff,
  Terminal,
  Sparkles,
  Copy,
  FileText,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AdCopy } from "@/services/api";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentStep: string;
  progressMessage: string;
  enhancedPrompts: string[];
  adCopy: AdCopy | null;
  isGenerating: boolean;
  consoleMessages: string[];
  showPrompts: boolean;
  setShowPrompts: (show: boolean) => void;
}

const steps = [
  { id: "company_analysis", label: "Company Analysis", icon: "🔍" },
  { id: "loading_references", label: "Loading References", icon: "🖼️" },
  { id: "prompt_enhancement", label: "Prompt Enhancement", icon: "✨" },
  { id: "copy_generation", label: "Copy Generation", icon: "📝" },
  { id: "image_generation", label: "Image Generation", icon: "🎨" },
];

const styleColors = {
  professional: "bg-blue-100 text-blue-800 border-blue-200",
  modern: "bg-purple-100 text-purple-800 border-purple-200",
  creative: "bg-pink-100 text-pink-800 border-pink-200",
  minimalist: "bg-gray-100 text-gray-800 border-gray-200",
  bold: "bg-orange-100 text-orange-800 border-orange-200",
};

export const Sidebar = ({
  isOpen,
  onClose,
  currentStep,
  progressMessage,
  enhancedPrompts,
  adCopy,
  isGenerating,
  consoleMessages,
  showPrompts,
  setShowPrompts,
}: SidebarProps) => {
  const consoleRef = useRef<HTMLDivElement>(null);

  // Auto-scroll console to bottom when new messages arrive
  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [consoleMessages]);

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />

      {/* Sidebar */}
      <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-2xl z-50 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Terminal className="w-5 h-5" />
            Generation Console
          </h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex flex-col">
          {/* Progress Steps */}
          <div className="p-4 border-b">
            <h3 className="text-sm font-medium mb-3">Progress</h3>
            <div className="space-y-2">
              {steps.map((step, index) => {
                const isActive = currentStep === step.id;
                const currentStepIndex = steps.findIndex(
                  (s) => s.id === currentStep
                );
                const isCompleted =
                  currentStepIndex > index ||
                  (!isGenerating && currentStepIndex === index);

                return (
                  <div
                    key={step.id}
                    className={`flex items-center gap-3 p-2 rounded-lg transition-colors ${
                      isActive
                        ? "bg-blue-50 border border-blue-200"
                        : isCompleted
                        ? "bg-green-50 border border-green-200"
                        : "bg-gray-50"
                    }`}
                  >
                    <span className="text-lg">{step.icon}</span>
                    <span
                      className={`text-sm font-medium ${
                        isActive
                          ? "text-blue-700"
                          : isCompleted
                          ? "text-green-700"
                          : "text-gray-600"
                      }`}
                    >
                      {step.label}
                    </span>
                    {isActive && (
                      <div className="ml-auto">
                        <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                      </div>
                    )}
                    {isCompleted && (
                      <div className="ml-auto text-green-600">✅</div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Console Messages */}
          <div className="p-4 border-b flex-1 flex flex-col">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium">Console Output</h3>
              <Badge variant="outline" className="text-xs">
                {consoleMessages.length} messages
              </Badge>
            </div>
            <div
              ref={consoleRef}
              className="bg-gray-900 text-green-400 p-3 rounded-lg font-mono text-xs h-48 overflow-y-auto flex-1"
            >
              {consoleMessages.length === 0 ? (
                <div className="text-gray-500">
                  Waiting for generation to start...
                </div>
              ) : (
                consoleMessages.map((message, index) => (
                  <div key={index} className="mb-1">
                    <span className="text-gray-500">
                      [{new Date().toLocaleTimeString()}]
                    </span>{" "}
                    {message}
                  </div>
                ))
              )}
              {isGenerating && (
                <div className="text-yellow-400 animate-pulse">
                  <span className="text-gray-500">
                    [{new Date().toLocaleTimeString()}]
                  </span>{" "}
                  {progressMessage}
                </div>
              )}
            </div>
          </div>

          {/* Enhanced Prompts Section */}
          {enhancedPrompts.length > 0 && (
            <div className="p-4 border-b">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Enhanced Prompts
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowPrompts(!showPrompts)}
                  className="text-xs"
                >
                  {showPrompts ? (
                    <EyeOff className="w-3 h-3" />
                  ) : (
                    <Eye className="w-3 h-3" />
                  )}
                  {showPrompts ? "Hide" : "Show"}
                </Button>
              </div>

              {showPrompts && (
                <ScrollArea className="h-32">
                  <div className="space-y-2">
                    {enhancedPrompts.map((prompt, index) => {
                      const style = [
                        "professional",
                        "modern",
                        "creative",
                        "minimalist",
                        "bold",
                      ][index];
                      return (
                        <Card key={index} className="p-2">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge
                              variant="outline"
                              className={`text-xs ${
                                styleColors[style as keyof typeof styleColors]
                              }`}
                            >
                              {style}
                            </Badge>
                          </div>
                          <p className="text-xs text-gray-600 leading-relaxed">
                            {prompt}
                          </p>
                        </Card>
                      );
                    })}
                  </div>
                </ScrollArea>
              )}
            </div>
          )}

          {/* Ad Copy Section */}
          {adCopy && (
            <div className="p-4">
              <h3 className="text-sm font-medium flex items-center gap-2 mb-3">
                <FileText className="w-4 h-4" />
                Generated Ad Copy
              </h3>
              <Card className="p-3">
                <div className="space-y-2">
                  <div>
                    <Badge variant="outline" className="text-xs mb-1">
                      Headline
                    </Badge>
                    <p className="text-sm font-medium">{adCopy.headline}</p>
                  </div>
                  <div>
                    <Badge variant="outline" className="text-xs mb-1">
                      Description
                    </Badge>
                    <p className="text-xs text-gray-600">
                      {adCopy.description}
                    </p>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </>
  );
};
