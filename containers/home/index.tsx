"use client";

import { motion } from "framer-motion";
import { MetalBackground } from "@/components/ui/metal/metal-background";
import { MetalLogo } from "@/components/ui/metal/metal-logo";
import { MetalTitle } from "@/components/ui/metal/metal-title";
import { FileUploadFeature } from "@/features/file-upload/file-upload-feature";

export function HomePageContainer() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-100px)] px-4 relative overflow-hidden">
      <MetalBackground />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center mb-12 relative z-10"
      >
        <div className="mb-8">
          <MetalLogo size="lg" delay={0.3} />
        </div>

        <MetalTitle delay={0.5}>
          GUITAR PRO
          <br />
          <span className="text-4xl md:text-6xl">TRACKS BUILDER</span>
        </MetalTitle>

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

      <FileUploadFeature />
    </div>
  );
}