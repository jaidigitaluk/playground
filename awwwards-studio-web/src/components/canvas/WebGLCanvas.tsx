'use client';

import React, { Suspense, useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { PerspectiveCamera, Environment } from '@react-three/drei';
import ArtifactModel from './ArtifactModel';
import ParticleField from './ParticleField';

export default function WebGLCanvas({ scrollProgress = 0 }: { scrollProgress?: number }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="absolute inset-0 bg-[#08080a] flex items-center justify-center">
        <div className="w-8 h-8 rounded-full border-2 border-cyan-400/20 border-t-cyan-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="fixed inset-0 pointer-events-none z-0">
      <Canvas
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: 'high-performance',
        }}
        dpr={[1, 2]}
      >
        <PerspectiveCamera makeDefault position={[0, 0, 5.5]} fov={45} />
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={1.5} color="#38bdf8" />
        <directionalLight position={[-10, -10, -5]} intensity={0.8} color="#a855f7" />
        <pointLight position={[0, 0, 2]} intensity={2} color="#ffffff" distance={5} />

        <Suspense fallback={null}>
          <ArtifactModel scrollProgress={scrollProgress} />
          <ParticleField count={1000} />
          <Environment preset="night" />
        </Suspense>
      </Canvas>
    </div>
  );
}
