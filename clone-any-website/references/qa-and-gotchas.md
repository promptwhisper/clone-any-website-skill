# QA and Gotchas

Read this reference before final validation or when the clone is close but still
feels wrong.

## Contents

- Comparison loop and required states
- WebGL, animation, and physics gotchas
- Browser, network, build, and deployment checks
- Final report

## Comparison Loop

Use identical viewport, device scale, state, cursor position, and elapsed time.
For graphics-heavy targets, compare in this order:

1. framing and background;
2. global color grade;
3. primary silhouette;
4. lighting and shadows;
5. material response;
6. typography and UI;
7. secondary effects.

Fix one major delta per loop.

For DOM-heavy targets, compare in this order:

1. document flow, section heights, and scroll ownership;
2. fonts, line wrapping, and dominant media crops;
3. grids, spacing, sticky and fixed geometry;
4. controls, borders, shadows, and compositing;
5. responsive reordering and visibility;
6. transitions and micro-interactions.

Maintain a matrix of viewport × interaction state. A full-page screenshot is
necessary for flow but does not verify hover, focus, open, active, error, or
time-dependent states.

Before comparison, record project-specific spatial and timing tolerances plus
masking rules for grain, antialiasing, randomized particles, video frames, or
other nondeterministic pixels. For physics, compare contact timing, trajectory,
settling, and end-state envelopes rather than demanding identical floating-point
simulation across browsers.

For a dynamic WebGL/WebGPU target, capture the same nominal target state at
least three times. Compare those target captures to estimate a self-variance
floor. Then:

- score static and dynamic masks separately;
- keep structural framing and UI gates strict;
- set foliage, weather, particles, physics, and temporal-AA gates above the
  target's own variance;
- report both global and masked metrics;
- never describe a single dynamic frame as zero-diff or pixel-identical.

When the reference includes browser chrome or was captured at a different DPR,
crop to the content viewport first. Resize only after proving the CSS viewport
and aspect ratio match; otherwise resizing can hide a layout error. Use the
comparator's explicit crop and reference-resize options and retain the prepared
dimensions in the report.

## Screenshot Metrics

Use the bundled
[screenshot comparator](../scripts/compare-screenshots.py) for repeatable RGB
metrics, masks, heatmaps, and calibrated CI gates. A run without `--max-*`
options is measurement-only; derive project gates from repeated captures of a
stable target state. For decoded-video capture timing and crop checks, follow
[Video-First Website Reproduction](video-first.md).

Crop arguments use `X Y WIDTH HEIGHT`. For a browser-chrome reference captured
at a different DPR:

```bash
python scripts/compare-screenshots.py reference.png candidate.png \
  --reference-crop 0 174 3840 1756 \
  --resize-reference-to-candidate \
  --pixel-threshold 24 --output heatmap.png
```

## Required States

- initial loading;
- click-to-start or consent gate;
- primary idle state;
- primary active interaction;
- completion or reset;
- muted and unmuted;
- desktop and mobile;
- tablet when it has an intermediate layout;
- reduced-performance branch;
- reduced-motion branch when supported;
- missing-asset or decoder error during development.
- WebGL unavailable or context lost when the target handles it.

Mark an unobserved state `N/A` with evidence; do not add behavior merely to
satisfy this list.

## WebGL and Animation

| Symptom | Likely cause | Check |
| --- | --- | --- |
| Whole frame has wrong color | Tone mapping, exposure, LUT, or color space | Match renderer and pass order first |
| Background is slightly wrong | Postprocessing shifts source hex | Sample the final screenshot |
| Terrain is flat or recolored | Authored UV palette atlas ignored | Use atlas with nearest sRGB sampling |
| Long spike from a character | Skin weights do not sum to one | Normalize after binding |
| Character remains in T-pose | Strict Mode cleanup stopped action | Restart inactive action |
| HUD object is missing | Camera-relative object placed at world origin | Billboard it in the scene |
| Only one sub-object appears | Batched geometry not split | Inspect identifier attributes |
| Edge-on surface disappears | Wrong side or winding | Check `DoubleSide` only where intended |
| Shader fails to compile | MRT, UBO, GLSL version, or engine include dependency | Isolate or approximate |
| Phone overheats | Desktop postprocessing and DPR | Add a low-tier branch |
| Slow first load ends in audio recursion | Per-frame setters queued before sound readiness | Gate audio updates on loaded state |

## Physics

| Symptom | Likely cause | Check |
| --- | --- | --- |
| Object floats | World-unit mismatch | Confirm scale conversion |
| Pieces explode | Impulse or penetration is too large | Reduce impulse and inspect spawn overlap |
| Object tumbles forever | Damping, sleep, or friction mismatch | Tune after first collision |
| Contact feels detached | Collider does not match visible contact area | Inspect both in one debug view |

## Browser Capture

- Keep the tested tab active when heavy animation is throttled in background
  tabs.
- Wait for an observable state, not only an arbitrary delay.
- Trigger click-to-start before judging a splash-screen capture.
- Use the browser screenshot pipeline for WebGL.
- Capture a second frame and compare pixels to prove animation is running.
- Inspect console errors and failed requests after each major state.
- Distinguish retained log history from the current page load or bundle before
  declaring a new runtime error.
- Use the same font readiness, scroll position, focus, cursor or touch position,
  and observable animation state on the original and clone.
- Check for horizontal overflow and layout shift after fonts and responsive
  media finish loading.

## Network

Require:

- no 404 or opaque decoder failure;
- correct MIME types for modules, WASM, audio, and models;
- no runtime request to the original host;
- correct base path under GitHub Pages or another subpath;
- no credential, token, local path, or development host in emitted files.

## Build

Run the repository's own commands. A typical gate is:

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Do not invent a test command when the project has none. Report skipped checks.

## Deployment

- Test the built artifact, not only the dev server.
- Verify one HTML file, one JavaScript chunk, one large model, one WASM decoder,
  one texture, and one audio file from the public URL.
- Open the public URL in a clean navigation and complete the primary flow.
- Confirm deployment status before reporting success.

## Final Report

State:

- public or local URL;
- implemented scope;
- number of pages, components or scene subsystems, specifications, and mirrored
  assets;
- exact and approximate subsystems;
- checks passed, failed, and skipped;
- desktop, tablet when applicable, and mobile verification;
- interaction states verified and not verified;
- remaining visual differences;
- asset licensing or attribution constraints.
