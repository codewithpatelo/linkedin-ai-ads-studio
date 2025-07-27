const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface CompanyFormData {
  companyUrl: string;
  productName: string;
  businessValue: string;
  audience: string;
  bodyText: string;
  footerText: string;
}

export interface GeneratedImage {
  id: string;
  url: string;
  style: string;
  prompt_used: string;
  generation_timestamp: string;
}

export interface ImageGenerationResponse {
  request_id: string;
  images: GeneratedImage[];
  status: string;
  message?: string;
}

export interface ImageModificationResponse {
  image: GeneratedImage;
  status: string;
  message?: string;
}

export interface AdCopy {
  headline: string;
  description: string;
  cta: string;
}

export interface StreamEvent {
  type: 'started' | 'progress' | 'step_completed' | 'prompts_ready' | 'copy_ready' | 'image_ready' | 'completed' | 'error' | 'end';
  step?: string;
  message: string;
  request_id?: string;
  images?: GeneratedImage[];
  image?: GeneratedImage;
  progress?: string;
  prompts?: string[];
  ad_copy?: AdCopy;
  enhanced_prompts?: string[];
  results?: {
    enhanced_prompts?: string[];
    ad_copy?: AdCopy;
  };
}

export interface ImageModificationRequest {
  original_image_id: string;
  modification_prompt: string;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`API Error ${response.status}: ${errorData}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  async generateImages(data: CompanyFormData): Promise<ImageGenerationResponse> {
    // Transform frontend data to match backend schema
    const requestData = {
      company_url: data.companyUrl,
      product_name: data.productName,
      business_value: data.businessValue,
      audience: data.audience,
      body_text: data.bodyText,
      footer_text: data.footerText,
    };

    return this.request<ImageGenerationResponse>('/images/generate', {
      method: 'POST',
      body: JSON.stringify(requestData),
    });
  }

  async modifyImage(
    imageId: string,
    modificationPrompt: string
  ): Promise<ImageModificationResponse> {
    const requestData: ImageModificationRequest = {
      original_image_id: imageId,
      modification_prompt: modificationPrompt,
    };

    return this.request<ImageModificationResponse>('/images/modify', {
      method: 'POST',
      body: JSON.stringify(requestData),
    });
  }

  async getAvailableStyles(): Promise<{
    styles: string[];
    descriptions: Record<string, string>;
  }> {
    return this.request('/images/styles');
  }

  async getGeneratedImages(requestId: string): Promise<{
    images: GeneratedImage[];
    original_request: CompanyFormData;
  }> {
    return this.request(`/images/request/${requestId}`);
  }

  async deleteGeneratedImages(requestId: string): Promise<{ message: string }> {
    return this.request(`/images/request/${requestId}`, {
      method: 'DELETE',
    });
  }

  async healthCheck(): Promise<{ status: string }> {
    const url = API_BASE_URL.replace('/api/v1', '/health');
    const response = await fetch(url);
    return response.json();
  }

  async generateImagesStream(
    formData: CompanyFormData,
    onEvent: (event: StreamEvent) => void
  ): Promise<void> {
    const requestData = {
      company_url: formData.companyUrl,
      product_name: formData.productName,
      business_value: formData.businessValue,
      audience: formData.audience,
      body_text: formData.bodyText,
      footer_text: formData.footerText,
    };

    const response = await fetch(`${API_BASE_URL}/stream/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Failed to get response reader');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const eventData = JSON.parse(line.slice(6));
              onEvent(eventData as StreamEvent);
              
              if (eventData.type === 'end') {
                return;
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }
}

export const apiService = new ApiService();
