import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Wand2, Download, RefreshCw, ArrowLeft, Sparkles, Heart, MessageCircle, Repeat2, Send, MoreHorizontal } from "lucide-react";
import { CompanyFormData } from "./CompanyForm";
import { AdCopy } from "@/services/api";

interface GeneratedImage {
  id: string;
  url: string;
  style: string;
  prompt: string;
}

interface ImageGalleryProps {
  companyData: CompanyFormData;
  images: GeneratedImage[];
  adCopy: AdCopy | null;
  onBack: () => void;
  onRegenerateImage: (imageId: string, modificationPrompt: string) => void;
  isRegenerating: Record<string, boolean>;
}

interface LinkedInAdCardProps {
  image: GeneratedImage;
  companyData: CompanyFormData;
  adCopy: AdCopy | null;
  modificationPrompt: string;
  onModificationChange: (prompt: string) => void;
  onRegenerate: () => void;
  onDownload: () => void;
  isRegenerating: boolean;
}

const LinkedInAdCard = ({ 
  image, 
  companyData, 
  adCopy, 
  modificationPrompt, 
  onModificationChange, 
  onRegenerate, 
  onDownload, 
  isRegenerating 
}: LinkedInAdCardProps) => {
  // Company initial from company name with null check
  const companyInitial = companyData?.companyName?.charAt(0)?.toUpperCase() || 'C';
  
  // Use adCopy if available, otherwise fallback to company data with null checks
  const headline = adCopy?.headline || `Discover ${companyData?.productName || 'Our Product'}`;
  const description = adCopy?.description || `${companyData?.businessValue || 'Amazing value'} for ${companyData?.audience || 'our customers'}`;
  
  return (
    <Card className="bg-white shadow-lg border-0 overflow-hidden max-w-lg mx-auto">
      <CardContent className="p-0">
        {/* LinkedIn Post Header */}
        <div className="p-4 flex items-center gap-3 border-b border-gray-100">
          <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-lg">
            {companyInitial}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-gray-900 text-sm">{companyData?.companyName || 'Company Name'}</h3>
              <Badge variant="outline" className="text-xs px-2 py-0.5 bg-gray-50 text-gray-600 border-gray-200">
                Sponsored
              </Badge>
            </div>
            <p className="text-xs text-gray-500">2.1M followers</p>
          </div>
          <Button variant="ghost" size="sm" className="p-1 h-auto">
            <MoreHorizontal className="w-4 h-4 text-gray-400" />
          </Button>
        </div>

        {/* Ad Copy */}
        <div className="p-4 pb-3">
          <h4 className="font-semibold text-gray-900 text-sm mb-2 leading-tight">
            {headline}
          </h4>
          <p className="text-sm text-gray-700 leading-relaxed">
            {description}
          </p>
        </div>

        {/* Generated Image */}
        <div className="relative">
          <img
            src={image.url}
            alt={`LinkedIn ad - ${image.style}`}
            className="w-full aspect-[4/3] object-cover"
          />
          <div className="absolute top-3 right-3">
            <Badge className="bg-black/70 text-white text-xs px-2 py-1">
              {image.style}
            </Badge>
          </div>
        </div>

        {/* CTA Section */}
        <div className="p-4 pt-3 border-b border-gray-100">
          <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-sm">
            {companyData.footerText}
          </Button>
        </div>

        {/* LinkedIn Engagement */}
        <div className="px-4 py-3">
          <div className="flex items-center justify-between text-sm text-gray-500 mb-3">
            <div className="flex items-center gap-1">
              <div className="flex -space-x-1">
                <div className="w-4 h-4 bg-blue-600 rounded-full border border-white flex items-center justify-center">
                  <Heart className="w-2 h-2 text-white fill-current" />
                </div>
                <div className="w-4 h-4 bg-green-600 rounded-full border border-white" />
              </div>
              <span className="ml-1">847</span>
            </div>
            <div className="flex gap-3">
              <span>23 comments</span>
              <span>156 reposts</span>
            </div>
          </div>
          
          <div className="flex items-center justify-between pt-3 border-t border-gray-100">
            <Button variant="ghost" size="sm" className="flex-1 flex items-center justify-center gap-2 text-gray-600 hover:bg-gray-50 py-2">
              <Heart className="w-4 h-4" />
              <span className="text-sm font-medium">Like</span>
            </Button>
            <Button variant="ghost" size="sm" className="flex-1 flex items-center justify-center gap-2 text-gray-600 hover:bg-gray-50 py-2">
              <MessageCircle className="w-4 h-4" />
              <span className="text-sm font-medium">Comment</span>
            </Button>
            <Button variant="ghost" size="sm" className="flex-1 flex items-center justify-center gap-2 text-gray-600 hover:bg-gray-50 py-2">
              <Repeat2 className="w-4 h-4" />
              <span className="text-sm font-medium">Repost</span>
            </Button>
            <Button variant="ghost" size="sm" className="flex-1 flex items-center justify-center gap-2 text-gray-600 hover:bg-gray-50 py-2">
              <Send className="w-4 h-4" />
              <span className="text-sm font-medium">Send</span>
            </Button>
          </div>
        </div>

        {/* Modification Controls */}
        <div className="p-4 bg-gray-50 border-t border-gray-100">
          <div className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor={`modify-${image.id}`} className="text-sm font-medium text-gray-700">
                Modify this ad
              </Label>
              <Input
                id={`modify-${image.id}`}
                placeholder="e.g., make it more colorful, change to dark theme..."
                value={modificationPrompt}
                onChange={(e) => onModificationChange(e.target.value)}
                className="text-sm"
              />
            </div>
            
            <div className="flex gap-2">
              <Button
                onClick={onRegenerate}
                disabled={isRegenerating || !modificationPrompt.trim()}
                variant="outline"
                size="sm"
                className="flex-1"
              >
                {isRegenerating ? (
                  <>
                    <div className="w-3 h-3 border-2 border-foreground border-t-transparent rounded-full animate-spin mr-2" />
                    Modifying...
                  </>
                ) : (
                  <>
                    <Wand2 className="w-3 h-3 mr-2" />
                    Modify
                  </>
                )}
              </Button>
              <Button
                onClick={onDownload}
                variant="outline"
                size="sm"
                className="px-3"
              >
                <Download className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export const ImageGallery = ({ 
  companyData, 
  images, 
  adCopy,
  onBack, 
  onRegenerateImage, 
  isRegenerating 
}: ImageGalleryProps) => {
  const [modificationPrompts, setModificationPrompts] = useState<Record<string, string>>({});

  const handleModificationChange = (imageId: string, prompt: string) => {
    setModificationPrompts(prev => ({ ...prev, [imageId]: prompt }));
  };

  const handleRegenerate = (imageId: string) => {
    const prompt = modificationPrompts[imageId] || "";
    onRegenerateImage(imageId, prompt);
  };

  const handleDownload = async (imageUrl: string, imageId: string) => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `linkedin-ad-${imageId}.jpg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <Button 
            variant="outline" 
            onClick={onBack}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Form
          </Button>
          
          <div className="text-center">
            <div className="inline-flex items-center gap-2 bg-gradient-card rounded-full px-4 py-2 shadow-card mb-2">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium">Generated Ads</span>
            </div>
            <h1 className="text-3xl font-bold bg-gradient-hero bg-clip-text text-transparent">
              LinkedIn Ads for {companyData.productName}
            </h1>
          </div>
          
          <div className="w-[120px]" /> {/* Spacer for centering */}
        </div>

        {/* Company Info Summary */}
        <Card className="bg-gradient-card shadow-card border-0 mb-8">
          <CardContent className="p-6">
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="font-medium text-foreground">Target:</span>
                <span className="text-muted-foreground ml-2">{companyData.audience}</span>
              </div>
              <div>
                <span className="font-medium text-foreground">Value:</span>
                <span className="text-muted-foreground ml-2">{companyData.businessValue}</span>
              </div>
              <div>
                <span className="font-medium text-foreground">CTA:</span>
                <span className="text-muted-foreground ml-2">{companyData.footerText}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* LinkedIn Ads Grid */}
        <div className="grid lg:grid-cols-2 xl:grid-cols-3 gap-6 animate-fade-in">
          {images.map((image, index) => (
            <div 
              key={image.id}
              className="animate-scale-in"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <LinkedInAdCard
                image={image}
                companyData={companyData}
                adCopy={adCopy}
                modificationPrompt={modificationPrompts[image.id] || ""}
                onModificationChange={(prompt) => handleModificationChange(image.id, prompt)}
                onRegenerate={() => handleRegenerate(image.id)}
                onDownload={() => handleDownload(image.url, image.id)}
                isRegenerating={isRegenerating[image.id] || false}
              />
            </div>
          ))}
        </div>

        {/* Tips */}
        <Card className="bg-gradient-card shadow-card border-0 mt-8">
          <CardContent className="p-6">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-primary" />
              Modification Tips
            </h3>
            <div className="grid md:grid-cols-2 gap-4 text-sm text-muted-foreground">
              <div>
                <strong className="text-foreground">Style changes:</strong> "make it minimalist", "corporate look", "modern design"
              </div>
              <div>
                <strong className="text-foreground">Colors:</strong> "use blue theme", "darker colors", "vibrant palette"
              </div>
              <div>
                <strong className="text-foreground">Elements:</strong> "add tech icons", "include charts", "professional photo"
              </div>
              <div>
                <strong className="text-foreground">Layout:</strong> "center the text", "split layout", "full background"
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};