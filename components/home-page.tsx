"use client";

import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { Button } from "./ui/button";
import { Upload, Skull, Zap, Flame, Volume2, Guitar } from "lucide-react";
import { useRouter } from "next/navigation";

export function HomePage() {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.gp') || file.name.endsWith('.gpx') || file.name.endsWith('.gp5') || file.name.endsWith('.gp4')) {
        setUploadedFile(file);
      }
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setUploadedFile(files[0]);
    }
  };

  const handleContinue = () => {
    if (uploadedFile) {
      // Store file info and navigate to track builder
      localStorage.setItem('uploadedFileName', uploadedFile.name);
      router.push('/track');
    }
  };

  const handleStartWithoutFile = () => {
    router.push('/track');
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-100px)] px-4 relative overflow-hidden">
      {/* Background effects */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-20 left-10 animate-pulse">
          <Skull className="w-8 h-8 text-red-500" />
        </div>
        <div className="absolute top-40 right-20 animate-bounce">
          <Zap className="w-6 h-6 text-yellow-500" />
        </div>
        <div className="absolute bottom-40 left-20 animate-pulse">
          <Flame className="w-10 h-10 text-orange-500" />
        </div>
        <div className="absolute bottom-20 right-10 animate-bounce">
          <Volume2 className="w-7 h-7 text-red-400" />
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center mb-12 relative z-10"
      >
        {/* Logo */}
        <motion.div
          initial={{ scale: 0.5, rotate: -10 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ delay: 0.3, duration: 0.8, type: "spring", bounce: 0.4 }}
          className="flex items-center justify-center mb-8"
        >
          <div className="relative flame-glow">
            <Guitar className="w-20 h-20 text-red-500 distorted-hover" />
            <Skull className="w-10 h-10 text-orange-500 absolute -top-3 -right-3 animate-pulse" />
            <Zap className="w-8 h-8 text-yellow-400 absolute -bottom-2 -left-2 animate-bounce" />
          </div>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="text-5xl md:text-7xl font-black metal-gradient bg-clip-text text-transparent mb-6 metal-text tracking-wider"
          style={{ fontFamily: 'Impact, Arial Black, sans-serif' }}
        >
          GUITAR PRO
          <br />
          <span className="text-4xl md:text-6xl">TRACKS BUILDER</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="text-xl text-red-200 max-w-3xl mx-auto font-bold tracking-wide"
        >
          🔥 FORGE BRUTAL RIFFS • CRAFT EPIC SOLOS • UNLEASH YOUR METAL 🔥
        </motion.p>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.8 }}
          className="text-lg text-muted-foreground max-w-2xl mx-auto mt-4"
        >
          AI-powered tool for creating devastating Guitar Pro tracks with intelligent suggestions and metal automation.
        </motion.p>
      </motion.div>

      {/* File Upload Area */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.2, duration: 0.8 }}
        className="w-full max-w-lg relative z-10"
      >
        <div
          className={`
            metal-border rounded-xl p-8 text-center transition-all duration-300 skull-shadow distorted-hover
            ${isDragging 
              ? 'border-red-500 bg-red-950/30 scale-105' 
              : 'hover:bg-red-950/10'
            }
          `}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <motion.div
            animate={{ rotate: isDragging ? 360 : 0 }}
            transition={{ duration: 0.5 }}
          >
            <Upload className="w-16 h-16 mx-auto mb-4 text-red-400 flame-glow" />
          </motion.div>
          
          {uploadedFile ? (
            <div className="space-y-4">
              <div className="text-orange-400 font-bold text-lg flex items-center justify-center gap-2">
                <Flame className="w-5 h-5" />
                ✓ {uploadedFile.name}
                <Flame className="w-5 h-5" />
              </div>
              <Button 
                onClick={handleContinue} 
                className="w-full bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white font-bold py-3 text-lg skull-shadow"
              >
                🔥 UNLEASH THE FURY 🔥
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              <div>
                <h3 className="font-black text-xl mb-3 text-red-300">🎸 LOAD YOUR ARSENAL 🎸</h3>
                <p className="text-sm text-orange-200 font-medium">
                  Drop your .gp, .gpx, .gp5, or .gp4 files into the pit!
                </p>
              </div>
              
              <input
                ref={fileInputRef}
                type="file"
                accept=".gp,.gpx,.gp5,.gp4"
                onChange={handleFileInput}
                className="hidden"
              />
              
              <Button
                onClick={() => fileInputRef.current?.click()}
                variant="outline"
                className="w-full border-red-500 text-red-300 hover:bg-red-950 hover:text-red-200 font-bold py-3 skull-shadow"
              >
                🔥 CHOOSE YOUR WEAPON 🔥
              </Button>
            </div>
          )}
        </div>

        <div className="mt-8 text-center">
          <p className="text-sm text-orange-300 mb-4 font-bold">
            ⚡ OR FORGE FROM THE FLAMES ⚡
          </p>
          <Button 
            onClick={handleStartWithoutFile} 
            className="bg-gradient-to-r from-orange-600 to-yellow-600 hover:from-orange-700 hover:to-yellow-700 text-black font-black py-3 px-8 text-lg skull-shadow distorted-hover"
          >
            🏗️ BUILD FROM SCRATCH 🏗️
          </Button>
        </div>
      </motion.div>
    </div>
  );
}