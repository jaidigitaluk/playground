'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Volume2, VolumeX } from 'lucide-react';

export default function AudioController() {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const oscillatorRef = useRef<OscillatorNode | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);
  const filterRef = useRef<BiquadFilterNode | null>(null);

  // Initialize Web Audio Context on first interaction
  const initAudio = () => {
    if (!audioCtxRef.current) {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      audioCtxRef.current = new AudioCtx();
    }
  };

  const startAmbient = () => {
    initAudio();
    if (!audioCtxRef.current) return;

    if (audioCtxRef.current.state === 'suspended') {
      audioCtxRef.current.resume();
    }

    const ctx = audioCtxRef.current;

    // Filtered subtle ambient drone
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(55, ctx.currentTime); // A1 bass drone

    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(140, ctx.currentTime);

    gain.gain.setValueAtTime(0.001, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.04, ctx.currentTime + 3);

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(ctx.destination);

    osc.start();

    oscillatorRef.current = osc;
    gainNodeRef.current = gain;
    filterRef.current = filter;
    setIsPlaying(true);
  };

  const stopAmbient = () => {
    if (gainNodeRef.current && audioCtxRef.current) {
      const ctx = audioCtxRef.current;
      gainNodeRef.current.gain.setValueAtTime(gainNodeRef.current.gain.value, ctx.currentTime);
      gainNodeRef.current.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 1);
      setTimeout(() => {
        oscillatorRef.current?.stop();
        oscillatorRef.current?.disconnect();
        oscillatorRef.current = null;
        setIsPlaying(false);
      }, 1000);
    } else {
      setIsPlaying(false);
    }
  };

  const toggleSound = () => {
    if (isPlaying) {
      stopAmbient();
    } else {
      startAmbient();
    }
  };

  // Play subtle futuristic UI tick sound
  const playTick = useCallback(() => {
    if (!isPlaying || !audioCtxRef.current) return;
    try {
      const ctx = audioCtxRef.current;
      const tickOsc = ctx.createOscillator();
      const tickGain = ctx.createGain();

      tickOsc.type = 'triangle';
      tickOsc.frequency.setValueAtTime(880, ctx.currentTime);
      tickOsc.frequency.exponentialRampToValueAtTime(220, ctx.currentTime + 0.04);

      tickGain.gain.setValueAtTime(0.015, ctx.currentTime);
      tickGain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.04);

      tickOsc.connect(tickGain);
      tickGain.connect(ctx.destination);

      tickOsc.start();
      tickOsc.stop(ctx.currentTime + 0.04);
    } catch {
      // Audio context might be suspended
    }
  }, [isPlaying]);

  useEffect(() => {
    // Attach tick sound to interactive elements
    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement | null;
      if (target && (target.tagName === 'BUTTON' || target.tagName === 'A' || target.closest('button') || target.closest('a'))) {
        playTick();
      }
    };

    window.addEventListener('mouseover', handleMouseOver);
    return () => {
      window.removeEventListener('mouseover', handleMouseOver);
      if (oscillatorRef.current) {
        oscillatorRef.current.stop();
      }
    };
  }, [playTick]);

  return (
    <div className="fixed bottom-8 right-8 z-50 flex items-center gap-3">
      <button
        onClick={toggleSound}
        className="glass-panel px-4 py-2.5 rounded-full flex items-center gap-3 text-xs tracking-widest uppercase transition-all duration-300 hover:border-cyan-500/50 group"
        aria-label="Toggle ambient sound"
      >
        <div className="flex items-center gap-0.5 h-3 w-4">
          <span
            className={`w-0.5 bg-cyan-400 rounded-full transition-all duration-300 ${
              isPlaying ? 'animate-[bounce_0.8s_infinite] h-3' : 'h-1 bg-zinc-500'
            }`}
          />
          <span
            className={`w-0.5 bg-cyan-400 rounded-full transition-all duration-300 ${
              isPlaying ? 'animate-[bounce_1.1s_infinite_0.2s] h-3.5' : 'h-1 bg-zinc-500'
            }`}
          />
          <span
            className={`w-0.5 bg-cyan-400 rounded-full transition-all duration-300 ${
              isPlaying ? 'animate-[bounce_0.9s_infinite_0.4s] h-2.5' : 'h-1 bg-zinc-500'
            }`}
          />
        </div>
        <span className="font-mono text-[11px] text-zinc-300 group-hover:text-cyan-400">
          {isPlaying ? 'SOUND ON' : 'SOUND OFF'}
        </span>
        {isPlaying ? (
          <Volume2 className="w-3.5 h-3.5 text-cyan-400" />
        ) : (
          <VolumeX className="w-3.5 h-3.5 text-zinc-500" />
        )}
      </button>
    </div>
  );
}
