# Reconnaissance and Assets

Read this reference when the target is interactive, canvas-based, asset-heavy,
or unclear after a first screenshot.

## Contents

- Recon checklist
- Asset mirroring and inventory
- Binary formats
- Color sampling

## Recon Checklist

Capture findings into the target project's `docs/research/` folder.

### Page and DOM

- Record the final URL, title, language, viewport, and device scale.
- Freeze browser, zoom, locale, motion preference, consent state, experiment or
  geo variant, and font readiness for repeatable captures.
- Capture visible text, semantic roles, links, forms, and controls.
- Record all script and stylesheet URLs.
- Inspect computed typography, spacing, position, opacity, transforms, and
  z-index for visible UI.
- Identify overlays, modals, click-to-start gates, and pointer-blocking layers.

### Canvas and WebGL

- Count canvas elements and record their CSS and drawing-buffer sizes.
- Check WebGL1 versus WebGL2.
- Record the renderer string when available.
- Inspect canvas attributes for engine clues.
- Observe whether the canvas is blank until a gesture, focus, resize, or asset
  completion event.
- Compare screenshots rather than relying on `canvas.toDataURL()` when
  `preserveDrawingBuffer` is false.

### Interaction

- Enumerate hover, click, drag, wheel, keyboard, touch, and audio-unlock paths.
- Scroll through each region before clicking controls so scroll-driven state is
  not mistaken for tabs or an accordion.
- Classify each region as static, scroll-driven, click-driven, hover-driven,
  pointer-driven, keyboard-driven, time-driven, physics-driven, or mixed.
- Capture each meaningful state at a stable point in its animation.
- Measure click-versus-drag thresholds and timing rather than describing them
  only as "small" or "fast".
- For each transition, capture before and after state, trigger, threshold,
  duration, delay, easing, interruption, and reset behavior.
- Test desktop and mobile independently; do not infer one from the other.
- Test tablet when it has a distinct layout, and probe around suspected
  breakpoints instead of assuming framework defaults.

Record the sweep in `docs/research/BEHAVIORS.md`. Record the ordered sections,
layering, scroll owner, and cross-section dependencies in
`docs/research/PAGE_TOPOLOGY.md` before assigning implementation boundaries.

### Network

- Record every request needed by the primary workflow.
- Group by code, geometry, image, texture, audio, video, font, decoder, worker,
  and API.
- Note content types, sizes, cache behavior, and variant selection.
- Distinguish required assets from speculative or unused URLs.

### DOM Media and Layers

- Enumerate `<img>`, `<picture>`, `<video>`, inline SVG, CSS background images,
  pseudo-elements, masks, and absolutely positioned overlays.
- Record intrinsic dimensions, responsive candidates, crop, object position,
  autoplay, looping, and poster behavior.
- Inspect the full composition tree; do not assume a visual that looks like one
  image is stored as one asset.
- Distinguish rendered animation or video from a UI that should be rebuilt as
  interactive HTML.

## Asset Mirroring

Mirror the public static assets required by the reproduced experience into the
local project. Keep the final runtime independent from the original host.

- Preserve formats, paths, variants, and compression when they affect behavior.
- Download only files used by the implemented experience.
- Do not acquire private, authenticated, paywalled, or user-specific content.
- Record the original URL and creator attribution for each asset group.
- Keep research bundles separate from shipped runtime assets.

## Asset Inventory

Track at least:

- local output path;
- source URL or source package;
- role in the experience;
- state, viewport, or performance variant that selects it;
- original URL and creator attribution;
- checksum when deterministic mirroring matters.
- license and selected compressed/uncompressed variant.

Keep the downloader as the source of truth for mirrored runtime assets. Make it:

- bounded to 4 to 6 concurrent requests;
- idempotent;
- able to skip existing files;
- able to force refresh explicitly;
- strict about HTTP status and expected content type;
- bounded by explicit request timeout, retry and backoff limits, redirect
  policy, and per-file or total-size guardrails;
- explicit about checksum mismatch and partial-file cleanup;
- deterministic about output paths.

## Binary Formats

Prefer standard loaders for GLB, glTF, FBX, HDR, EXR, KTX2, and common audio.

When a file wraps a standard codec in a custom container:

1. Find the client worker or loader that parses the framing.
2. Document only the container structure and attribute map.
3. Reuse the matching standard decoder or the decoder shipped for that public
   asset format.
4. Write a thin clean wrapper around the decoder.
5. Preserve unknown attributes such as `surfaceId`, `elementId`, `batchId`,
   `dist`, skin indices, and skin weights.
6. Validate decoded bounds, index count, attribute count, and rendering.

A common custom Draco framing is either:

- a raw Draco stream whose metadata contains an attribute map; or
- a little-endian JSON length, JSON metadata, then the Draco stream.

Never assume that pattern. Confirm the actual framing.

## Color Sampling

Rendered color may differ from source color because of tone mapping, output
color space, LUTs, grain, blending, and browser compositing. Sample flat regions
from the final screenshot:

```python
from PIL import Image

image = Image.open("original.png").convert("RGB")
red, green, blue = image.getpixel((x, y))
print(f"#{red:02x}{green:02x}{blue:02x}")
```

Use several nearby pixels when compression, antialiasing, or grain is present.
Record both the sampled output and the implementation value that produced it.
