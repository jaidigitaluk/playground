'use client';

import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import Navbar from '@/components/sections/Navbar';
import HeroSection from '@/components/sections/HeroSection';
import ManifestoSection from '@/components/sections/ManifestoSection';
import ShowcaseGallery from '@/components/sections/ShowcaseGallery';
import VideoScrubberSection from '@/components/sections/VideoScrubberSection';
import AwardsMetricsSection from '@/components/sections/AwardsMetricsSection';
import InteractiveFooter from '@/components/sections/InteractiveFooter';
import GenerativeVideoStudio from '@/components/sections/GenerativeVideoStudio';
import ShowreelModal from '@/components/sections/ShowreelModal';
import ProjectDetailModal from '@/components/sections/ProjectDetailModal';

// Dynamic import for WebGL Three.js Canvas to prevent SSR issues
const WebGLCanvas = dynamic(() => import('@/components/canvas/WebGLCanvas'), {
  ssr: false,
});

export default function Home() {
  const [scrollProgress, setScrollProgress] = useState(0);
  const [isStudioOpen, setIsStudioOpen] = useState(false);
  const [isShowreelOpen, setIsShowreelOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<any | null>(null);

  useEffect(() => {
    const handleScroll = () => {
      const totalScroll = document.documentElement.scrollHeight - window.innerHeight;
      if (totalScroll > 0) {
        setScrollProgress(window.scrollY / totalScroll);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <main className="relative min-h-screen bg-[#08080a] text-white selection:bg-cyan-500/30">
      {/* 3D WebGL Canvas Layer */}
      <WebGLCanvas scrollProgress={scrollProgress} />

      {/* Navigation */}
      <Navbar
        onOpenReel={() => setIsShowreelOpen(true)}
        onOpenStudio={() => setIsStudioOpen(true)}
      />

      {/* Hero Section */}
      <HeroSection
        onOpenReel={() => setIsShowreelOpen(true)}
        onOpenStudio={() => setIsStudioOpen(true)}
      />

      {/* Manifesto Section */}
      <ManifestoSection />

      {/* Pinned Horizontal Showcase */}
      <ShowcaseGallery onSelectProject={(p) => setSelectedProject(p)} />

      {/* 4K Scroll-driven Video Scrubber */}
      <VideoScrubberSection />

      {/* Podium Metrics & Awards */}
      <AwardsMetricsSection />

      {/* Kinetic Footer */}
      <InteractiveFooter onOpenStudio={() => setIsStudioOpen(true)} />

      {/* Modals & Studios */}
      <GenerativeVideoStudio
        isOpen={isStudioOpen}
        onClose={() => setIsStudioOpen(false)}
      />

      <ShowreelModal
        isOpen={isShowreelOpen}
        onClose={() => setIsShowreelOpen(false)}
      />

      <ProjectDetailModal
        project={selectedProject}
        onClose={() => setSelectedProject(null)}
      />
    </main>
  );
}
