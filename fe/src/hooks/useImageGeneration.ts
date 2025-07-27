import { useState } from "react";
import { CompanyFormData } from "@/components/CompanyForm";
import {
  apiService,
  GeneratedImage as ApiGeneratedImage,
  StreamEvent,
  AdCopy,
} from "@/services/api";

export interface GeneratedImage {
  id: string;
  url: string;
  style: string;
  prompt: string;
  generation_timestamp?: string;
}

export const useImageGeneration = () => {
  const [images, setImages] = useState<GeneratedImage[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState<Record<string, boolean>>(
    {}
  );
  const [requestId, setRequestId] = useState<string | null>(null);
  const [progressMessage, setProgressMessage] = useState<string>("");
  const [currentStep, setCurrentStep] = useState<string>("");
  const [enhancedPrompts, setEnhancedPrompts] = useState<string[]>([]);
  const [adCopy, setAdCopy] = useState<AdCopy | null>(null);
  const [showPrompts, setShowPrompts] = useState(false);
  const [consoleMessages, setConsoleMessages] = useState<string[]>([]);

  const generateImages = async (
    companyData: CompanyFormData
  ): Promise<GeneratedImage[]> => {
    setIsGenerating(true);
    setImages([]);
    setProgressMessage("Starting image generation...");
    setCurrentStep("");
    setConsoleMessages([]);

    return new Promise((resolve, reject) => {
      const finalImages: GeneratedImage[] = [];

      const handleStreamEvent = (event: StreamEvent) => {
        console.log("Stream event:", event);

        switch (event.type) {
          case "step_started":
            setCurrentStep(event.step || "");
            setProgressMessage(event.message);
            break;

          case "progress":
            setProgressMessage(event.message);
            // Add progress messages to console as well
            if (event.message) {
              setConsoleMessages((prev) => [...prev, event.message]);
            }
            break;

          case "step_completed":
            if (event.message) {
              setConsoleMessages((prev) => [...prev, event.message]);
            }
            // Update current step based on the completed step
            if (event.step) {
              // Map completed steps to next step
              const stepProgression = {
                company_analysis: "loading_references",
                loading_references: "prompt_enhancement",
                prompt_enhancement: "copy_generation",
                copy_generation: "image_generation",
                image_generation: "completed",
              };
              const nextStep =
                stepProgression[event.step as keyof typeof stepProgression];
              if (nextStep) {
                setCurrentStep(nextStep);
              }
            }
            break;

          case "prompts_ready":
            if (event.results?.enhanced_prompts) {
              setEnhancedPrompts(event.results.enhanced_prompts);
              setShowPrompts(true);
            }
            setProgressMessage(event.message);
            break;

          case "copy_ready":
            if (event.results?.ad_copy) {
              setAdCopy(event.results.ad_copy);
            }
            setProgressMessage(event.message);
            break;

          case "image_ready":
            if (event.image) {
              const newImage: GeneratedImage = {
                id: event.image.id,
                url: event.image.url,
                style: event.image.style,
                prompt: event.image.prompt_used || "",
                generation_timestamp: event.image.generation_timestamp,
              };
              setImages((prev) => [...prev, newImage]);
              finalImages.push(newImage);
            }
            setProgressMessage(event.message);
            break;

          case "error":
            console.error("Generation error:", event.message);
            setProgressMessage(`Error: ${event.message}`);
            setIsGenerating(false);
            reject(new Error(event.message));
            break;

          case "generation_complete":
            // Handle final images from generation_complete event
            if (event.images && event.images.length > 0) {
              const completedImages: GeneratedImage[] = event.images.map(
                (img: any) => ({
                  id: img.id,
                  url: img.url,
                  style: img.style,
                  prompt: img.prompt_used || "",
                  generation_timestamp: new Date().toISOString(),
                })
              );
              setImages(completedImages);
              finalImages.push(...completedImages);
            }
            // Set ad copy from generation_complete event
            if (event.ad_copy) {
              console.log(
                "Setting ad copy from generation_complete:",
                event.ad_copy
              );
              setAdCopy(event.ad_copy);
            }
            // Set enhanced prompts
            if (event.enhanced_prompts) {
              setEnhancedPrompts(event.enhanced_prompts);
            }
            setProgressMessage("All images generated successfully!");
            setIsGenerating(false);
            setShowPrompts(false); // Close the sidebar canvas
            setCurrentStep(""); // Reset current step
            resolve(finalImages.length > 0 ? finalImages : images);
            break;

          case "done":
            setIsGenerating(false);
            setShowPrompts(false);
            resolve(finalImages);
            break;
        }
      };

      apiService
        .generateImagesStream(companyData, handleStreamEvent)
        .catch((error) => {
          console.error("Stream error:", error);
          setIsGenerating(false);
          setProgressMessage(`Error: ${error.message}`);
          reject(error);
        });
    });
  };

  const regenerateImage = async (
    imageId: string,
    modificationPrompt: string
  ) => {
    setIsRegenerating((prev) => ({ ...prev, [imageId]: true }));

    try {
      // Find the image to get its URL
      const imageToModify = images.find((img) => img.id === imageId);
      if (!imageToModify) {
        throw new Error("Image not found");
      }

      const response = await apiService.modifyImage(
        imageToModify.url,
        modificationPrompt
      );

      if (response.status === "success") {
        // Transform API response and update the specific image
        const updatedImage: GeneratedImage = {
          id: response.image.id,
          url: response.image.url,
          style: response.image.style,
          prompt: response.image.prompt_used,
          generation_timestamp: response.image.generation_timestamp,
        };

        setImages((prev) =>
          prev.map((img) => (img.id === imageId ? updatedImage : img))
        );
      } else {
        throw new Error(response.message || "Failed to regenerate image");
      }
    } catch (error) {
      console.error("Error regenerating image:", error);
      throw error;
    } finally {
      setIsRegenerating((prev) => ({ ...prev, [imageId]: false }));
    }
  };

  const clearImages = () => {
    setImages([]);
    setRequestId(null);
    setEnhancedPrompts([]);
    setAdCopy(null);
    setShowPrompts(false);
    setConsoleMessages([]);
  };

  return {
    images,
    isGenerating,
    isRegenerating,
    requestId,
    progressMessage,
    currentStep,
    enhancedPrompts,
    adCopy,
    showPrompts,
    setShowPrompts,
    consoleMessages,
    generateImages,
    regenerateImage,
    clearImages,
  };
};
