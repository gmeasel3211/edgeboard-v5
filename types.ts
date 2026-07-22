import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "EdgeBoard — Sports Intelligence", template: "%s · EdgeBoard" },
  description: "Transparent, tracked sports-betting analytics powered by market-aware modeling.",
  icons: { icon: "/favicon.svg" }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
