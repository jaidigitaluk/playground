'use client';

import React from 'react';
import { X, ExternalLink, Award, Play } from 'lucide-react';

interface Project {
  id: string;
  title: string;
  category: string;
  year: string;
  awards: string[];
  description: string;
  videoUrl: string;
  poster: string;
}

interface ProjectDetailModalProps {
  project: Project | null;
  onClose: () => void;
}

export default function ProjectDetailModal({ project, onClose }: ProjectDetailModalProps) {
  if (!project) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-8 bg-black/85 backdrop-blur-xl animate-in fade-in duration-300">
      <div className="relative w-full max-w-4xl glass-panel rounded-3xl overflow-hidden border border-cyan-500/30 p-6 sm:p-10 shadow-2xl">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 w-10 h-10 rounded-full glass-panel flex items-center justify-center text-zinc-400 hover:text-white hover:border-white/40 transition-colors z-20"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Video Preview */}
        <div className="relative aspect-video rounded-2xl overflow-hidden border border-white/10 mb-8">
          <video
            src={project.videoUrl}
            poster={project.poster}
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-cover"
          />
          <div className="absolute top-4 left-4 glass-panel px-3 py-1 rounded-full text-xs font-mono text-cyan-300 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span>INTERACTIVE DEMO REEL</span>
          </div>
        </div>

        {/* Metadata & Title */}
        <div className="flex items-center gap-3 font-mono text-xs text-zinc-400 uppercase mb-2">
          <span>{project.category}</span>
          <span>&bull;</span>
          <span>{project.year}</span>
        </div>

        <h3 className="text-3xl sm:text-4xl font-bold tracking-tight text-white mb-4">
          {project.title}
        </h3>

        <p className="text-sm sm:text-base text-zinc-300 font-light leading-relaxed mb-6">
          {project.description}
        </p>

        {/* Award Badges */}
        <div className="flex flex-wrap items-center gap-2 mb-8">
          {project.awards.map((award, i) => (
            <div
              key={i}
              className="glass-panel px-3 py-1 rounded-full text-xs font-mono text-amber-300 border border-amber-400/30 flex items-center gap-1.5"
            >
              <Award className="w-3.5 h-3.5" />
              <span>{award}</span>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-4 pt-6 border-t border-white/10">
          <button
            onClick={onClose}
            className="px-6 py-3 rounded-full bg-white text-black font-semibold text-xs tracking-wider uppercase hover:bg-zinc-200 transition-colors"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
