'use client';

import React, { useState } from 'react';
import { ArrowUpRight, Copy, Check, Sparkles, Send } from 'lucide-react';

export default function InteractiveFooter({ onOpenStudio }: { onOpenStudio?: () => void }) {
  const [copied, setCopied] = useState(false);
  const email = 'commissions@ateliernocturne.studio';

  const handleCopy = () => {
    navigator.clipboard.writeText(email);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <footer className="relative py-28 px-6 sm:px-12 bg-black border-t border-white/10 pointer-events-auto overflow-hidden">
      {/* Ambient background glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-48 bg-cyan-500/10 blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto w-full flex flex-col justify-between">
        {/* Massive Call To Action */}
        <div className="text-center sm:text-left mb-20">
          <div className="flex items-center gap-3 font-mono text-xs text-cyan-400 tracking-[0.3em] uppercase mb-6">
            <span className="w-8 h-[1px] bg-cyan-400" />
            <span>[05] COMMENCE CO-CREATION</span>
          </div>

          <h2 className="text-4xl sm:text-7xl md:text-8xl font-bold tracking-tighter uppercase text-white leading-tight">
            READY TO BUILD <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-indigo-300 to-fuchsia-400 italic">
              SOMETHING IMMORTAL?
            </span>
          </h2>

          <div className="mt-10 flex flex-wrap items-center gap-4">
            <button
              onClick={handleCopy}
              className="glass-panel px-8 py-4 rounded-full text-white font-mono text-xs sm:text-sm uppercase tracking-widest flex items-center gap-3 hover:border-cyan-400/60 hover:text-cyan-300 transition-all duration-300"
              data-cursor="COPY"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? 'EMAIL COPIED TO CLIPBOARD' : email}</span>
            </button>

            <button
              onClick={onOpenStudio}
              className="px-8 py-4 rounded-full bg-cyan-400 text-black font-semibold text-xs tracking-widest uppercase flex items-center gap-2 hover:bg-cyan-300 hover:shadow-[0_0_30px_rgba(6,182,212,0.5)] transition-all duration-300"
              data-cursor="STUDIO"
            >
              <Sparkles className="w-3.5 h-3.5 fill-black" />
              <span>Explore AI Video Lab</span>
            </button>
          </div>
        </div>

        {/* Footer Meta Strip */}
        <div className="pt-12 border-t border-white/10 grid grid-cols-1 md:grid-cols-4 gap-8 text-xs font-mono text-zinc-400">
          <div>
            <span className="block text-white uppercase tracking-widest font-semibold mb-2">LOCATION</span>
            <p>100 Shoreditch High St<br />London, E1 6JQ<br />United Kingdom</p>
          </div>

          <div>
            <span className="block text-white uppercase tracking-widest font-semibold mb-2">DIRECT INQUIRIES</span>
            <p>Direct: +44 (0) 20 7946 0912<br />Encrypted: signal@ateliernocturne.studio</p>
          </div>

          <div>
            <span className="block text-white uppercase tracking-widest font-semibold mb-2">CHANNELS</span>
            <div className="flex flex-col gap-1 text-zinc-300">
              <a href="#" className="hover:text-cyan-400 flex items-center gap-1">Awwwards Profile <ArrowUpRight className="w-3 h-3" /></a>
              <a href="#" className="hover:text-cyan-400 flex items-center gap-1">GitHub / Tech Core <ArrowUpRight className="w-3 h-3" /></a>
              <a href="#" className="hover:text-cyan-400 flex items-center gap-1">Instagram @ateliernocturne <ArrowUpRight className="w-3 h-3" /></a>
            </div>
          </div>

          <div>
            <span className="block text-white uppercase tracking-widest font-semibold mb-2">ARCHITECTURE</span>
            <p>Next.js 14 &bull; R3F Three.js<br />GSAP 3.12 &bull; Lenis Smooth<br />Fal.ai Video API Ready</p>
          </div>
        </div>

        <div className="mt-12 flex flex-wrap items-center justify-between text-[11px] font-mono text-zinc-500">
          <span>&copy; 2026 ATELIER NOCTURNE. ALL RIGHTS RESERVED.</span>
          <span>CRAFTED FOR PODIUM EXCELLENCE</span>
        </div>
      </div>
    </footer>
  );
}
