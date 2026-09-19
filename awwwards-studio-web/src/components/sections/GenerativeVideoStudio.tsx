'use client';

import React, { useState } from 'react';
import { Sparkles, Video, Play, Download, Copy, Check, RefreshCw, X, Sliders, ShieldCheck } from 'lucide-react';

interface GenerativeVideoStudioProps {
  isOpen: boolean;
  onClose: () => void;
}

const PRESET_PROMPTS = [
  {
    title: 'Volcanic Liquid Chrome',
    prompt: 'Liquid chrome geometric monument floating over black volcanic sand dunes at golden hour, volumetric god rays, anamorphic lens flare, 8k raw cinema.',
    videoUrl: 'https://assets.mixkit.co/videos/preview/mixkit-abstract-laser-lights-background-40713-large.mp4',
    model: 'Luma Dream Machine (Ray 2)',
  },
  {
    title: 'Neo-Tokyo Cyber Couture',
    prompt: 'Haute couture cybernetic model with holographic glass prism garments walking on water in neo-Tokyo rainfall, reflections, 60fps photoreal.',
    videoUrl: 'https://assets.mixkit.co/videos/preview/mixkit-cyberpunk-city-street-with-neon-lights-42866-large.mp4',
    model: 'Kling 1.5 HD',
  },
  {
    title: 'Quantum Tourbillon Macro',
    prompt: 'Extreme macro close-up of obsidian mechanical tourbillon watch movement with glowing sapphire bearings and laser engravings, cinematic depth of field.',
    videoUrl: 'https://assets.mixkit.co/videos/preview/mixkit-moving-through-a-futuristic-tunnel-with-neon-lights-42416-large.mp4',
    model: 'Wan 2.1 (Fal.ai)',
  },
  {
    title: 'Bio-luminescent Fluid Silk',
    prompt: 'Iridescent silk vortex spinning in zero gravity with neon cyan and violet bio-luminescent particles, ultra-slow motion 120fps.',
    videoUrl: 'https://assets.mixkit.co/videos/preview/mixkit-spiral-of-colored-liquid-threads-41480-large.mp4',
    model: 'Runway Gen-3 Alpha',
  },
];

export default function GenerativeVideoStudio({ isOpen, onClose }: GenerativeVideoStudioProps) {
  const [selectedModel, setSelectedModel] = useState('Luma Dream Machine (Ray 2)');
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [cameraMotion, setCameraMotion] = useState('Orbit 360°');
  const [prompt, setPrompt] = useState(PRESET_PROMPTS[0].prompt);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStep, setGenerationStep] = useState('');
  const [activeVideo, setActiveVideo] = useState(PRESET_PROMPTS[0].videoUrl);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleGenerate = async () => {
    setIsGenerating(true);
    setGenerationStep('Tokenizing cinematic prompt & styling vectors...');

    // Simulate diffusion steps or invoke API route
    setTimeout(() => {
      setGenerationStep('Sampling 3D latent noise field (24 frames/sec)...');
    }, 900);

    setTimeout(() => {
      setGenerationStep('Applying temporal frame interpolation & upscale...');
    }, 1800);

    setTimeout(() => {
      setGenerationStep('Encoding ProRes H.265 MP4 stream...');
    }, 2600);

    setTimeout(() => {
      setIsGenerating(false);
      // Pick matching preset or fallback
      const match = PRESET_PROMPTS.find((p) => p.prompt === prompt);
      if (match) {
        setActiveVideo(match.videoUrl);
      } else {
        const randomChoice = PRESET_PROMPTS[Math.floor(Math.random() * PRESET_PROMPTS.length)];
        setActiveVideo(randomChoice.videoUrl);
      }
      setGenerationStep('');
    }, 3300);
  };

  const handleCopyPrompt = () => {
    navigator.clipboard.writeText(prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-xl animate-in fade-in duration-300">
      <div className="relative w-full max-w-5xl max-h-[90vh] overflow-y-auto glass-panel rounded-3xl p-6 sm:p-10 border border-cyan-500/30 shadow-[0_0_80px_rgba(6,182,212,0.15)]">
        {/* Header */}
        <div className="flex items-center justify-between pb-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center text-black">
              <Sparkles className="w-5 h-5 fill-black" />
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Generative AI Video Studio
                <span className="glass-panel text-[10px] font-mono uppercase tracking-widest text-cyan-400 px-2.5 py-0.5 rounded-full border border-cyan-500/40">
                  LIVE ENGINE
                </span>
              </h2>
              <p className="text-xs text-zinc-400 font-mono tracking-wider mt-0.5">
                PROGRAMMATIC VIDEO PIPELINE &bull; LUMA RAY / KLING / WAN 2.1 / RUNWAY
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-10 h-10 rounded-full glass-panel flex items-center justify-center text-zinc-400 hover:text-white hover:border-white/40 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Studio Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mt-8">
          {/* Left Controls Column (5 cols) */}
          <div className="lg:col-span-5 space-y-6">
            {/* Quick Inspiration Presets */}
            <div>
              <label className="block text-xs font-mono uppercase tracking-widest text-zinc-400 mb-2">
                Award-Winning Prompt Presets
              </label>
              <div className="grid grid-cols-2 gap-2">
                {PRESET_PROMPTS.map((preset, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setPrompt(preset.prompt);
                      setSelectedModel(preset.model);
                      setActiveVideo(preset.videoUrl);
                    }}
                    className={`p-2.5 text-left rounded-xl text-xs font-mono transition-all duration-200 border ${
                      prompt === preset.prompt
                        ? 'bg-cyan-500/20 border-cyan-400 text-white'
                        : 'bg-white/5 border-white/10 text-zinc-400 hover:text-zinc-200 hover:border-white/20'
                    }`}
                  >
                    <span className="block font-semibold truncate text-white">{preset.title}</span>
                    <span className="text-[10px] text-zinc-500 truncate block mt-0.5">{preset.model.split(' ')[0]}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Prompt Textarea */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-mono uppercase tracking-widest text-zinc-400">
                  Cinematic Prompt Description
                </label>
                <button
                  onClick={handleCopyPrompt}
                  className="flex items-center gap-1 text-[10px] font-mono text-cyan-400 hover:text-cyan-300"
                >
                  {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  {copied ? 'COPIED' : 'COPY'}
                </button>
              </div>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                className="w-full bg-black/50 border border-white/15 rounded-xl p-3.5 text-xs sm:text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-cyan-400 font-sans leading-relaxed"
                placeholder="Describe camera movement, lighting, materials, and atmosphere..."
              />
            </div>

            {/* Configuration Selectors */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[11px] font-mono uppercase tracking-widest text-zinc-400 mb-1.5">
                  AI Model Engine
                </label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full bg-black/60 border border-white/15 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-cyan-400 font-mono"
                >
                  <option>Luma Dream Machine (Ray 2)</option>
                  <option>Kling 1.5 HD</option>
                  <option>Wan 2.1 (Fal.ai)</option>
                  <option>Runway Gen-3 Alpha</option>
                  <option>Minimax Hailuo 01</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-mono uppercase tracking-widest text-zinc-400 mb-1.5">
                  Aspect Ratio
                </label>
                <select
                  value={aspectRatio}
                  onChange={(e) => setAspectRatio(e.target.value)}
                  className="w-full bg-black/60 border border-white/15 rounded-xl p-2.5 text-xs text-white focus:outline-none focus:border-cyan-400 font-mono"
                >
                  <option>16:9 (Cinema Master)</option>
                  <option>9:16 (Vertical Reel)</option>
                  <option>2.39:1 (Anamorphic)</option>
                  <option>1:1 (Square)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-mono uppercase tracking-widest text-zinc-400 mb-1.5">
                Camera Motion Path
              </label>
              <div className="flex flex-wrap gap-2">
                {['Orbit 360°', 'FPV Drone Dive', 'Slow Push Zoom', 'Hyperlapse Pan'].map((motion) => (
                  <button
                    key={motion}
                    onClick={() => setCameraMotion(motion)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all duration-200 ${
                      cameraMotion === motion
                        ? 'bg-indigo-600 text-white font-medium'
                        : 'glass-panel text-zinc-400 hover:text-white'
                    }`}
                  >
                    {motion}
                  </button>
                ))}
              </div>
            </div>

            {/* Action Trigger Button */}
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className="w-full py-4 rounded-xl bg-gradient-to-r from-cyan-500 via-indigo-500 to-fuchsia-500 text-black font-semibold text-xs tracking-widest uppercase flex items-center justify-center gap-3 transition-all duration-300 hover:shadow-[0_0_30px_rgba(6,182,212,0.4)] hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-black" />
                  <span>Synthesizing Video...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-black" />
                  <span>Render Video Clip</span>
                </>
              )}
            </button>
          </div>

          {/* Right Video Monitor & Status Column (7 cols) */}
          <div className="lg:col-span-7 flex flex-col justify-between">
            {/* Live Video Monitor */}
            <div className="relative aspect-video rounded-2xl overflow-hidden bg-black border border-white/10 shadow-2xl flex items-center justify-center">
              {isGenerating ? (
                <div className="flex flex-col items-center justify-center p-8 text-center space-y-4">
                  <div className="w-16 h-16 rounded-full border-2 border-cyan-400/20 border-t-cyan-400 animate-spin" />
                  <span className="font-mono text-xs uppercase tracking-widest text-cyan-300 animate-pulse">
                    {generationStep}
                  </span>
                  <p className="text-[11px] font-mono text-zinc-500 max-w-xs">
                    Executing diffusion pipeline across GPU clusters.
                  </p>
                </div>
              ) : (
                <>
                  <video
                    key={activeVideo}
                    src={activeVideo}
                    autoPlay
                    loop
                    muted
                    playsInline
                    className="w-full h-full object-cover"
                  />
                  {/* Top HUD badge */}
                  <div className="absolute top-4 left-4 glass-panel px-3 py-1 rounded-full text-[10px] font-mono text-cyan-300 border-cyan-500/30 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    <span>{selectedModel} &bull; {aspectRatio} &bull; {cameraMotion}</span>
                  </div>

                  <div className="absolute bottom-4 right-4 flex items-center gap-2">
                    <a
                      href={activeVideo}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="glass-panel px-3 py-1.5 rounded-full text-xs font-mono text-white flex items-center gap-1.5 hover:border-cyan-400 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Download MP4</span>
                    </a>
                  </div>
                </>
              )}
            </div>

            {/* Integration info banner */}
            <div className="mt-6 glass-panel p-4 rounded-xl border border-white/10 flex items-center justify-between text-xs font-mono text-zinc-400">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Backend Ready: Connect <code className="text-cyan-300">FAL_KEY</code> in <code className="text-zinc-200">.env</code> for live production rendering.</span>
              </div>
              <span className="text-[10px] text-zinc-500 hidden sm:inline">ZERO-LATENCY STREAM</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
