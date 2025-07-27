import React, { useState } from 'react';
import { CompanyForm, CompanyFormData } from '@/components/CompanyForm';
import { ImageGallery } from '@/components/ImageGallery';

import { useImageGeneration } from '@/hooks/useImageGeneration';
import { toast } from 'sonner';
import { Sidebar } from '@/components/Sidebar';


type AppState = "form" | "gallery";

const Index = () => {
  const [appState, setAppState] = useState<AppState>("form");
  const [companyData, setCompanyData] = useState<CompanyFormData | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  const { 
    images, 
    isGenerating, 
    isRegenerating, 
    progressMessage,
    currentStep,
    enhancedPrompts,
    adCopy,
    showPrompts,
    setShowPrompts,
    consoleMessages,
    generateImages, 
    regenerateImage 
  } = useImageGeneration();

  const handleFormSubmit = async (data: CompanyFormData) => {
    try {
      setCompanyData(data);
      setIsSidebarOpen(true); // Open sidebar when form is submitted
      const generatedImages = await generateImages(data);
      
      if (generatedImages.length > 0) {
        setAppState("gallery");
        toast.success(`Successfully generated ${generatedImages.length} LinkedIn ads!`);
      } else {
        toast.error("Failed to generate images. Please try again.");
      }
    } catch (error) {
      console.error("Error generating images:", error);
      toast.error("Failed to generate images. Please try again.");
    }
  };

  const handleBackToForm = () => {
    setAppState("form");
  };

  const handleRegenerateImage = async (imageId: string, modificationPrompt: string) => {
    try {
      await regenerateImage(imageId, modificationPrompt);
      toast.success("Image regenerated successfully!");
    } catch (error) {
      console.error("Error regenerating image:", error);
      toast.error("Failed to regenerate image. Please try again.");
    }
  };

  if (appState === "gallery" && companyData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              LinkedIn Ads Generated Successfully!
            </h1>
            <p className="text-gray-600">
              Your AI-powered LinkedIn ad campaign is ready
            </p>
          </div>

          {/* Image Gallery */}
          <ImageGallery
            companyData={companyData}
            images={images}
            adCopy={adCopy}
            onBack={handleBackToForm}
            onRegenerateImage={handleRegenerateImage}
            isRegenerating={isRegenerating}
          />
        </div>

        {/* Sidebar with Console View */}
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
          currentStep={currentStep}
          progressMessage={progressMessage}
          enhancedPrompts={enhancedPrompts}
          adCopy={adCopy}
          isGenerating={isGenerating}
          consoleMessages={consoleMessages}
          showPrompts={showPrompts}
          setShowPrompts={setShowPrompts}
        />
      </div>
    );
  }

  return (
    <>
      <CompanyForm 
        onSubmit={handleFormSubmit} 
        isGenerating={isGenerating}
        progressMessage={progressMessage}
        currentStep={currentStep}
      />
      
      {/* Sidebar with Console View */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        currentStep={currentStep}
        progressMessage={progressMessage}
        enhancedPrompts={enhancedPrompts}
        adCopy={adCopy}
        isGenerating={isGenerating}
        consoleMessages={consoleMessages}
        showPrompts={showPrompts}
        setShowPrompts={setShowPrompts}
      />
    </>
  );
};

export default Index;
