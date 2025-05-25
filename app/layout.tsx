import "./globals.css"
import { GeistSans } from "geist/font/sans"
import { Toaster } from "sonner"
import { cn } from "@/lib/utils"
import { Navbar } from "@/components/navbar"
import { RootProvider } from "@/root/providers"

export const metadata = {
  title: "Guitar Pro Tracks Builder",
  description:
    "AI-powered tool for building and managing Guitar Pro tracks with intelligent suggestions and automation.",
  openGraph: {
    images: [
      {
        url: "/og?title=Guitar Pro Tracks Builder",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    images: [
      {
        url: "/og?title=Guitar Pro Tracks Builder",
      },
    ],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head></head>
      <body className={cn(GeistSans.className, "antialiased dark")}>
        <RootProvider>
          <Toaster position="top-center" richColors />
          <Navbar />
          <div className="flex flex-col items-center justify-center min-h-[calc(100vh-64px)] w-full px-4">
            {children}
          </div>
        </RootProvider>
      </body>
    </html>
  )
}
