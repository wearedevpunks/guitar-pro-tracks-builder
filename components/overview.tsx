import { motion } from "framer-motion";
import Link from "next/link";

import { MessageIcon } from "./icons";
import { LogoPython } from "@/app/icons";

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
        <p className="flex flex-row justify-center gap-4 items-center">
          <LogoPython size={32} />
          <span>+</span>
          <MessageIcon size={32} />
        </p>
        <p>
          Welcome to Guitar Pro Tracks Builder - an AI-powered tool for creating,
          editing, and managing Guitar Pro tracks with intelligent suggestions
          and automation.
        </p>
        <p>
          Start a conversation to get help with building guitar tracks, chord
          progressions, tab notation, or any guitar-related music theory questions.
        </p>
      </div>
    </motion.div>
  );
};
