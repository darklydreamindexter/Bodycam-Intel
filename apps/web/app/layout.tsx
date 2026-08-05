import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Bodycam Intelligence",
  description: "Painel de inteligência operacional",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
