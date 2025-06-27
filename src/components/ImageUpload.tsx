"use client";

import { useState, useRef } from "react";
import { Upload, Camera } from "lucide-react";

interface ImageUploadProps {
  onImageUpload: (base64: string, filename: string) => void;
}

export default function ImageUpload({ onImageUpload }: ImageUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dropRef = useRef<HTMLDivElement>(null);

  const convertToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        resolve(result);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const handleFileSelect = async (file: File) => {
    if (!file) return;

    // Validate file type
    const validTypes = ["image/jpeg", "image/jpg", "image/png", "image/webp"];
    if (!validTypes.includes(file.type)) {
      alert("Please select a valid image file (JPG, PNG, or WebP)");
      return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      alert("File size must be less than 10MB");
      return;
    }

    setIsUploading(true);
    try {
      const base64 = await convertToBase64(file);
      onImageUpload(base64, file.name);
    } catch (error) {
      console.error("Error converting file to base64:", error);
      alert("Error processing image. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileInputChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);

    const files = event.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleCameraCapture = async () => {
    if (!fileInputRef.current) return;

    // Create a temporary file input for camera capture
    const cameraInput = document.createElement("input");
    cameraInput.type = "file";
    cameraInput.accept = "image/*";
    cameraInput.capture = "environment"; // This opens the rear camera app

    cameraInput.onchange = async (event) => {
      const file = (event.target as HTMLInputElement).files?.[0];
      if (file) {
        await handleFileSelect(file);
      }
      // Clean up the temporary input
      document.body.removeChild(cameraInput);
    };

    // Add to DOM temporarily and trigger click
    cameraInput.style.display = "none";
    document.body.appendChild(cameraInput);
    cameraInput.click();
  };

  return (
    <div className="space-y-6">
      {/* Drag & Drop Area */}
      <div
        ref={dropRef}
        className={`border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300 ${
          isDragOver
            ? "border-black bg-yellow-100 shadow-lg scale-105"
            : "border-black/20 hover:border-black hover:bg-yellow-50 hover:shadow-md hover:scale-[1.02]"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="p-6 bg-yellow-100 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
          <Upload className="h-12 w-12 text-black" />
        </div>

        <p className="text-black/70 mb-6 leading-relaxed text-lg">
          Drop your food photo here, or{" "}
          <button
            type="button"
            className="text-black underline hover:text-gray-700 font-semibold"
          >
            browse files
          </button>
        </p>
        <div className="bg-white/60 rounded-2xl p-4 max-w-md mx-auto">
          <p className="text-sm text-black/60">
            Supports JPG, PNG, WebP up to 10MB
          </p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileInputChange}
          className="hidden"
        />
      </div>

      {/* Camera Capture */}
      <div className="space-y-4">
        <div className="text-center">
          <p className="text-black/60 mb-4">or</p>
        </div>
        <button
          type="button"
          onClick={handleCameraCapture}
          className="w-full bg-black text-yellow-400 hover:bg-gray-800 border-2 border-black py-5 px-6 rounded-3xl font-semibold transition-all duration-200 flex items-center justify-center space-x-3 shadow-lg hover:shadow-xl text-lg"
        >
          <Camera className="h-6 w-6" />
          <span>Take Photo with Camera</span>
        </button>
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="space-y-4 bg-yellow-50 border border-yellow-200 rounded-3xl p-6">
          <div className="flex items-center justify-between text-sm text-black font-medium">
            <span>Processing your image...</span>
            <span>Please wait</span>
          </div>
          <div className="w-full bg-white rounded-full h-4 overflow-hidden">
            <div
              className="bg-gradient-to-r from-black to-gray-800 h-4 rounded-full transition-all duration-300 animate-pulse"
              style={{ width: "100%" }}
            ></div>
          </div>
        </div>
      )}
    </div>
  );
}
