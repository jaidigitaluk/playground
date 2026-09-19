'use client';

import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowUpRight, Menu, X } from 'lucide-react';

export default function Navbar({ onOpenReel, onOpenStudio }: { onOpenReel?: () => void; onOpenStudio?: () => void }) {
  const [time, setTime] = useState('');
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString('en-US', { hour12: false, timeZone: 'Europe/London' }));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);

    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);

    return () => {
      clearInterval(interval);
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return (
    <header
      className={`fixed top-0 left-0 w-full z-40 px-6 sm:px-12 py-6 transition-all duration-500 ${
        scrolled ? 'bg-black/60 backdrop-blur-md py-4 border-b border-white/5' : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Monogram & Title */}
        <a href="#hero" className="flex items-center gap-3 group" data-cursor="INDEX">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-500 via-cyan-400 to-white flex items-center justify-center font-bold text-black text-sm tracking-tighter shadow-[0_0_20px_rgba(99,102,241,0.5)] transition-transform duration-300 group-hover:scale-105">
            A
          </div>
          <div className="flex flex-col">
            <span className="font-mono text-sm tracking-[0.25em] text-white uppercase font-semibold">
              ATELIER NOCTURNE
            </span>
            <span className="font-mono text-[9px] text-zinc-400 tracking-wider">
              CREATIVE ENGINEERING &reg;
            </span>
          </div>
        </a>

        {/* Desktop Nav Links */}
        <nav className="hidden md:flex items-center gap-8 text-xs font-mono tracking-widest text-zinc-400 uppercase">
          <a
            href="#manifesto"
            className="hover:text-white transition-colors duration-200"
            data-cursor="READ"
          >
            Manifesto
          </a>
          <a
            href="#showcase"
            className="hover:text-white transition-colors duration-200"
            data-cursor="WORK"
          >
            Works [04]
          </a>
          <a
            href="#scrubber"
            className="hover:text-white transition-colors duration-200"
            data-cursor="CINEMA"
          >
            Film Reel
          </a>
          <button
            onClick={onOpenStudio}
            className="text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1.5 font-bold"
            data-cursor="AI GEN"
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            AI Video Lab
          </button>
        </nav>

        {/* Right HUD info & CTA */}
        <div className="hidden lg:flex items-center gap-6">
          <div className="flex items-center gap-2 font-mono text-[11px] text-zinc-400 border-l border-white/10 pl-6">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span>LON {time || '12:00:00'}</span>
          </div>

          <button
            onClick={onOpenReel}
            className="glass-panel px-5 py-2 rounded-full text-xs font-mono uppercase tracking-wider text-white hover:border-cyan-400/60 hover:text-cyan-400 transition-all duration-300 flex items-center gap-2 group"
            data-cursor="PLAY"
          >
            <span>Showreel</span>
            <ArrowUpRight className="w-3.5 h-3.5 transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
          </button>
        </div>

        {/* Mobile menu button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden text-white p-2"
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden glass-panel mt-4 p-6 rounded-2xl flex flex-col gap-4 font-mono text-sm uppercase tracking-wider text-zinc-300">
          <a href="#manifesto" onClick={() => setMobileMenuOpen(false)}>Manifesto</a>
          <a href="#showcase" onClick={() => setMobileMenuOpen(false)}>Works</a>
          <a href="#scrubber" onClick={() => setMobileMenuOpen(false)}>Film Reel</a>
          <button
            onClick={() => {
              setMobileMenuOpen(false);
              onOpenStudio?.();
            }}
            className="text-left text-cyan-400 flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" /> AI Video Lab
          </button>
          <button
            onClick={() => {
              setMobileMenuOpen(false);
              onOpenReel?.();
            }}
            className="text-left text-indigo-400 flex items-center gap-2"
          >
            Watch Showreel <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </header>
  );
}
