# QA and Gotchas

Read this reference before final validation or when the clone is close but still
feels wrong.

## Comparison Loop

Use identical viewport, device scale, state, cursor position, and elapsed time.
Compare in this order:

1. framing and background;
2. global color grade;
3. primary silhouette;
4. lighting and shadows;
5. material response;
6. typography and UI;
7. secondary effects.

Fix one major delta per loop.

## Required States

- initial loading;
- click-to-start or consent gate;
- primary idle state;
- primary active interaction;
- completion or reset;
- muted and unmuted;
- desktop and mobile;
- reduced-performance branch;
- missing-asset or decoder error during development.

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
- exact and approximate subsystems;
- checks run;
- desktop and mobile verification;
- remaining visual differences;
- asset licensing or attribution constraints.
