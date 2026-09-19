# Implementation & Architecture Ledger: Atelier Nocturne (Awwwards Showcase)

## 🏛️ Executive Objective
Build an award-winning digital flagship experience combining:
1. **Haute Couture / High-Tech Creative Studio Aesthetics**: Dark luxury styling, fluid clamp typography, noise grain, glassmorphic HUD panels.
2. **Interactive 3D WebGL Spatial Experience**: React Three Fiber (R3F) + Drei dynamic Torus Knot artifact with liquid distortion shaders, orbital quantum rings, and celestial particle field reacting to cursor physics and scroll progression.
3. **Cinematic Storytelling & GSAP Scroll Choreography**: Lenis smooth momentum inertia scrolling, word-by-word scroll highlights, pinned horizontal showcase gallery, and 4K scroll-synchronized video scrubber with SMPTE timecode.
4. **Generative AI Video Studio Pipeline**: Multi-model video studio interface (Luma Dream Machine Ray 2, Kling 1.5 HD, Wan 2.1 Fal.ai, Runway Gen-3) with automated prompting, real Fal.ai API connector (`/api/generate-video`), and high-res fallback preview.
5. **Procedural Web Audio Synthesizer**: Subtle harmonic drone and reactive acoustic feedback ticks built natively on the Web Audio API with visualizer and mute toggle.

---

## 🚦 Roadmap & Milestones
- [x] **Phase 1: Environment & Scaffolding**:
  - Isolated sandbox `awwwards-studio-web` configured with Next.js 14, React Three Fiber, GSAP, Lenis, and Tailwind CSS.
  - Python virtual environment with `requests`, `python-dotenv`, and `rich`.
  - Secret protection configured (`.gitignore`, `.env.example`, `_system/git_guard.py`).
- [x] **Phase 2: Health & Smoke Testing**:
  - `01_verify_auth.py` checks Node, Python, build artifacts, and video API credentials.
  - `npm run build` passes with zero lint or compilation errors.
- [x] **Phase 3: Core Interactive Modules**:
  - `WebGLCanvas.tsx` + `ArtifactModel.tsx` + `ParticleField.tsx` (R3F + Drei).
  - `LenisProvider.tsx` (Lenis + GSAP ScrollTrigger sync).
  - `AudioController.tsx` (Web Audio API synthesis & equalizer).
  - `CustomCursor.tsx` (Fluid magnetic cursor with difference blend).
  - `Navbar.tsx` (Haute glass bar with live London clock & triggers).
  - `HeroSection.tsx` (GSAP kinetic text reveals & award citations).
  - `ManifestoSection.tsx` (Word-by-word scroll highlighting & spec HUD).
  - `ShowcaseGallery.tsx` (Pinned horizontal virtual track with video cards).
  - `VideoScrubberSection.tsx` (Scroll-controlled 4K cinema scrubbing with SMPTE timecode).
  - `AwardsMetricsSection.tsx` (Rolling stats and official registry shelf).
  - `GenerativeVideoStudio.tsx` (In-app AI video generation studio with preset prompts & download).
  - `ShowreelModal.tsx` & `ProjectDetailModal.tsx` (Full-screen cinema modals).
- [ ] **Phase 4: Live Custom Production & Video Rendering**:
  - Connect real `FAL_KEY` in `.env` to execute live diffusion jobs directly on cloud GPUs.
  - Add client-specific 3D assets (`.gltf` / `.spline` / `.usdz`) into `/public/models`.

---

## 🛠️ Tech Stack & Dependencies
| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | Next.js 14 (App Router) | High-performance React SSR & dynamic API routes |
| **Smooth Momentum** | Lenis (`lenis`) | Butter-smooth scroll physics synced to GSAP ticker |
| **Animation Engine** | GSAP 3.12 + ScrollTrigger | Choreography, pin triggers, horizontal tracks, text reveals |
| **3D & WebGL** | Three.js + React Three Fiber + Drei | 3D artifact, liquid distortion shaders, particle field |
| **Styling** | Tailwind CSS + PostCSS | Obsidian dark-mode palette, glow utilities, glassmorphism |
| **Audio Engine** | Web Audio API | Procedural sound design with zero external MP3 assets |
| **Video Generation** | Fal.ai / Luma / Kling / Wan 2.1 | Programmatic AI video generation pipeline |
