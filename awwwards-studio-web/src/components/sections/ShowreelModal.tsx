'use client';

import React from 'react';
import { X, Maximize2 } from 'lucide-react';

interface ShowreelModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ShowreelModal({ isOpen, onClose }: ShowreelModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8 bg-black/90 backdrop-blur-2xl animate-in fade-in duration-300">
      <div className="relative w-full max-w-6xl aspect-video glass-panel rounded-3xl overflow-hidden border border-white/20 shadow-[0_0_100px_rgba(0,0,0,0.9)] flex flex-col">
        {/* Top Bar */}
        <div className="absolute top-4 left-6 right-6 z-20 flex items-center justify-between pointer-events-auto">
          <div className="glass-panel px-4 py-1.5 rounded-full font-mono text-xs text-zinc-300 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <span>4K CINEMATIC REEL &bull; 60 FPS HDR</span>
          </div>

          <button
            onClick={onClose}
            className="w-10 h-10 rounded-full glass-panel flex items-center justify-center text-white hover:text-cyan-400 hover:border-cyan-400/60 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Video Player */}
        <div className="w-full h-full relative">
          <video
            src="https://assets.mixkit.co/videos/preview/mixkit-cyberpunk-city-street-with-neon-lights-42866-large.mp4"
            autoPlay
            controls
            playsInline
            className="w-full h-full object-cover"
          />
        </div>
      </div>
    </div>
  );
}
