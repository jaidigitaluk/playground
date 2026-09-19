'use client';

import React, { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/dist/ScrollTrigger';
import { Shield, Zap, Layers, Cpu } from 'lucide-react';

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

const MANIFESTO_WORDS = [
  "Standard", "web", "design", "is", "dead.", "We", "do", "not", "build", "static", "templates;",
  "we", "engineer", "living,", "breathing", "digital", "sculptures.", "By", "unifying",
  "real-time", "raymarching,", "procedural", "audio,", "and", "generative", "neural", "video,",
  "every", "interaction", "becomes", "an", "unforgettable", "visceral", "spectacle."
];

export default function ManifestoSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const wordsRef = useRef<(HTMLSpanElement | null)[]>([]);
  const hudRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      // Scrub word opacity sequentially
      gsap.fromTo(
        wordsRef.current,
        { opacity: 0.15, filter: 'blur(4px)', y: 10 },
        {
          opacity: 1,
          filter: 'blur(0px)',
          y: 0,
          stagger: 0.05,
          scrollTrigger: {
            trigger: containerRef.current,
            start: 'top 70%',
            end: 'bottom 50%',
            scrub: 0.5,
          },
        }
      );

      // Parallax float on HUD cards
      gsap.fromTo(
        hudRef.current,
        { y: 80, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          scrollTrigger: {
            trigger: containerRef.current,
            start: 'top 60%',
            end: 'center center',
            scrub: 1,
          },
        }
      );
    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      id="manifesto"
      ref={containerRef}
      className="relative min-h-screen py-32 px-6 sm:px-12 flex flex-col justify-center pointer-events-auto"
    >
      <div className="max-w-6xl mx-auto w-full">
        {/* Section Header Tag */}
        <div className="flex items-center gap-3 font-mono text-xs text-cyan-400 tracking-[0.3em] uppercase mb-12">
          <span className="w-8 h-[1px] bg-cyan-400" />
          <span>[01] THE MANIFESTO & PHILOSOPHY</span>
        </div>

        {/* Word-by-word Scrubbed Text */}
        <h2 className="text-3xl sm:text-5xl md:text-6xl lg:text-7xl font-light tracking-tight leading-[1.2] text-white">
          {MANIFESTO_WORDS.map((word, idx) => (
            <span
              key={idx}
              ref={(el) => { wordsRef.current[idx] = el; }}
              className="inline-block mr-2.5 sm:mr-4 transition-colors"
            >
              {word}
            </span>
          ))}
        </h2>

        {/* HUD Spec Pillars */}
        <div
          ref={hudRef}
          className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-24"
        >
          <div className="glass-panel p-6 rounded-2xl glass-panel-hover" data-cursor="SHADERS">
            <Layers className="w-5 h-5 text-cyan-400 mb-3" />
            <h3 className="font-mono text-xs uppercase tracking-widest text-zinc-200">GLSL Raymarching</h3>
            <p className="mt-2 text-xs text-zinc-400 leading-relaxed">
              Custom volumetric shaders running at locked 60 FPS across desktop and high-end mobile.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl glass-panel-hover" data-cursor="AUDIO">
            <Zap className="w-5 h-5 text-indigo-400 mb-3" />
            <h3 className="font-mono text-xs uppercase tracking-widest text-zinc-200">Bespoke Acoustics</h3>
            <p className="mt-2 text-xs text-zinc-400 leading-relaxed">
              Procedural Web Audio synthesis that resonates with the user's cursor velocity and scroll friction.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl glass-panel-hover" data-cursor="NEURAL">
            <Cpu className="w-5 h-5 text-fuchsia-400 mb-3" />
            <h3 className="font-mono text-xs uppercase tracking-widest text-zinc-200">Neural Video Pipes</h3>
            <p className="mt-2 text-xs text-zinc-400 leading-relaxed">
              Real-time programmatic video rendering and AI video generation for hyper-personalized storytelling.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl glass-panel-hover" data-cursor="AWARDS">
            <Shield className="w-5 h-5 text-amber-400 mb-3" />
            <h3 className="font-mono text-xs uppercase tracking-widest text-zinc-200">Awwwards Grade</h3>
            <p className="mt-2 text-xs text-zinc-400 leading-relaxed">
              Meticulous typography, micro-interactions, and choreography built strictly for podium finishes.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
