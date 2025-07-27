import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Building2, Target, Users, MessageSquare, ArrowRight } from "lucide-react";

export interface CompanyFormData {
  companyUrl: string;
  productName: string;
  businessValue: string;
  audience: string;
  bodyText: string;
  footerText: string;
}

interface CompanyFormProps {
  onSubmit: (data: CompanyFormData) => void;
  isGenerating: boolean;
  progressMessage?: string;
  currentStep?: string;
}

export const CompanyForm = ({ onSubmit, isGenerating, progressMessage, currentStep }: CompanyFormProps) => {
  const [formData, setFormData] = useState<CompanyFormData>({
    companyUrl: "",
    productName: "",
    businessValue: "",
    audience: "",
    bodyText: "",
    footerText: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleChange = (field: keyof CompanyFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const isFormValid = Object.values(formData).every(value => value.trim() !== "");

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="inline-flex items-center gap-3 bg-gradient-card rounded-full px-6 py-3 shadow-card mb-6 hover-lift animate-scale-in">
            <Building2 className="w-6 h-6 text-primary" />
            <span className="text-sm font-medium text-foreground">LinkedIn Ad Generator</span>
          </div>
          <h1 className="text-4xl font-bold bg-gradient-hero bg-clip-text text-transparent mb-4">
            Create Professional LinkedIn Ads
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Generate 5 unique, high-converting LinkedIn advertisement images tailored to your company and audience.
          </p>
        </div>

        {/* Form */}
        <Card className="bg-gradient-card shadow-elevated border-0 hover-lift animate-slide-up">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl font-semibold">Company Information</CardTitle>
            <p className="text-muted-foreground">Tell us about your company to create targeted ads</p>
          </CardHeader>
          <CardContent className="space-y-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                {/* Company URL */}
                <div className="space-y-2">
                  <Label htmlFor="companyUrl" className="text-sm font-medium flex items-center gap-2">
                    <Building2 className="w-4 h-4 text-primary" />
                    Company URL
                  </Label>
                  <Input
                    id="companyUrl"
                    placeholder="https://superhuman.com"
                    value={formData.companyUrl}
                    onChange={(e) => handleChange("companyUrl", e.target.value)}
                    className="bg-background/50 input-focus"
                    required
                  />
                </div>

                {/* Product Name */}
                <div className="space-y-2">
                  <Label htmlFor="productName" className="text-sm font-medium flex items-center gap-2">
                    <Target className="w-4 h-4 text-primary" />
                    Product Name
                  </Label>
                  <Input
                    id="productName"
                    placeholder="AI powered Email"
                    value={formData.productName}
                    onChange={(e) => handleChange("productName", e.target.value)}
                    className="bg-background/50 input-focus"
                    required
                  />
                </div>
              </div>

              {/* Business Value */}
              <div className="space-y-2">
                <Label htmlFor="businessValue" className="text-sm font-medium flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-primary" />
                  Business Value
                </Label>
                <Input
                  id="businessValue"
                  placeholder="Reply to Your Customers Faster"
                  value={formData.businessValue}
                  onChange={(e) => handleChange("businessValue", e.target.value)}
                  className="bg-background/50 input-focus"
                  required
                />
              </div>

              {/* Target Audience */}
              <div className="space-y-2">
                <Label htmlFor="audience" className="text-sm font-medium flex items-center gap-2">
                  <Users className="w-4 h-4 text-primary" />
                  Target Audience
                </Label>
                <Input
                  id="audience"
                  placeholder="Director of Sales, VP of Sales, Head of Business Development"
                  value={formData.audience}
                  onChange={(e) => handleChange("audience", e.target.value)}
                  className="bg-background/50 input-focus"
                  required
                />
              </div>

              {/* Body Text */}
              <div className="space-y-2">
                <Label htmlFor="bodyText" className="text-sm font-medium flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-primary" />
                  Ad Body Text
                </Label>
                <Textarea
                  id="bodyText"
                  placeholder="Slow response times and missed emails weaken trust and put businesses at a disadvantage..."
                  value={formData.bodyText}
                  onChange={(e) => handleChange("bodyText", e.target.value)}
                  className="min-h-[120px] bg-background/50 resize-none input-focus"
                  required
                />
              </div>

              {/* Footer Text */}
              <div className="space-y-2">
                <Label htmlFor="footerText" className="text-sm font-medium">
                  Call-to-Action Text
                </Label>
                <Input
                  id="footerText"
                  placeholder="Boost Client Trust: Respond to Emails 3x Faster with Superhuman!"
                  value={formData.footerText}
                  onChange={(e) => handleChange("footerText", e.target.value)}
                  className="bg-background/50 input-focus"
                  required
                />
              </div>

              {/* Submit Button */}
              <div className="pt-6">
                <Button 
                  type="submit" 
                  variant="hero" 
                  size="lg" 
                  className="w-full"
                  disabled={!isFormValid || isGenerating}
                >
                  {isGenerating ? (
                    <>
                      <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                      {progressMessage || 'Generating LinkedIn Ads...'}
                    </>
                  ) : (
                    <>
                      Generate 5 LinkedIn Ads
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </Button>
                
                {/* Progress Indicator */}
                {isGenerating && currentStep && (
                  <div className="mt-4 p-3 bg-primary/10 rounded-lg border border-primary/20">
                    <div className="flex items-center gap-2 text-sm">
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                      <span className="font-medium text-primary">Current Step:</span>
                      <span className="text-muted-foreground capitalize">{currentStep.replace('_', ' ')}</span>
                    </div>
                  </div>
                )}
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};