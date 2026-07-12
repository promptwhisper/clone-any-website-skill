---
name: clone-any-website
description: Rebuild public websites as clean, maintainable local projects with disciplined visual, interaction, and media fidelity. Use when the user asks to clone, replicate, reproduce, port, or study a public website, including video-led landing pages, MP4/WebM or HLS experiences, scroll-scrubbed and masked video, Three.js/WebGL/R3F scenes, Pixi.js or Canvas2D toys, animated product pages, and phrases such as "复刻这个网站", "clone this site", "pixel-perfect copy", "rebuild this page", or "rewrite this screen toy". Covers stack triage, browser reconnaissance, licensed asset mirroring, deterministic media-state capture, client-bundle analysis as a behavioral reference, clean-room implementation, responsive QA, and deployment checks.
---

# Clone Any Website

Reproduce the observable behavior and rendered experience of a public website in
a fresh project. Treat the running site as the visual specification and
client-delivered code as a read-only behavioral reference. Implement the result
as clean source code rather than redistributing the original application.

## Boundaries

Before implementation:

1. Confirm the target is public and does not require authentication, payment,
   invitation, or bypassing an access control.
2. Never collect or reproduce private data, secrets, user content, analytics
   identifiers, API keys, or server-only behavior.
3. Do not ship the target's compiled JavaScript, source maps, or proprietary
   source code. Extract observable behavior, constants, public interfaces, and
   asset relationships, then reimplement them.
4. Mirror only public runtime assets the user is authorized to reuse. Record
   their source and keep runtime requests local.
5. Do not represent the clone as official or affiliated with the original
   creator.

## Core Rules

- Read the original before choosing a stack.
- Match observable pixels and behavior, not internal architecture.
- Decide exact versus approximate per subsystem and record the decision.
- Separate the fidelity path from resilience improvements that the target does
  not visibly demonstrate.
- Extract names and constants; do not guess them.
- Change one high-impact delta at a time, capture again, and compare.
- Freeze viewport, interaction, and media time before calling a comparison
  pixel-accurate.
- Keep the original host out of the final runtime network log.
- Preserve the existing repository's conventions when extending a project.

## Workflow

### 1. Triage

Use the available browser-control skill or tool and read its instructions before
driving the browser. Capture enough evidence to classify the target:

- page screenshot at desktop size;
- script and stylesheet URLs;
- DOM text volume and visible interactive controls;
- canvas count, canvas dimensions, and WebGL availability;
- video count, source topology, current source, playback state, intrinsic size,
  crop, masks, and HLS/MSE network clues;
- renderer or library clues from script names and runtime objects;
- mobile behavior at approximately 390 x 844.

Choose the smallest appropriate stack:

| Target | Preferred stack |
| --- | --- |
| Three.js or complex 3D scene | Existing stack, or React + TypeScript + R3F |
| Pixi.js sprite game | Vite + TypeScript + matching Pixi major |
| Canvas2D animation | Vite + TypeScript |
| Video-led DOM or product page | Existing stack, native video, and HLS only when observed |
| DOM-heavy product page | Existing stack, or React + TypeScript + CSS |
| Mostly text | Use a text extraction workflow instead |

Match the original library's major version when behavior depends on it.

Read [references/recon-and-assets.md](references/recon-and-assets.md) before
capturing a complex site or handling nonstandard assets.
Read [references/video-first.md](references/video-first.md) when video controls
composition, interaction, responsive behavior, or the comparison timeline.

### 2. Establish a Baseline

Inspect the destination repository before editing. If no project exists:

1. Scaffold the selected stack.
2. Add lint, typecheck, and production-build commands.
3. Run the untouched scaffold once.
4. Commit or otherwise record the baseline when the user wants version history.

Create `docs/research/` in the target project when the work is substantial.
Record:

- page topology and responsive states;
- asset inventory and source paths;
- media topology, crop, clock owner, and fixed comparison times;
- visual tokens and sampled output colors;
- interaction states and thresholds;
- extracted constants;
- exact-versus-approximate decisions.

Keep downloaded reference bundles out of the final shipped application and out
of Git. Use them only as temporary research inputs.

### 3. Reconstruct the Specification

Use browser observations first. Use client-delivered bundles only to resolve
unknown behavior, constants, asset paths, shaders, layout formulas, and state
transitions.

Inspect before beautifying. Read an unminified bundle directly; use targeted
search and bounded slicing for a large minified bundle.

Extract by subsystem:

- renderer, color space, tone mapping, exposure, DPR, shadows;
- scene units, camera, lights, background or sky;
- layout formulas and responsive gates;
- video sources and variants, player lifecycle, crop/compositing, and mapping
  from time, scroll, pointer, or state to the presented frame;
- postprocessing and material parameters;
- interactions, thresholds, easing, timing, and audio cues;
- loader task counts and mobile performance branches.

Do not paste large blocks from the source. Re-express behavior in clean code.
Read [references/bundle-analysis.md](references/bundle-analysis.md) for the
detailed extraction checklist.

### 4. Implement by Visual Impact

Implement in this order unless the target suggests otherwise:

1. viewport, page composition, background, and layer stack;
2. primary canvas or media surface, including camera/framing or video crop;
3. global color management, lighting, overlays, and postprocessing;
4. primary geometry, imagery, typography, and materials;
5. main animation, media timeline, and character or component state;
6. physics or spatial interaction;
7. pointer, keyboard, touch, and accessibility behavior;
8. audio, loading/error states, secondary props, particles, and polish.

For each iteration:

1. Run lint, typecheck, and build.
2. Capture the same viewport and state on original and clone.
3. Identify the single highest-impact visible or behavioral delta.
4. Fix it.
5. Capture again.

For 3D work, read [references/three-r3f.md](references/three-r3f.md).
For Pixi.js or Canvas2D work, read
[references/pixi-canvas.md](references/pixi-canvas.md).
For video-led work, implement media geometry, crop, compositing, and clock
ownership before secondary polish.

### 5. Validate

Validate at minimum:

- desktop at 1440 x 900;
- mobile at 390 x 844;
- the primary interaction after any click-to-start gate;
- hover, drag, click, keyboard, and touch paths that exist;
- loading, empty, error, reduced-performance, and muted states;
- console errors and network failures;
- zero runtime requests to the original host;
- frame-aligned captures at fixed media times, scroll, pointer, and playback
  state for every video-led surface;
- nonblank canvas pixels and stable framing for WebGL scenes;
- lint, typecheck, tests, and production build;
- production base paths when deploying below a subpath.

Read [references/qa-and-gotchas.md](references/qa-and-gotchas.md) before the
final screenshot and deployment pass.

### 6. Hand Off

Leave the target project with:

- maintainable source code and only required dependencies;
- an asset source inventory;
- media evidence, fixed capture states, and retained comparison metrics for
  video-led work;
- reproducible asset acquisition;
- run, check, build, and deployment instructions;
- an attribution link when required by license or requested by the user;
- a clear disclaimer when the project is an unofficial study;
- no credentials, research bundles, browser profiles, or unrelated template
  files.

State what is exact, what is approximate, what was not verified, and any
remaining licensing constraints.
