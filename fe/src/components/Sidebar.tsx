import React, { useEffect, useRef } from 'react';
import { X, Terminal, Copy, Check, Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AdCopy } from '@/services/api';
import { useState } from 'react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentStep: string;
  progressMessage: string;
  enhancedPrompts: string[];
  adCopy: AdCopy | null;
  isGenerating: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onClose,
  currentStep,
  progressMessage,
  enhancedPrompts,
  adCopy,
  isGenerating,
}) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [showPrompts, setShowPrompts] = useState(false);
  const consoleRef = useRef<HTMLDivElement>(null);

  // Auto-scroll console to bottom when new content is added
  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [progressMessage, enhancedPrompts, adCopy]);

  // Show prompts automatically when they're ready
  useEffect(() => {
    if (enhancedPrompts.length > 0) {
      setShowPrompts(true);
    }
  }, [enhancedPrompts]);

  const copyToClipboard = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const getStepStatus = (step: string) => {
    const steps = ['company_analysis', 'loading_references', 'prompt_enhancement', 'copy_generation', 'image_generation'];
    const currentIndex = steps.indexOf(currentStep);
    const stepIndex = steps.indexOf(step);
    
    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅';
      case 'active': return '⏳';
      default: return '⏸️';
    }
  };

  const formatStepName = (step: string) => {
    const names: Record<string, string> = {
      'company_analysis': 'Company Analysis',
      'loading_references': 'Loading References',
      'prompt_enhancement': 'Prompt Enhancement',
      'copy_generation': 'Copy Generation',
      'image_generation': 'Image Generation'
    };
    return names[step] || step.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm" 
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <div className="relative ml-auto w-full max-w-2xl bg-white shadow-2xl">
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b bg-gray-50 px-6 py-4">
            <div className="flex items-center gap-3">
              <Terminal className="h-5 w-5 text-blue-600" />
              <h2 className="text-lg font-semibold text-gray-900">
                Generation Console
              </h2>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="h-8 w-8 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-hidden">
            <div className="h-full overflow-y-auto p-6 space-y-6">
              
              {/* Progress Steps */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium">Progress Steps</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {['company_analysis', 'loading_references', 'prompt_enhancement', 'copy_generation', 'image_generation'].map((step) => {
                    const status = getStepStatus(step);
                    return (
                      <div key={step} className="flex items-center gap-3">
                        <span className="text-lg">{getStepIcon(status)}</span>
                        <span className={`text-sm ${status === 'active' ? 'font-medium text-blue-600' : status === 'completed' ? 'text-green-600' : 'text-gray-500'}`}>
                          {formatStepName(step)}
                        </span>
                        {status === 'active' && (
                          <Badge variant="secondary" className="ml-auto">
                            Active
                          </Badge>
                        )}
                      </div>
                    );
                  })}
                </CardContent>
              </Card>

              {/* Console Output */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Terminal className="h-4 w-4" />
                    Console Output
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div 
                    ref={consoleRef}
                    className="bg-gray-900 text-green-400 p-4 rounded-md font-mono text-xs h-32 overflow-y-auto"
                  >
                    <div className="space-y-1">
                      <div className="text-gray-500">$ linkedin-ads-generator --start</div>
                      <div>🚀 Initializing LinkedIn Ads Generation Studio...</div>
                      {progressMessage && (
                        <div className="text-yellow-400">
                          [{new Date().toLocaleTimeString()}] {progressMessage}
                        </div>
                      )}
                      {!isGenerating && enhancedPrompts.length > 0 && (
                        <div className="text-green-400">
                          ✅ Generation completed successfully!
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Enhanced Prompts */}
              {enhancedPrompts.length > 0 && (
                <Card>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm font-medium">
                        Enhanced Prompts ({enhancedPrompts.length})
                      </CardTitle>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setShowPrompts(!showPrompts)}
                        className="h-8 px-2"
                      >
                        {showPrompts ? (
                          <>
                            <EyeOff className="h-3 w-3 mr-1" />
                            Hide
                          </>
                        ) : (
                          <>
                            <Eye className="h-3 w-3 mr-1" />
                            Show
                          </>
                        )}
                      </Button>
                    </div>
                  </CardHeader>
                  {showPrompts && (
                    <CardContent className="space-y-4">
                      {enhancedPrompts.map((prompt, index) => (
                        <div key={index} className="border rounded-lg">
                          <div className="flex items-center justify-between p-3 bg-gray-50 border-b">
                            <span className="text-xs font-medium text-gray-600">
                              Style {index + 1} Prompt
                            </span>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => copyToClipboard(prompt, index)}
                              className="h-6 w-6 p-0"
                            >
                              {copiedIndex === index ? (
                                <Check className="h-3 w-3 text-green-600" />
                              ) : (
                                <Copy className="h-3 w-3" />
                              )}
                            </Button>
                          </div>
                          <div className="p-3">
                            <div className="bg-gray-900 text-gray-300 p-3 rounded text-xs font-mono max-h-32 overflow-y-auto">
                              <pre className="whitespace-pre-wrap">{prompt}</pre>
                            </div>
                          </div>
                        </div>
                      ))}
                    </CardContent>
                  )}
                </Card>
              )}

              {/* Generated Ad Copy */}
              {adCopy && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-medium">Generated Ad Copy</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Headline
                      </label>
                      <p className="text-sm font-medium text-gray-900 mt-1">
                        {adCopy.headline}
                      </p>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Description
                      </label>
                      <p className="text-sm text-gray-700 mt-1">
                        {adCopy.description}
                      </p>
                    </div>
                    <div>
                      <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">
                        Call to Action
                      </label>
                      <p className="text-sm font-medium text-blue-600 mt-1">
                        {adCopy.cta}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}

            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
