import "./globals.css";
import { Nav } from "@/components/Nav";
import { Footer } from "@/components/Footer";
import { PlanViewBanner } from "@/components/PlanViewBanner";

export const metadata = {
  title: "EdgeBoard — Professional Sports Analytics",
  description: "Model-driven sports betting analysis, transparent performance, and premium game intelligence."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <PlanViewBanner />
        <Nav />
        {children}
        <Footer />
      </body>
    </html>
  );
}
