import { useState } from 'react';
import { CompanyFormData } from "@/components/CompanyForm";
import { apiService, GeneratedImage as ApiGeneratedImage, StreamEvent, AdCopy } from "@/services/api";

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
  const [isRegenerating, setIsRegenerating] = useState<Record<string, boolean>>({});
  const [requestId, setRequestId] = useState<string | null>(null);
  const [progressMessage, setProgressMessage] = useState<string>('');
  const [currentStep, setCurrentStep] = useState<string>('');
  const [enhancedPrompts, setEnhancedPrompts] = useState<string[]>([]);
  const [adCopy, setAdCopy] = useState<AdCopy | null>(null);
  const [showPrompts, setShowPrompts] = useState(false);

  const generateImages = async (companyData: CompanyFormData): Promise<GeneratedImage[]> => {
    setIsGenerating(true);
    setImages([]);
    setProgressMessage('Starting image generation...');
    setCurrentStep('');
    
    return new Promise((resolve, reject) => {
      let finalImages: GeneratedImage[] = [];
      
      const handleStreamEvent = (event: StreamEvent) => {
        console.log('Stream event:', event);
        
        switch (event.type) {
          case 'step_started':
            console.log('🚀 Step started:', event.step, event.message);
            setProgressMessage(event.message);
            setCurrentStep(event.step || '');
            if (event.request_id) {
              setRequestId(event.request_id);
            }
            break;
            
          case 'progress':
            console.log('📊 Progress:', event.message);
            setProgressMessage(event.message);
            if (event.step) {
              setCurrentStep(event.step);
            }
            break;
            
          case 'step_completed':
            console.log('✅ Step completed:', event.message);
            setProgressMessage(event.message);
            break;
            
          case 'prompts_ready':
            console.log('✨ Prompts ready:', event.prompts?.length);
            if (event.prompts) {
              setEnhancedPrompts(event.prompts);
              setShowPrompts(true);
            }
            setProgressMessage(event.message);
            break;
            
          case 'copy_ready':
            console.log('📝 Copy ready:', event.ad_copy);
            if (event.ad_copy) {
              setAdCopy(event.ad_copy);
            }
            setProgressMessage(event.message);
            break;
            
          case 'image_ready':
            console.log('🖼️ Image ready:', event.image?.style);
            if (event.image) {
              const transformedImage: GeneratedImage = {
                id: event.image.id,
                url: event.image.url,
                style: event.image.style,
                prompt: event.image.prompt_used,
                generation_timestamp: event.image.generation_timestamp,
              };
              setImages(prev => [...prev, transformedImage]);
              finalImages.push(transformedImage);
            }
            setProgressMessage(event.message);
            break;
            
          case 'generation_complete':
            console.log('🎉 Generation complete:', event.images?.length, 'images');
            if (event.images) {
              const transformedImages: GeneratedImage[] = event.images.map((img) => ({
                id: img.id,
                url: img.url,
                style: img.style,
                prompt: img.prompt_used,
                generation_timestamp: img.generation_timestamp,
              }));
              setImages(transformedImages);
              finalImages = transformedImages;
            }
            setProgressMessage(event.message);
            setIsGenerating(false);
            resolve(finalImages);
            break;
            
          case 'error':
            console.error('❌ Error:', event.message);
            setProgressMessage(`Error: ${event.message}`);
            setIsGenerating(false);
            reject(new Error(event.message));
            break;
            
          case 'done':
            console.log('🏁 Stream done');
            setIsGenerating(false);
            if (finalImages.length === 0) {
              reject(new Error('No images were generated'));
            }
            break;
        }
      };
      
      apiService.generateImagesStream(companyData, handleStreamEvent)
        .catch((error) => {
          console.error('Stream error:', error);
          setIsGenerating(false);
          setProgressMessage(`Error: ${error.message}`);
          reject(error);
        });
    });
  };

  const regenerateImage = async (imageId: string, modificationPrompt: string) => {
    setIsRegenerating(prev => ({ ...prev, [imageId]: true }));

    try {
      const response = await apiService.modifyImage(imageId, modificationPrompt);
      
      if (response.status === 'success') {
        // Transform API response and update the specific image
        const updatedImage: GeneratedImage = {
          id: response.image.id,
          url: response.image.url,
          style: response.image.style,
          prompt: response.image.prompt_used,
          generation_timestamp: response.image.generation_timestamp,
        };
        
        setImages(prev => prev.map(img => 
          img.id === imageId ? updatedImage : img
        ));
      } else {
        throw new Error(response.message || 'Failed to regenerate image');
      }
    } catch (error) {
      console.error('Error regenerating image:', error);
      throw error;
    } finally {
      setIsRegenerating(prev => ({ ...prev, [imageId]: false }));
    }
  };

  const clearImages = () => {
    setImages([]);
    setRequestId(null);
    setEnhancedPrompts([]);
    setAdCopy(null);
    setShowPrompts(false);
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
    generateImages,
    regenerateImage,
    clearImages
  };
};