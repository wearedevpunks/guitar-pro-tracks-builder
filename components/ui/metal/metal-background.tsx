import { Skull, Zap, Flame, Volume2 } from "lucide-react";

export function MetalBackground() {
  return (
    <div className="absolute inset-0 opacity-20 pointer-events-none">
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
  );
}