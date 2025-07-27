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
          case 'started':
            setProgressMessage(event.message);
            if (event.request_id) {
              setRequestId(event.request_id);
            }
            break;
            
          case 'progress':
            setProgressMessage(event.message);
            setCurrentStep(event.step || '');
            break;
            
          case 'prompts_ready':
            if (event.prompts) {
              setEnhancedPrompts(event.prompts);
            }
            setProgressMessage(event.message);
            break;
            
          case 'copy_ready':
            if (event.ad_copy) {
              setAdCopy(event.ad_copy);
            }
            setProgressMessage(event.message);
            break;
            
          case 'image_ready':
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
            
          case 'completed':
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
            setProgressMessage(`Error: ${event.message}`);
            setIsGenerating(false);
            reject(new Error(event.message));
            break;
            
          case 'end':
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


    generateImages,
    regenerateImage,
    clearImages
  };
};