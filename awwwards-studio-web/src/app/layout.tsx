import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import LenisProvider from '@/components/common/LenisProvider';
import CustomCursor from '@/components/common/CustomCursor';
import AudioController from '@/components/common/AudioController';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-geist-sans',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-geist-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'ATELIER NOCTURNE &reg; — Haute Creative Engineering & Award-Winning Digital Monuments',
  description: 'A visionary digital atelier crafting WebGL 3D spatial experiences, generative neural video pipelines, and award-winning websites.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable} dark scroll-smooth`}>
      <body className="bg-[#08080a] text-zinc-100 selection:bg-indigo-500/30 selection:text-white font-sans antialiased overflow-x-hidden">
        <LenisProvider>
          <div className="fixed inset-0 bg-noise pointer-events-none z-[1] opacity-35" />
          <CustomCursor />
          <AudioController />
          {children}
        </LenisProvider>
      </body>
    </html>
  );
}
