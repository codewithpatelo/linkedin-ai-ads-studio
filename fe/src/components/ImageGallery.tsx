import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Wand2, Download, RefreshCw, ArrowLeft, Sparkles } from "lucide-react";
import { CompanyFormData } from "./CompanyForm";

interface GeneratedImage {
  id: string;
  url: string;
  style: string;
  prompt: string;
}

interface ImageGalleryProps {
  companyData: CompanyFormData;
  images: GeneratedImage[];
  onBack: () => void;
  onRegenerateImage: (imageId: string, modificationPrompt: string) => void;
  isRegenerating: Record<string, boolean>;
}

export const ImageGallery = ({ 
  companyData, 
  images, 
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

        {/* Images Grid */}
        <div className="grid lg:grid-cols-2 xl:grid-cols-3 gap-6 animate-fade-in">
          {images.map((image, index) => (
            <Card 
              key={image.id} 
              className="bg-gradient-card shadow-card border-0 overflow-hidden hover-lift animate-scale-in"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <CardContent className="p-0">
                {/* Image */}
                <div className="relative aspect-square bg-muted group">
                  <img
                    src={image.url}
                    alt={`LinkedIn ad - ${image.style}`}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                  <div className="absolute top-3 left-3">
                    <Badge variant="secondary" className="bg-background/90 text-foreground">
                      {image.style}
                    </Badge>
                  </div>
                  <div className="absolute top-3 right-3">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => handleDownload(image.url, image.id)}
                      className="bg-background/90 hover:bg-background"
                    >
                      <Download className="w-3 h-3" />
                    </Button>
                  </div>
                </div>

                {/* Modification Controls */}
                <div className="p-4 space-y-3">
                  <div className="space-y-2">
                    <Label htmlFor={`modify-${image.id}`} className="text-sm font-medium">
                      Modify this ad
                    </Label>
                    <Input
                      id={`modify-${image.id}`}
                      placeholder="e.g., make it more colorful, change to dark theme, add tech elements..."
                      value={modificationPrompts[image.id] || ""}
                      onChange={(e) => handleModificationChange(image.id, e.target.value)}
                      className="text-sm input-focus"
                    />
                  </div>
                  
                  <Button
                    onClick={() => handleRegenerate(image.id)}
                    disabled={isRegenerating[image.id]}
                    variant="outline"
                    size="sm"
                    className="w-full"
                  >
                    {isRegenerating[image.id] ? (
                      <>
                        <div className="w-3 h-3 border-2 border-foreground border-t-transparent rounded-full animate-spin" />
                        Regenerating...
                      </>
                    ) : (
                      <>
                        <Wand2 className="w-3 h-3" />
                        Regenerate
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
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