"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "./ui/button";
import { Home, Music } from "lucide-react";

export const Navbar = () => {
  const pathname = usePathname();
  const isHomePage = pathname === "/";

  return (
    <div className="p-4 flex flex-row gap-4 justify-between items-center border-b border-red-900/30 bg-black/20 backdrop-blur-sm">
      <Link href="/" className="text-lg font-black text-foreground hover:text-red-400 transition-colors metal-text tracking-wider">
        🎸 GUITAR PRO TRACKS BUILDER 🔥
      </Link>
      
      <div className="flex gap-2">
        {!isHomePage && (
          <Link href="/">
            <Button variant="outline" size="sm" className="border-red-500 text-red-300 hover:bg-red-950 hover:text-red-200 font-bold">
              <Home className="w-4 h-4 mr-2" />
              🏠 Home
            </Button>
          </Link>
        )}
        
        {isHomePage && (
          <Link href="/track">
            <Button size="sm" className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white font-bold">
              <Music className="w-4 h-4 mr-2" />
              🎵 Track Builder
            </Button>
          </Link>
        )}
      </div>
    </div>
  );
};
