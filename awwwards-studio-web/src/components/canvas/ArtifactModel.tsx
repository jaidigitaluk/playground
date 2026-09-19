'use client';

import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Float, MeshDistortMaterial } from '@react-three/drei';
import * as THREE from 'three';

interface ArtifactProps {
  scrollProgress?: number;
}

export default function ArtifactModel({ scrollProgress = 0 }: ArtifactProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const wireframeRef = useRef<THREE.Mesh>(null);
  const ringRef1 = useRef<THREE.Mesh>(null);
  const ringRef2 = useRef<THREE.Mesh>(null);
  const coreRef = useRef<THREE.Mesh>(null);

  useFrame((state, delta) => {
    const time = state.clock.getElapsedTime();
    const pointer = state.pointer;

    // Organic continuous rotation
    if (meshRef.current) {
      meshRef.current.rotation.x = time * 0.2 + pointer.y * 0.4 + scrollProgress * Math.PI * 2;
      meshRef.current.rotation.y = time * 0.25 + pointer.x * 0.5 + scrollProgress * Math.PI * 1.5;

      // Scroll-driven dynamic scaling & position shifting
      const targetScale = 1.6 + Math.sin(scrollProgress * Math.PI) * 0.5;
      meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), delta * 4);
    }

    if (wireframeRef.current) {
      wireframeRef.current.rotation.x = -time * 0.15;
      wireframeRef.current.rotation.y = time * 0.3;
    }

    if (ringRef1.current) {
      ringRef1.current.rotation.x = time * 0.4;
      ringRef1.current.rotation.z = time * 0.2;
    }

    if (ringRef2.current) {
      ringRef2.current.rotation.y = -time * 0.35;
      ringRef2.current.rotation.z = -time * 0.15;
    }

    if (coreRef.current) {
      const pulse = 1 + Math.sin(time * 3) * 0.1;
      coreRef.current.scale.set(pulse, pulse, pulse);
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.8} floatIntensity={1.2}>
      <group position={[0, 0, 0]}>
        {/* Core Torus Knot with liquid iridescent distortion */}
        <mesh ref={meshRef} castShadow receiveShadow>
          <torusKnotGeometry args={[1, 0.35, 128, 32, 2, 3]} />
          <MeshDistortMaterial
            color="#6366f1"
            roughness={0.1}
            metalness={0.9}
            distort={0.35}
            speed={2}
            emissive="#06b6d4"
            emissiveIntensity={0.25}
          />
        </mesh>

        {/* Outer glowing holographic wireframe */}
        <mesh ref={wireframeRef}>
          <torusKnotGeometry args={[1.08, 0.38, 64, 16, 2, 3]} />
          <meshBasicMaterial
            color="#38bdf8"
            wireframe={true}
            transparent={true}
            opacity={0.18}
          />
        </mesh>

        {/* Orbiting Quantum Rings */}
        <mesh ref={ringRef1}>
          <torusGeometry args={[2.2, 0.015, 16, 100]} />
          <meshBasicMaterial color="#a855f7" transparent={true} opacity={0.4} />
        </mesh>

        <mesh ref={ringRef2}>
          <torusGeometry args={[2.5, 0.01, 16, 100]} />
          <meshBasicMaterial color="#06b6d4" transparent={true} opacity={0.3} />
        </mesh>

        {/* Glowing inner singularity */}
        <mesh ref={coreRef}>
          <sphereGeometry args={[0.35, 32, 32]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
      </group>
    </Float>
  );
}
