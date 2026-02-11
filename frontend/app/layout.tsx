import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProviderWrapper } from "./auth/AuthProviderWrapper";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Facturador SaaS",
  description: "Sistema de facturación electrónica SUNAT",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" suppressHydrationWarning>
      <body
        className={`${inter.variable} antialiased font-sans`}
      >
        <AuthProviderWrapper>{children}</AuthProviderWrapper>
      </body>
    </html>
  );
}
