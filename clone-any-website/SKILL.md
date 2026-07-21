---
name: clone-any-website
description: Rebuild public websites as clean, maintainable local projects with disciplined visual, interaction, and media fidelity. Use when the user asks to clone, replicate, reproduce, port, or study a public website, including DOM-heavy product and marketing pages, video-led MP4/WebM or HLS experiences, scroll-scrubbed or masked video, Three.js/WebGL/R3F scenes, Pixi.js or Canvas2D toys, and phrases such as "复刻这个网站", "clone this site", "pixel-perfect copy", "rebuild this page", or "rewrite this screen toy". Covers stack triage, browser reconnaissance, interaction-model discovery, licensed asset mirroring, deterministic media-state capture, specification-driven clean-room implementation, responsive visual QA, and deployment checks.
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
   identifiers, API keys, server-only implementation, or live transactional
   behavior. When an in-scope public state depends on an API, reproduce the
   observed state with disclosed local fixtures unless the user separately
   authorizes a backend integration.
3. Do not ship the target's compiled JavaScript, source maps, or proprietary
   source code. Extract observable behavior, constants, public interfaces, and
   asset relationships, then reimplement them.
4. Treat public accessibility and reuse permission as separate questions.
   Mirror only required assets whose license or user authorization permits
   reuse. When permission is unclear, do not mirror by default; substitute,
   omit, or ask the user for evidence or direction. Record the decision and keep
   runtime requests local.
5. Do not represent the clone as official or affiliated with the original
   creator.

## Core Rules

- Read the original before choosing a stack.
- Match observable pixels and behavior, not internal architecture.
- Identify whether each subsystem is driven by scroll, click, hover, pointer,
  keyboard, time, physics, or a combination before implementing it.
- Decide exact versus approximate per subsystem and record the decision.
- Separate the fidelity path from resilience improvements that the target does
  not visibly demonstrate.
- Extract names and constants; do not guess them.
- Give implementation tasks an auditable specification; do not build from a
  screenshot and memory alone.
- Change one high-impact delta at a time, capture again, and compare.
- Freeze viewport, interaction, and media time before calling a comparison
  pixel-accurate.
- Keep the original host out of the final runtime network log.
- Preserve the existing repository's conventions when extending a project.
- Reproduce observed states; do not invent loading, error, accessibility, or
  lower-performance behavior solely to fill a checklist. Mark absent states as
  not applicable with evidence, and keep improvements separate from fidelity
  work.

## Workflow

### 1. Triage

Use the available browser-control skill or tool and read its instructions before
driving the browser. Capture enough evidence to classify the target:

- page screenshot at desktop size;
- capture environment: browser, CSS viewport, zoom, DPR, locale, motion
  preference, and font readiness;
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

Match the original library's major version when behavior depends on it and the
dependency is safe and compatible with the destination. Otherwise use a clean
equivalent and document the deviation and visible risk.

Read [references/recon-and-assets.md](references/recon-and-assets.md) before
capturing a complex site or handling nonstandard assets.
Read [references/video-first.md](references/video-first.md) when video controls
composition, interaction, responsive behavior, or the comparison timeline.

Before choosing a stack, perform a short interaction sweep: scroll before
clicking, then test clicks, hover, keyboard, drag, touch, and time-driven changes
that are present. Do not mistake a scroll-driven section for tabs or a rendered
video for an HTML component.

### 2. Establish a Baseline

Inspect the destination repository before editing. If no project exists:

1. Scaffold the selected stack.
2. Add lint, typecheck, and production-build commands.
3. Run the untouched scaffold once.
4. Commit or otherwise record the baseline when the user wants version history.

Create `docs/research/` in the target project when the work is substantial. Copy
and adapt the relevant files from `assets/research-templates/`; delete sections
that truly do not apply rather than leaving placeholders. Record:

- page topology, subsystem ownership, and responsive states in
  `PAGE_TOPOLOGY.md`;
- interaction triggers and before/after states in `BEHAVIORS.md`;
- asset inventory, source paths, selection variants, and attribution in
  `ASSET_INVENTORY.md`;
- media topology, crop, clock owner, and fixed comparison times;
- visual tokens and sampled output colors;
- extracted constants;
- exact-versus-approximate decisions in `EXACT_APPROXIMATE.md`;
- one specification per independently implemented component or scene subsystem.

Keep downloaded reference bundles out of the final shipped application and out
of Git. Keep raw bundles, source maps, browser profiles, HAR files, and other
bulky or sensitive capture artifacts out of Git by default; commit derived
specifications and reproducible acquisition instructions. Preserve raw evidence
only when the user requests it and its contents are safe and authorized.

### 3. Reconstruct the Specification

Use browser observations first. Use client-delivered bundles only to resolve
unknown behavior, constants, asset paths, shader parameters and pass order,
layout formulas, and state transitions.

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

For every interactive subsystem, explicitly record:

- the interaction model;
- its trigger and threshold;
- default, active, completion, and error states that exist;
- properties or content that change between states;
- transition duration, easing, interruption, and reset behavior;
- differences at desktop, tablet, mobile, reduced-motion, or lower-performance
  branches.

Write a specification before implementation when a subsystem has independent
layout, rendering, or behavior. Use
`assets/research-templates/COMPONENT_SPEC.md` as the starting contract. Split a
spec when it contains several independently testable behaviors or would force
the implementer to infer missing details.

Do not paste large blocks from the source. Re-express behavior in clean code.
Read [references/bundle-analysis.md](references/bundle-analysis.md) for the
detailed extraction checklist.

For DOM-heavy product, marketing, documentation, or application pages, read
[references/dom-pages.md](references/dom-pages.md) before extracting component
specifications or implementing responsive layouts.

### 4. Implement by Visual Impact

Establish shared foundations first: fonts, color tokens, page geometry, asset
paths, icon primitives, global scroll behavior, and renderer settings that
affect multiple subsystems. Verify the baseline still builds before parallel or
component-level work.

Implement in this order unless the target suggests otherwise:

1. viewport, page composition, background, and layer stack;
2. primary canvas or media surface, including camera/framing or video crop;
3. global color management, lighting, overlays, and postprocessing;
4. primary geometry, imagery, typography, and materials;
5. main animation, media timeline, and character or component state;
6. physics or spatial interaction;
7. pointer, keyboard, touch, and accessibility behavior;
8. audio, loading/error states, secondary props, particles, and polish.

For a DOM-heavy page, use the corresponding impact order in
[references/dom-pages.md](references/dom-pages.md). For mixed DOM and canvas
pages, stabilize page geometry and canvas framing together before polishing
either layer.

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
- tablet near 768 px when the layout has an intermediate state;
- mobile at 390 x 844;
- the primary interaction after any click-to-start gate;
- hover, drag, click, keyboard, and touch paths that exist;
- loading, empty, error, reduced-performance, and muted states that exist;
- WebGL-unavailable and context-loss behavior when the target defines it;
- console errors and network failures;
- zero runtime requests to the original host;
- frame-aligned captures at fixed media times, scroll, pointer, and playback
  state for every video-led surface;
- nonblank canvas pixels and stable framing for WebGL scenes;
- lint, typecheck, tests, and production build;
- production base paths when deploying below a subpath.

Maintain a state-and-viewport validation matrix rather than relying on one
full-page screenshot. Treat a state as verified only when the original and clone
were captured with the same viewport, scroll position, input state, cursor or
touch position, and animation time or observable readiness condition.
Use `assets/research-templates/VALIDATION_MATRIX.md` when the target has several
viewports or interaction states. Define project-specific spatial, timing,
animation, and physics tolerances before judging an approximation; do not claim
pixel-perfect results without a recorded comparison method.

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

Report the number of implemented pages, components or scene subsystems,
mirrored assets, and written specifications. State what is exact, what is
approximate, which checks passed or were skipped, what was not verified, and
any remaining licensing constraints.
