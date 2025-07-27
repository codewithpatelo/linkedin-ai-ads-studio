import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, ExternalLink, ThumbsUp, MessageCircle, Share, Send } from 'lucide-react';
import { AdCopy } from '@/services/api';
import { GeneratedImage } from '@/hooks/useImageGeneration';

interface AdPreviewProps {
  images: GeneratedImage[];
  adCopy: AdCopy | null;
  companyName?: string;
}

export const AdPreview: React.FC<AdPreviewProps> = ({
  images,
  adCopy,
  companyName = "Your Company"
}) => {
  const downloadImage = async (imageUrl: string, imageName: string) => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${imageName}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading image:', error);
    }
  };

  if (!images.length && !adCopy) return null;

  return (
    <div className="w-full space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-xl font-semibold text-gray-800">LinkedIn Ad Preview</h3>
        <div className="flex gap-2">
          {images.map((image, index) => (
            <Button
              key={image.id}
              variant="outline"
              size="sm"
              onClick={() => downloadImage(image.url, `linkedin-ad-${image.style}-${index + 1}`)}
              className="flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              Download {image.style}
            </Button>
          ))}
        </div>
      </div>

      <div className="grid gap-6">
        {images.map((image, index) => (
          <Card key={image.id} className="max-w-2xl mx-auto border border-gray-200 shadow-sm">
            {/* LinkedIn Post Header */}
            <div className="p-4 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-semibold text-lg">
                    {companyName.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">{companyName}</h4>
                  <p className="text-sm text-gray-500">Sponsored</p>
                </div>
              </div>
            </div>

            <CardContent className="p-0">
              {/* Ad Copy */}
              {adCopy && (
                <div className="p-4">
                  <h5 className="font-semibold text-lg text-gray-900 mb-2">
                    {adCopy.headline}
                  </h5>
                  <p className="text-gray-700 text-sm leading-relaxed mb-3">
                    {adCopy.description}
                  </p>
                </div>
              )}

              {/* Ad Image */}
              <div className="relative">
                <img
                  src={image.url}
                  alt={`LinkedIn ad - ${image.style} style`}
                  className="w-full h-auto object-cover"
                />
                <div className="absolute top-3 right-3">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => downloadImage(image.url, `linkedin-ad-${image.style}-${index + 1}`)}
                    className="bg-white/90 hover:bg-white text-gray-700 shadow-sm"
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Call to Action */}
              {adCopy && (
                <div className="p-4 border-t border-gray-100">
                  <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium">
                    {adCopy.cta}
                    <ExternalLink className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              )}

              {/* LinkedIn Engagement Actions */}
              <div className="px-4 py-3 border-t border-gray-100 bg-gray-50">
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <div className="flex items-center gap-4">
                    <button className="flex items-center gap-1 hover:text-blue-600 transition-colors">
                      <ThumbsUp className="h-4 w-4" />
                      Like
                    </button>
                    <button className="flex items-center gap-1 hover:text-blue-600 transition-colors">
                      <MessageCircle className="h-4 w-4" />
                      Comment
                    </button>
                    <button className="flex items-center gap-1 hover:text-blue-600 transition-colors">
                      <Share className="h-4 w-4" />
                      Share
                    </button>
                    <button className="flex items-center gap-1 hover:text-blue-600 transition-colors">
                      <Send className="h-4 w-4" />
                      Send
                    </button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Style Information */}
      {images.length > 0 && (
        <div className="text-center">
          <p className="text-sm text-gray-500">
            Generated {images.length} ad{images.length > 1 ? 's' : ''} in{' '}
            {images.map(img => img.style).join(', ')} style{images.length > 1 ? 's' : ''}
          </p>
        </div>
      )}
    </div>
  );
};
