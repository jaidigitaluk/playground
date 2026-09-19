'use client';

import React, { useEffect, useRef, useState } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/dist/ScrollTrigger';
import { ArrowUpRight, ExternalLink, Play, Sparkles } from 'lucide-react';

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

interface Project {
  id: string;
  title: string;
  category: string;
  year: string;
  awards: string[];
  description: string;
  videoUrl: string;
  poster: string;
  accent: string;
}

const PROJECTS: Project[] = [
  {
    id: '01',
    title: 'CHRONO OBSIDIAN',
    category: 'Haute Horlogerie & Spatial Web',
    year: '2026',
    awards: ['SOTD', 'FWA of the Day', 'Dev Award'],
    description: 'Interactive exploded 3D tour of a 48-jewel tourbillon timepiece featuring real-time chromatic aberration and gold leaf shaders.',
    videoUrl: 'https://assets.mixkit.co/videos/preview/mixkit-abstract-laser-lights-background-40713-large.mp4',
    poster: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=1200&auto=format&fit=crop',
    accent: 'from-amber-500/20 to-orange-500/10',
  },
  {
    id: '02',
    title: 'NEURA KINETICS',
    category: 'Autonomous Electric Hypercar',
    year: '2026',
    awards: ['Site of the Month Nominee', 'CSSDA WOTD'],
    description: 'High-speed aerodynamic wind tunnel simulation with WebGL particle streams and scroll-scrubbed 4K cinematic road footage.',
    videoUrl: 'https://assets.mixkit.co/videos/preview/mixkit-moving-through-a-futuristic-tunnel-with-neon-lights-42416-large.mp4',
    poster: 'https://images.unsplash.com/photo-1617814076367-b759c7d7e738?q=80&w=1200&auto=format&fit=crop',
    accent: 'from-cyan-500/20 to-blue-500/10',
  },
  {
    id: '03',
    title: 'AETHER BIOTECH',
    category: 'Molecular Genomics & AI',
    year: '2025',
    awards: ['FWA of the Day', 'Webby Winner'],
    description: 'Procedural DNA folding canvas rendered in GLSL raymarching with live audio-reactive harmonic frequencies.',
    videoUrl: 'https://assets.mixkit.co/videos/preview/mixkit-spiral-of-colored-liquid-threads-41480-large.mp4',
    poster: 'https://images.unsplash.com/photo-1507413245164-6160d8298b31?q=80&w=1200&auto=format&fit=crop',
    accent: 'from-fuchsia-500/20 to-purple-500/10',
  },
  {
    id: '04',
    title: 'SYNTHESIS SOUND',
    category: 'Spatial Audio Metaverse',
    year: '2025',
    awards: ['Awwwards SOTD', 'Cannes Gold Lion'],
    description: 'Next-gen audio playground with 3D binaural sound field mapping and AI-generated dynamic visualizer loops.',
    videoUrl: 'https://assets.mixkit.co/videos/preview/mixkit-virtual-reality-headset-in-a-neon-room-42867-large.mp4',
    poster: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?q=80&w=1200&auto=format&fit=crop',
    accent: 'from-emerald-500/20 to-teal-500/10',
  },
];

export default function ShowcaseGallery({ onSelectProject }: { onSelectProject?: (project: Project) => void }) {
  const sectionRef = useRef<HTMLDivElement>(null);
  const scrollWrapperRef = useRef<HTMLDivElement>(null);
  const [activeVideo, setActiveVideo] = useState<string | null>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const scrollWrapper = scrollWrapperRef.current;
      if (!scrollWrapper) return;

      const totalWidth = scrollWrapper.scrollWidth - window.innerWidth;

      gsap.to(scrollWrapper, {
        x: () => -totalWidth,
        ease: 'none',
        scrollTrigger: {
          trigger: sectionRef.current,
          start: 'top top',
          end: () => `+=${totalWidth}`,
          pin: true,
          scrub: 1,
          invalidateOnRefresh: true,
        },
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={sectionRef} id="showcase" className="relative overflow-hidden bg-[#08080a] z-10 pointer-events-auto">
      {/* Top Section Tag */}
      <div className="absolute top-8 left-6 sm:left-12 z-20 flex items-center gap-3 font-mono text-xs text-cyan-400 tracking-[0.3em] uppercase">
        <span className="w-8 h-[1px] bg-cyan-400" />
        <span>[02] SELECTED MONUMENTS & MASTERPIECES</span>
      </div>

      <div className="absolute top-8 right-6 sm:right-12 z-20 font-mono text-xs text-zinc-500 tracking-widest uppercase hidden md:block">
        PINNED HORIZONTAL VIRTUAL TRACK &bull; DRAG OR SCROLL
      </div>

      {/* Horizontal Sliding Strip */}
      <div
        ref={scrollWrapperRef}
        className="flex items-center h-screen pl-6 sm:pl-12 pr-24 gap-8 sm:gap-12"
      >
        {/* Intro Card */}
        <div className="w-[85vw] sm:w-[450px] shrink-0 flex flex-col justify-center">
          <span className="text-6xl sm:text-7xl font-bold tracking-tighter text-zinc-600 font-mono">
            04 / 04
          </span>
          <h3 className="mt-4 text-3xl sm:text-4xl font-light text-white tracking-tight leading-snug">
            Curated works of radical craftsmanship.
          </h3>
          <p className="mt-4 text-xs sm:text-sm text-zinc-400 font-light leading-relaxed">
            Every production is constructed with custom WebGL shaders, low-latency video streaming, and fluid physics simulation.
          </p>
          <div className="mt-8 flex items-center gap-3 text-xs font-mono text-cyan-400 tracking-wider">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>SCROLL HORIZONTALLY TO INSPECT</span>
          </div>
        </div>

        {/* Project Cards */}
        {PROJECTS.map((project) => (
          <div
            key={project.id}
            className="w-[85vw] sm:w-[580px] h-[75vh] shrink-0 glass-panel rounded-3xl p-6 sm:p-8 flex flex-col justify-between relative group overflow-hidden border border-white/10 hover:border-cyan-500/50 transition-all duration-500"
            data-cursor="EXPAND"
            onClick={() => onSelectProject?.(project)}
          >
            {/* Background Gradient Tint */}
            <div className={`absolute inset-0 bg-gradient-to-br ${project.accent} opacity-40 group-hover:opacity-70 transition-opacity duration-500 pointer-events-none`} />

            {/* Video / Poster Background */}
            <div className="absolute inset-0 z-0 overflow-hidden">
              <video
                src={project.videoUrl}
                poster={project.poster}
                autoPlay
                loop
                muted
                playsInline
                className="w-full h-full object-cover scale-100 group-hover:scale-105 transition-transform duration-700 opacity-60 group-hover:opacity-90"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />
            </div>

            {/* Top Card HUD */}
            <div className="relative z-10 flex items-center justify-between">
              <span className="font-mono text-sm tracking-widest text-cyan-400 font-semibold">
                [{project.id}]
              </span>

              <div className="flex flex-wrap items-center gap-1.5">
                {project.awards.map((award, i) => (
                  <span
                    key={i}
                    className="glass-panel px-2.5 py-1 rounded-full text-[10px] font-mono tracking-wider text-amber-300 border border-amber-400/30"
                  >
                    &bull; {award}
                  </span>
                ))}
              </div>
            </div>

            {/* Bottom Card Content */}
            <div className="relative z-10">
              <div className="flex items-center gap-2 font-mono text-[11px] text-zinc-400 tracking-wider uppercase mb-1">
                <span>{project.category}</span>
                <span>&bull;</span>
                <span>{project.year}</span>
              </div>

              <h4 className="text-2xl sm:text-3xl font-bold tracking-tight text-white group-hover:text-cyan-300 transition-colors duration-300">
                {project.title}
              </h4>

              <p className="mt-2 text-xs sm:text-sm text-zinc-300 line-clamp-2 font-light leading-relaxed">
                {project.description}
              </p>

              <div className="mt-5 flex items-center justify-between pt-4 border-t border-white/10">
                <span className="text-xs font-mono uppercase tracking-widest text-zinc-400 flex items-center gap-1.5 group-hover:text-white transition-colors">
                  <Play className="w-3 h-3 text-cyan-400 fill-cyan-400" />
                  Experience Live Demo
                </span>
                <div className="w-9 h-9 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center text-white group-hover:bg-cyan-400 group-hover:text-black transition-all duration-300">
                  <ArrowUpRight className="w-4 h-4" />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
