'use client';

import React, { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/dist/ScrollTrigger';
import { Film, Play, Pause, RotateCcw, Volume2, Sparkles } from 'lucide-react';

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

export default function VideoScrubberSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const progressLineRef = useRef<HTMLDivElement>(null);
  const [scrollPct, setScrollPct] = useState(0);
  const [activeAct, setActiveAct] = useState('ACT I: THE SPATIAL AWAKENING');
  const [timecode, setTimecode] = useState('00:00:00');

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    // Ensure video metadata is loaded
    const onLoadedMetadata = () => {
      video.pause();
    };
    video.addEventListener('loadedmetadata', onLoadedMetadata);

    const ctx = gsap.context(() => {
      ScrollTrigger.create({
        trigger: containerRef.current,
        start: 'top top',
        end: '+=250%',
        pin: true,
        scrub: 0.3,
        onUpdate: (self) => {
          const p = self.progress;
          setScrollPct(Math.round(p * 100));

          if (video.duration) {
            const targetTime = p * video.duration;
            video.currentTime = targetTime;

            const mins = Math.floor(targetTime / 60);
            const secs = Math.floor(targetTime % 60);
            const frames = Math.floor((targetTime % 1) * 30);
            setTimecode(
              `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}:${String(frames).padStart(2, '0')}`
            );
          }

          if (p < 0.33) {
            setActiveAct('ACT I: THE SPATIAL AWAKENING');
          } else if (p < 0.66) {
            setActiveAct('ACT II: KINETIC REFRACTION & GLSL');
          } else {
            setActiveAct('ACT III: SYNTHETIC TRANSCENDENCE');
          }

          if (progressLineRef.current) {
            progressLineRef.current.style.width = `${p * 100}%`;
          }
        },
      });
    }, containerRef);

    return () => {
      video.removeEventListener('loadedmetadata', onLoadedMetadata);
      ctx.revert();
    };
  }, []);

  return (
    <section
      id="scrubber"
      ref={containerRef}
      className="relative h-screen w-full bg-black overflow-hidden flex flex-col justify-between p-6 sm:p-12 z-20 pointer-events-auto"
    >
      {/* Background High-Fidelity Cinematic Video */}
      <div className="absolute inset-0 z-0">
        <video
          ref={videoRef}
          src="https://assets.mixkit.co/videos/preview/mixkit-cyberpunk-city-street-with-neon-lights-42866-large.mp4"
          playsInline
          muted
          preload="auto"
          className="w-full h-full object-cover filter contrast-125 brightness-90"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-black/60 pointer-events-none" />
        <div className="absolute inset-0 bg-noise pointer-events-none opacity-40" />
      </div>

      {/* Top HUD Display */}
      <div className="relative z-10 max-w-7xl mx-auto w-full flex items-center justify-between">
        <div className="flex items-center gap-3 font-mono text-xs text-cyan-400 tracking-[0.3em] uppercase">
          <Film className="w-4 h-4 text-cyan-400 animate-pulse" />
          <span>[03] SCROLL-SYNCHRONIZED 4K CINEMA SCRUB</span>
        </div>

        <div className="flex items-center gap-4 font-mono text-xs text-zinc-300">
          <span className="glass-panel px-3 py-1 rounded-full text-cyan-300 border-cyan-500/30">
            SMPTE {timecode}
          </span>
          <span className="hidden sm:inline-block glass-panel px-3 py-1 rounded-full text-zinc-400">
            PRORES 4444 XQ
          </span>
        </div>
      </div>

      {/* Center Dynamic Chapter Overlay */}
      <div className="relative z-10 max-w-4xl mx-auto text-center">
        <span className="font-mono text-xs tracking-[0.4em] uppercase text-cyan-400 block mb-2">
          IMMERSIVE DIRECTORS CUT
        </span>
        <h3 className="text-4xl sm:text-6xl md:text-7xl font-bold tracking-tighter uppercase text-white drop-shadow-[0_0_30px_rgba(0,0,0,0.8)] transition-all duration-300">
          {activeAct}
        </h3>
        <p className="mt-4 text-xs sm:text-sm text-zinc-300 font-mono tracking-wider max-w-md mx-auto">
          Rotate mouse wheel or scroll trackpad to step forward and backward through high-speed frame vectors.
        </p>
      </div>

      {/* Bottom Scrubber Timeline Controls */}
      <div className="relative z-10 max-w-7xl mx-auto w-full glass-panel p-4 sm:p-6 rounded-2xl">
        <div className="flex items-center justify-between font-mono text-xs text-zinc-400 mb-3">
          <div className="flex items-center gap-3">
            <span className="text-white font-semibold">{scrollPct}% SCRUBBED</span>
            <span className="text-zinc-600">|</span>
            <span className="text-cyan-400">{activeAct.split(':')[0]}</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-ping" />
            <span className="text-zinc-300 uppercase tracking-widest text-[10px]">REC SCRUB MODE</span>
          </div>
        </div>

        {/* Scrub Bar */}
        <div className="relative w-full h-2.5 bg-white/10 rounded-full overflow-hidden cursor-pointer">
          <div
            ref={progressLineRef}
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-cyan-400 via-indigo-500 to-fuchsia-500 rounded-full transition-all duration-75"
            style={{ width: `${scrollPct}%` }}
          />
        </div>

        {/* Timeline Frame Ticks */}
        <div className="flex justify-between items-center mt-2 px-1 text-[9px] font-mono text-zinc-600">
          <span>00:00</span>
          <span>00:15</span>
          <span>00:30</span>
          <span>00:45</span>
          <span>01:00</span>
          <span>01:15</span>
          <span>01:30</span>
        </div>
      </div>
    </section>
  );
}
