import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Eye, EyeOff, Copy, Check } from 'lucide-react';
import { useState } from 'react';

interface PromptViewerProps {
  prompts: string[];
  isVisible: boolean;
  onToggleVisibility: () => void;
}

export const PromptViewer: React.FC<PromptViewerProps> = ({
  prompts,
  isVisible,
  onToggleVisibility,
}) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const copyToClipboard = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  if (!prompts.length) return null;

  return (
    <div className="w-full mb-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-800">Enhanced Prompts</h3>
        <Button
          variant="outline"
          size="sm"
          onClick={onToggleVisibility}
          className="flex items-center gap-2"
        >
          {isVisible ? (
            <>
              <EyeOff className="h-4 w-4" />
              Hide Prompts
            </>
          ) : (
            <>
              <Eye className="h-4 w-4" />
              Show Prompts
            </>
          )}
        </Button>
      </div>

      {isVisible && (
        <div className="space-y-4">
          {prompts.map((prompt, index) => (
            <Card key={index} className="border border-gray-200">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-medium text-gray-700">
                    Style {index + 1} Prompt
                  </CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(prompt, index)}
                    className="h-8 w-8 p-0"
                  >
                    {copiedIndex === index ? (
                      <Check className="h-4 w-4 text-green-600" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="bg-gray-50 p-3 rounded-md">
                  <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {prompt}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
