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
  const [cameraError, setCameraError] = useState<string | null>(null);

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

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      const video = document.createElement("video");
      video.srcObject = stream;
      video.onloadedmetadata = () => {
        video.play();
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext("2d");
        if (context) {
          context.drawImage(video, 0, 0, canvas.width, canvas.height);
          const base64 = canvas.toDataURL("image/jpeg");
          onImageUpload(base64, "captured_photo.jpg");
        }
      };
      video.onerror = () => {
        setCameraError("Error accessing camera. Please try again.");
      };
    } catch (error) {
      console.error("Error accessing camera:", error);
      setCameraError("Error accessing camera. Please try again.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Drag & Drop Area */}
      <div
        ref={dropRef}
        className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 ${
          isDragOver
            ? "border-black bg-yellow-100 shadow-lg"
            : "border-black/20 hover:border-black hover:bg-yellow-50 hover:shadow-md"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="p-4 bg-yellow-100 rounded-full w-20 h-20 mx-auto mb-6 flex items-center justify-center">
          <Upload className="h-10 w-10 text-black" />
        </div>
        <h3 className="text-lg font-bold text-black mb-3">
          Upload Your Food Photo
        </h3>
        <p className="text-black/70 mb-4 leading-relaxed">
          Drop your food photo here, or{" "}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="text-black underline hover:text-gray-700 font-semibold"
          >
            browse files
          </button>
        </p>
        <p className="text-sm text-black/60">
          Supports JPG, PNG, WebP up to 10MB
        </p>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileInputChange}
          className="hidden"
        />
      </div>

      {/* Camera Capture */}
      <div className="space-y-3">
        <button
          type="button"
          onClick={handleCameraCapture}
          className="w-full bg-gradient-to-r from-black to-gray-800 text-yellow-400 hover:from-gray-800 hover:to-black border-2 border-black py-4 px-6 rounded-xl font-semibold transition-all duration-200 flex items-center justify-center space-x-3 shadow-lg hover:shadow-xl"
        >
          <Camera className="h-5 w-5" />
          <span>Take Photo with Camera</span>
        </button>
        {cameraError && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4">
            <p className="text-red-600 text-sm text-center">{cameraError}</p>
          </div>
        )}
      </div>

      {/* Upload Progress */}
      {isUploading && (
        <div className="space-y-3 bg-yellow-50 border border-yellow-200 rounded-xl p-4">
          <div className="flex items-center justify-between text-sm text-black font-medium">
            <span>Processing your image...</span>
            <span>Please wait</span>
          </div>
          <div className="w-full bg-white rounded-full h-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-black to-gray-800 h-3 rounded-full transition-all duration-300 animate-pulse"
              style={{ width: "100%" }}
            ></div>
          </div>
        </div>
      )}
    </div>
  );
}
