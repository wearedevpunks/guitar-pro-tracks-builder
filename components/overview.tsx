import { motion } from "framer-motion";

import { MessageIcon } from "./icons";
import { Guitar, Skull, Zap } from "lucide-react";

export const Overview = () => {
  return (
    <motion.div
      key="overview"
      className="max-w-3xl mx-auto md:mt-20"
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ delay: 0.5 }}
    >
      <div className="rounded-xl p-6 flex flex-col gap-8 leading-relaxed text-center max-w-xl">
        <div className="flex flex-row justify-center gap-4 items-center mb-6">
          <div className="relative flame-glow">
            <Guitar className="w-12 h-12 text-red-500" />
            <Skull className="w-6 h-6 text-orange-500 absolute -top-2 -right-2 animate-pulse" />
          </div>
          <span className="text-orange-400 font-bold text-2xl">+</span>
          <div className="relative">
            <MessageIcon size={32} />
            <Zap className="w-4 h-4 text-yellow-400 absolute -top-1 -right-1 animate-bounce" />
          </div>
        </div>
        <h2 className="text-2xl font-black text-red-300 mb-4 metal-text">
          🔥 UNLEASH YOUR CREATIVITY 🔥
        </h2>
        <p className="text-orange-200 font-medium mb-4">
          Welcome to the ultimate Guitar Pro Tracks Builder! Create devastating riffs,
          epic solos, and brutal compositions with AI-powered assistance.
        </p>
        <p className="text-muted-foreground">
          Start chatting to get help with building guitar tracks, chord progressions,
          tab notation, or any metal-related music theory questions. Let&apos;s forge some sonic fury! 🎸
        </p>
      </div>
    </motion.div>
  );
};
