'use client';

import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ArrowDown, Award, Sparkles, Play } from 'lucide-react';

export default function HeroSection({ onOpenReel, onOpenStudio }: { onOpenReel?: () => void; onOpenStudio?: () => void }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const title1Ref = useRef<HTMLHeadingElement>(null);
  const title2Ref = useRef<HTMLHeadingElement>(null);
  const subheadRef = useRef<HTMLParagraphElement>(null);
  const badgesRef = useRef<HTMLDivElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: 'power4.out', duration: 1.2 } });

      tl.fromTo(
        badgesRef.current,
        { opacity: 0, y: 30 },
        { opacity: 1, y: 0, delay: 0.2 }
      )
        .fromTo(
          title1Ref.current,
          { yPercent: 120, skewY: 7, opacity: 0 },
          { yPercent: 0, skewY: 0, opacity: 1, duration: 1.4 },
          '-=0.8'
        )
        .fromTo(
          title2Ref.current,
          { yPercent: 120, skewY: -7, opacity: 0 },
          { yPercent: 0, skewY: 0, opacity: 1, duration: 1.4 },
          '-=1.1'
        )
        .fromTo(
          subheadRef.current,
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 1 },
          '-=0.8'
        )
        .fromTo(
          ctaRef.current,
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 1 },
          '-=0.8'
        );
    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      id="hero"
      ref={containerRef}
      className="relative min-h-screen flex flex-col justify-between pt-36 pb-12 px-6 sm:px-12 pointer-events-auto"
    >
      {/* Top Award Recognition Bar */}
      <div ref={badgesRef} className="max-w-7xl mx-auto w-full flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3 glass-panel px-4 py-1.5 rounded-full">
          <Award className="w-3.5 h-3.5 text-amber-400" />
          <span className="font-mono text-[11px] tracking-widest uppercase text-zinc-300">
            AWWWARDS SOTD &bull; FWA OF THE MONTH &bull; CANNES LION
          </span>
        </div>

        <div className="hidden sm:flex items-center gap-2 font-mono text-[11px] tracking-widest text-zinc-400 uppercase">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
          <span>AUTONOMOUS SHADER ARCHITECTURE 2026</span>
        </div>
      </div>

      {/* Main Massive Kinetic Typography */}
      <div className="max-w-7xl mx-auto w-full my-auto text-center flex flex-col items-center">
        <div className="overflow-hidden">
          <h1
            ref={title1Ref}
            className="text-6xl sm:text-8xl md:text-9xl lg:text-[11rem] font-bold tracking-tighter uppercase text-transparent bg-clip-text bg-gradient-to-b from-white via-zinc-100 to-zinc-500 leading-none select-none"
          >
            HYPER
          </h1>
        </div>
        <div className="overflow-hidden -mt-2 sm:-mt-6">
          <h1
            ref={title2Ref}
            className="text-6xl sm:text-8xl md:text-9xl lg:text-[11rem] font-bold tracking-tighter uppercase italic text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-indigo-300 to-fuchsia-400 leading-none select-none"
          >
            REALITY
          </h1>
        </div>

        <p
          ref={subheadRef}
          className="mt-8 max-w-xl text-center text-zinc-400 text-sm sm:text-base md:text-lg font-light leading-relaxed tracking-wide"
        >
          We synthesize haute couture aesthetics, real-time WebGL shaders, and generative video systems to build digital monuments that win awards and redefine industries.
        </p>

        {/* Action Button Strip */}
        <div ref={ctaRef} className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <button
            onClick={onOpenStudio}
            className="px-8 py-4 rounded-full bg-gradient-to-r from-cyan-500 to-indigo-600 text-black font-semibold text-xs tracking-widest uppercase flex items-center gap-3 transition-all duration-300 hover:shadow-[0_0_40px_rgba(6,182,212,0.6)] hover:scale-105"
            data-cursor="CREATE"
          >
            <Sparkles className="w-4 h-4 text-black" />
            <span>Launch AI Video Engine</span>
          </button>

          <button
            onClick={onOpenReel}
            className="glass-panel px-8 py-4 rounded-full text-white font-medium text-xs tracking-widest uppercase flex items-center gap-3 transition-all duration-300 hover:border-white/40 hover:bg-white/10"
            data-cursor="PLAY"
          >
            <Play className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400" />
            <span>Watch 4K Showreel</span>
          </button>
        </div>
      </div>

      {/* Bottom Scroll Cue */}
      <div className="max-w-7xl mx-auto w-full flex items-center justify-between text-zinc-500 font-mono text-[11px] tracking-widest uppercase">
        <div className="flex items-center gap-2">
          <span>COORDINATES: 51.5074&deg; N, 0.1278&deg; W</span>
        </div>

        <a
          href="#manifesto"
          className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors duration-200 animate-bounce"
          data-cursor="SCROLL"
        >
          <span>DESCEND INTO THE MACHINE</span>
          <ArrowDown className="w-3.5 h-3.5" />
        </a>

        <div className="hidden sm:block">
          <span>FRAME RATE: 60 FPS &bull; WEBGL 2.0</span>
        </div>
      </div>
    </section>
  );
}
