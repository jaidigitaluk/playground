'use client';

import React from 'react';
import { Award, Trophy, Star, ShieldCheck, Zap } from 'lucide-react';

const METRICS = [
  { value: '14x', label: 'Awwwards SOTD', sub: 'Site of the Day Honors' },
  { value: '09x', label: 'FWA of the Day', sub: 'Cutting-edge Innovation' },
  { value: '06x', label: 'Cannes Lions', sub: 'Digital Craft & Tech' },
  { value: '99.8%', label: 'Performance Score', sub: 'Lighthouse & 60 FPS' },
];

const HONORS = [
  {
    org: 'AWWWARDS',
    title: 'Site of the Month Finalist',
    project: 'Chrono Obsidian Spatial Tour',
    badge: 'ANNUAL NOMINEE',
  },
  {
    org: 'FWA OF THE DAY',
    title: 'Most Innovative WebGL Shader',
    project: 'Neura Kinetics Hypercar',
    badge: 'JUDGES VOTE',
  },
  {
    org: 'CSS DESIGN AWARDS',
    title: 'Best UI / UX / Innovation',
    project: 'Aether Molecular Genomics',
    badge: 'SPECIAL KUDOS',
  },
];

export default function AwardsMetricsSection() {
  return (
    <section className="relative py-32 px-6 sm:px-12 bg-[#08080a] pointer-events-auto border-t border-white/5">
      <div className="max-w-7xl mx-auto w-full">
        {/* Section Tag */}
        <div className="flex items-center gap-3 font-mono text-xs text-cyan-400 tracking-[0.3em] uppercase mb-16">
          <span className="w-8 h-[1px] bg-cyan-400" />
          <span>[04] PODIUM METRICS & PEDIGREE</span>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8 mb-24">
          {METRICS.map((m, idx) => (
            <div
              key={idx}
              className="glass-panel p-8 rounded-3xl relative overflow-hidden group hover:border-cyan-500/40 transition-all duration-300"
              data-cursor="METRIC"
            >
              <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:opacity-10 transition-opacity">
                <Trophy className="w-32 h-32 text-cyan-400" />
              </div>
              <span className="text-4xl sm:text-6xl font-bold font-mono tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-zinc-200 to-zinc-500">
                {m.value}
              </span>
              <h4 className="mt-3 text-sm sm:text-base font-semibold text-white tracking-wide">
                {m.label}
              </h4>
              <p className="mt-1 text-xs text-zinc-400 font-mono">{m.sub}</p>
            </div>
          ))}
        </div>

        {/* Honor Wall */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {HONORS.map((h, idx) => (
            <div
              key={idx}
              className="glass-panel p-8 rounded-3xl border border-white/10 flex flex-col justify-between hover:border-amber-400/40 transition-all duration-300"
              data-cursor="AWARD"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="font-mono text-xs tracking-widest text-amber-400 uppercase font-semibold">
                    {h.org}
                  </span>
                  <span className="glass-panel text-[9px] font-mono tracking-widest uppercase text-zinc-400 px-2.5 py-0.5 rounded-full border border-white/10">
                    {h.badge}
                  </span>
                </div>
                <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight">
                  {h.title}
                </h3>
                <p className="mt-2 text-xs text-zinc-400 font-mono">
                  Recognized for: <span className="text-zinc-200">{h.project}</span>
                </p>
              </div>

              <div className="mt-8 pt-4 border-t border-white/10 flex items-center gap-2 text-xs font-mono text-zinc-500">
                <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                <span>Verified on Official Registry</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
