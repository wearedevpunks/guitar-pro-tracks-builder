"use client";

import { Button } from "./ui/button";
import { GitIcon, VercelIcon } from "./icons";
import Link from "next/link";

export const Navbar = () => {
  return (
    <div className="p-2 flex flex-row gap-2 justify-between">
      <div className="text-lg font-semibold text-foreground">
        Guitar Pro Tracks Builder
      </div>
      <div></div>
    </div>
  );
};
