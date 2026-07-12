# Video-First Website Reproduction

Read this reference when video is a primary visual surface, interaction state,
scroll timeline, mask source, WebGL texture, or responsive composition element.
Use it for progressive MP4/WebM, native HLS, `hls.js`/MSE playback,
scroll-scrubbed media, hover reveals, synchronized players, and alpha video.

## Table of contents

- A. Classify the video role
- B. Capture the media evidence contract
- C. Reconstruct the time contract
- D. Match crop, masks, and compositing
- E. Mirror assets without changing them accidentally
- F. Implement faithful playback and separate hardening
- G. Reproduce responsive and input behavior
- H. Run deterministic frame-aligned visual QA
- I. Test lifecycle, performance, and failures
- J. Acceptance checklist

## A. Classify the video role

Name each player's role before choosing an implementation:

- **Ambient background**: free-running loop behind semantic DOM.
- **Editorial media**: visible player or full-bleed footage carrying content.
- **Masked reveal**: video exposed through SVG, CSS mask, clip path, text, or a
  pointer trail.
- **Interaction-gated**: play, pause, seek, or reveal follows hover, pointer,
  click, drag, or component state.
- **Scroll-scrubbed**: scroll progress maps to `currentTime` or frame index.
- **Synchronized**: multiple players, canvas layers, or DOM states share a
  clock.
- **Texture source**: video feeds Canvas/WebGL, including stacked RGB/alpha
  video.

Keep a native DOM `<video>` when it can match the rendered result. Add Canvas or
WebGL only when the target visibly depends on shader sampling, custom
compositing, per-pixel interaction, or transformed hit testing. Do not choose a
heavier stack merely because the result feels cinematic.

## B. Capture the media evidence contract

Record a media inventory in `docs/research/` before downloading or coding. For
each player, capture:

- semantic role and containing section;
- `src`, every `<source>`, resolved `currentSrc`, and poster;
- intrinsic `videoWidth`/`videoHeight`, duration, frame rate when observable,
  and whether audio exists;
- `autoplay`, `muted`, `loop`, `playsInline`, `controls`, `preload`,
  `playbackRate`, paused state, and initial `currentTime`;
- element and container rectangles at every tested breakpoint;
- computed `object-fit`, `object-position`, transform, opacity, filter,
  blend mode, border radius, mask, clip path, and z-index;
- loading gate, first visible frame, loop boundary, and error behavior;
- the event or signal that owns playback: time, scroll, pointer, state, or a
  shared timeline.

Use one bounded browser evaluation to inventory players instead of querying
properties one at a time:

```js
[...document.querySelectorAll('video')].map((video, index) => {
  const style = getComputedStyle(video);
  const rect = video.getBoundingClientRect();
  return {
    index,
    src: video.getAttribute('src'),
    sources: [...video.querySelectorAll('source')].map((source) => ({
      src: source.src,
      type: source.type,
      media: source.media,
    })),
    currentSrc: video.currentSrc,
    intrinsic: [video.videoWidth, video.videoHeight],
    duration: video.duration,
    currentTime: video.currentTime,
    playbackRate: video.playbackRate,
    state: {
      paused: video.paused,
      muted: video.muted,
      loop: video.loop,
      readyState: video.readyState,
      networkState: video.networkState,
    },
    attributes: {
      autoplay: video.autoplay,
      playsInline: video.playsInline,
      preload: video.preload,
      poster: video.poster,
    },
    rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
    style: {
      objectFit: style.objectFit,
      objectPosition: style.objectPosition,
      transform: style.transform,
      opacity: style.opacity,
      filter: style.filter,
      mixBlendMode: style.mixBlendMode,
      borderRadius: style.borderRadius,
      clipPath: style.clipPath,
      maskImage: style.maskImage || style.webkitMaskImage,
      zIndex: style.zIndex,
    },
  };
});
```

Treat `blob:` in `currentSrc` as an MSE clue, not the source asset. Inspect the
network log for the master manifest, media playlist, initialization segment,
media segments, selected rendition, audio group, and subtitle group. Record
redirects, response MIME, CORS headers, cache headers, Range support, and query
parameters with expiry semantics.

Keep raw network exports and full signed URLs gitignored. In committed media
inventories, redact query-token values while retaining query-key names, expiry
metadata, hashes, and stable origins and paths needed to reproduce the source
topology.

Stop when the stream is encrypted, authenticated, DRM-protected, user-specific,
or otherwise access-controlled. Public playback does not prove redistribution
rights and never authorizes bypassing a restriction.

## C. Reconstruct the time contract

Classify the clock before matching easing:

```text
free-running time | hover/state gate | scroll progress | shared media clock
                                  ↓
                       normalized progress or seconds
                                  ↓
                 currentTime / play state / mask / DOM / shader
```

Give each visible property one owner. Do not let scroll code, hover handlers,
and a free-running `requestAnimationFrame` loop all write `currentTime`.

For scroll-scrubbed media, record the exact mapping:

- scroll container and start/end offsets;
- clamping, smoothing, snapping, and reversal behavior;
- `progress → seconds` formula;
- seek throttling or frame-sequence strategy;
- mobile-specific ranges and static alternatives.

Capture a presented frame rather than taking a screenshot immediately after
setting `currentTime`:

```js
function waitForMediaEvent(video, eventName, timeoutMs = 5000) {
  return new Promise((resolve, reject) => {
    const cleanup = () => {
      clearTimeout(timeoutId);
      video.removeEventListener(eventName, onEvent);
      video.removeEventListener('error', onError);
    };
    const onEvent = () => {
      cleanup();
      resolve();
    };
    const onError = () => {
      cleanup();
      reject(video.error || new Error(`Media failed before ${eventName}`));
    };
    const timeoutId = setTimeout(() => {
      cleanup();
      reject(new Error(`Timed out waiting for ${eventName}`));
    }, timeoutMs);
    video.addEventListener(eventName, onEvent, { once: true });
    video.addEventListener('error', onError, { once: true });
  });
}

function waitForPresentedFrame(
  video,
  targetTime,
  maxTimestampDelta,
  notBeforePresentationTime,
  timeoutMs = 2000,
) {
  return new Promise((resolve, reject) => {
    let callbackId;
    let settled = false;
    const finish = (error, mediaTime) => {
      if (settled) return;
      settled = true;
      clearTimeout(timeoutId);
      if (callbackId !== undefined &&
          typeof video.cancelVideoFrameCallback === 'function') {
        video.cancelVideoFrameCallback(callbackId);
      }
      if (error) reject(error);
      else resolve(mediaTime);
    };
    const onFrame = (_now, metadata) => {
      if (settled) return;
      const belongsToThisSeek =
        Number.isFinite(metadata.presentationTime) &&
        metadata.presentationTime >= notBeforePresentationTime;
      const matchesTarget =
        Math.abs(metadata.mediaTime - targetTime) <= maxTimestampDelta;
      if (belongsToThisSeek && matchesTarget) {
        finish(null, metadata.mediaTime);
        return;
      }
      callbackId = video.requestVideoFrameCallback(onFrame);
    };
    const timeoutId = setTimeout(
      () => finish(new Error('Timed out waiting for the target video frame')),
      timeoutMs,
    );
    callbackId = video.requestVideoFrameCallback(onFrame);
  });
}

function waitForTwoPaints(timeoutMs = 2000) {
  return new Promise((resolve, reject) => {
    let firstFrame;
    let secondFrame;
    let settled = false;
    const finish = (error) => {
      if (settled) return;
      settled = true;
      clearTimeout(timeoutId);
      if (firstFrame !== undefined) cancelAnimationFrame(firstFrame);
      if (secondFrame !== undefined) cancelAnimationFrame(secondFrame);
      if (error) reject(error);
      else resolve();
    };
    const timeoutId = setTimeout(
      () => finish(new Error('Timed out waiting for browser paints')),
      timeoutMs,
    );
    firstFrame = requestAnimationFrame(() => {
      if (settled) return;
      secondFrame = requestAnimationFrame(() => finish());
    });
  });
}

function clampToSeekable(video, requestedTime, epsilon) {
  const ranges = [];
  for (let index = 0; index < video.seekable.length; index += 1) {
    const start = video.seekable.start(index);
    const end = Math.min(
      video.duration - epsilon,
      video.seekable.end(index) - epsilon,
    );
    if (end >= start) ranges.push({ start, end });
  }
  if (ranges.length === 0) {
    throw new Error('The VOD has no usable seekable range');
  }

  const containingRange = ranges.find(
    ({ start, end }) => requestedTime >= start && requestedTime <= end,
  );
  if (containingRange) return requestedTime;

  return ranges
    .flatMap(({ start, end }) => [start, end])
    .reduce((closest, boundary) =>
      Math.abs(boundary - requestedTime) < Math.abs(closest - requestedTime)
        ? boundary
        : closest,
    );
}

async function seekAndPresent(
  video,
  requestedTime,
  maxTimestampDelta,
) {
  if (!Number.isFinite(requestedTime)) {
    throw new Error('requestedTime must be finite');
  }
  if (!Number.isFinite(maxTimestampDelta) || maxTimestampDelta <= 0) {
    throw new Error('maxTimestampDelta must be a positive finite number');
  }
  if (video.readyState < HTMLMediaElement.HAVE_METADATA) {
    await waitForMediaEvent(video, 'loadedmetadata');
  }
  if (video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA) {
    await waitForMediaEvent(video, 'loadeddata');
  }

  if (!Number.isFinite(video.duration) || video.duration <= 0 ||
      video.seekable.length === 0) {
    throw new Error('seekAndPresent requires finite, seekable VOD');
  }

  video.pause();
  const epsilon = 1 / 120;
  const targetTime = clampToSeekable(video, requestedTime, epsilon);
  let presentedMediaTime = null;
  let verification = 'paint-only';
  if (video.seeking || Math.abs(video.currentTime - targetTime) > 0.0005) {
    const seeked = waitForMediaEvent(video, 'seeked');
    const seekStartedAt = performance.now();
    video.currentTime = targetTime;
    const presented = typeof video.requestVideoFrameCallback === 'function'
      ? waitForPresentedFrame(
          video,
          targetTime,
          maxTimestampDelta,
          seekStartedAt,
        )
      : null;
    if (presented) {
      [, presentedMediaTime] = await Promise.all([seeked, presented]);
      verification = 'requestVideoFrameCallback';
    } else {
      await seeked;
      await waitForTwoPaints();
    }
  } else {
    await waitForTwoPaints();
  }

  return {
    requestedTime,
    targetTime,
    currentTime: video.currentTime,
    presentedMediaTime,
    verification,
  };
}
```

This helper is for finite, seekable video-on-demand. Live and low-latency HLS
need a recorded live-edge offset or another shared reference frame; do not
pretend an absolute VOD second is stable for them. Align `requestedTime` to an
observed frame timestamp and set `maxTimestampDelta` below half the smallest
observed frame interval. Retain the returned target, current, presented, and
verification fields with the screenshot evidence. `paint-only` is an explicit
fallback, not rVFC timestamp proof. A timeout is a failed capture, not
permission to compare an unknown frame.

For pointer-driven footage, record the pointer coordinate and wait for damping
to settle. For scroll-driven footage, record both pixel scroll and normalized
progress. For free-running loops, compare the same media second rather than the
same wall-clock delay.

## D. Match crop, masks, and compositing

Treat video layout as geometry. For `object-fit: cover`, derive the scale from
the intrinsic video and container:

```text
scale = max(containerWidth / videoWidth, containerHeight / videoHeight)
displayWidth  = videoWidth  * scale
displayHeight = videoHeight * scale
cropX = displayWidth  - containerWidth
cropY = displayHeight - containerHeight
```

Apply `object-position` to the excess crop instead of assuming a centered
frame. Capture recognizable landmarks near every edge to verify the crop.
Repeat the calculation after responsive reflow and when the source uses a
transform such as `scale(1.6)` rather than `object-fit` alone.

Reconstruct the complete layer contract:

```text
fallback surface or poster
→ video frame
→ color grade / opacity / blend
→ top, bottom, or radial fades
→ mask / clip / shader
→ decorative layers with pointer-events: none
→ semantic text and controls
```

Match gradient stops, mask coordinate systems, clip geometry, blend mode,
filter order, and border clipping before tuning individual colors. Verify text
contrast from final composited pixels, not the source CSS value.

## E. Mirror assets without changing them accidentally

Add these fields to the asset inventory:

- stable source URL and resolved URL;
- local path;
- media role and breakpoint/quality variant;
- MIME, codec, dimensions, duration, nominal frame rate, and audio channels;
- checksum and acquisition date;
- license, owner, attribution, and permitted modifications;
- playlist relationships and rewritten local URIs;
- any transcode, trim, color, or loop edit.

For MP4/WebM, verify redirects, `Content-Type`, byte size, checksum, and Range
requests. For HLS, recursively inventory the master, variants, media playlists,
initialization maps, media segments, audio/subtitle groups, and byte ranges.
Keep ABR variants when they affect fidelity or device behavior. Rewrite only
permitted assets to relative local URLs and test their MIME types in the built
deployment.

Never commit expiring query tokens or make the clone depend on a signed target
URL. Do not mirror DRM or encrypted playlists. When redistribution is not
licensed, use user-provided media, recreate an equivalent asset, or leave an
explicit replacement slot.

Avoid transcoding by default. A transcode can change color range, chroma,
frame cadence, keyframes, alpha, duration, and the loop seam. When conversion is
necessary, record the command and compare fixed frames plus the loop boundary.
Use `ffprobe` when available, but do not make it the only evidence source; the
browser's decoded dimensions and rendered pixels remain authoritative.

## F. Implement faithful playback and separate hardening

Maintain two explicit lanes:

- **Fidelity lane**: reproduce the observable normal path, including initial
  poster/no-poster state, autoplay behavior, ABR, controls, loop timing, and
  transitions.
- **Resilience lane**: add loading, error, offline, reduced-data, or fallback
  behavior that does not alter the observed normal path. Record any visible
  divergence and ask before intentionally improving the design.

Preserve native playback when it matches. For HLS, follow the target and the
installed library version:

1. Use `hls.js` only when MSE is supported and the target requires it.
2. Fall back to native `application/vnd.apple.mpegurl` playback where available.
3. Preserve adaptive quality unless evidence shows a fixed level.
4. Cap rendition selection to the rendered player size when doing so matches
   target behavior; do not force the highest level by default.
5. Handle fatal network/media errors with bounded recovery, then show the
   documented fallback.
6. Destroy the HLS instance, listeners, and object URLs on teardown.
7. Validate Safari's native HLS path and Chromium's MSE/`hls.js` path
   separately whenever both are supported deliverables.

Do not silently swallow `play()` rejection. Keep the semantic content and CTA
usable when autoplay fails. Add a poster or brand-color fallback only when it
matches the target or lives solely in an otherwise unobserved failure path.

For Canvas/WebGL video textures, set `video.crossOrigin = 'anonymous'` before
assigning `video.src`; the media server must return a compatible
`Access-Control-Allow-Origin` header for playlists, segments, and media files.
This media-element setting does not grant CORS access to `hls.js` fetches; its
playlist and segment requests must satisfy CORS independently. Update the
texture only when a new frame is presented, preserve color-space handling, and
validate the non-WebGL fallback. Do not create duplicate hidden `<video>`
elements for front/back faces or desktop/mobile variants unless the target
truly runs both.

## G. Reproduce responsive and input behavior

Test video composition at the target breakpoints and at each side of a media
query boundary. Record whether the target:

- scales one container;
- changes `object-position` or crop;
- swaps source/rendition;
- reorders the semantic section;
- replaces an interaction with a simpler mobile state;
- hides decoration while continuing or stopping decode;
- uses separate desktop/mobile players.

Prefer one semantic player and responsive composition when it matches. CSS
`display: none` alone does not guarantee that a duplicate video stops network
or decode work.

Reproduce pointer and touch paths independently. Do not infer touch behavior
from hover. Preserve keyboard and reduced-motion behavior from the target; when
the target omits them, treat accessibility improvements as documented
resilience changes rather than silently changing the main visual state.

## H. Run deterministic frame-aligned visual QA

Fix the environment before comparing:

- browser and version;
- viewport, DPR, zoom, color scheme, and font state;
- scroll position and normalized progress;
- pointer position and settled interaction state;
- media source, selected rendition when relevant, playback rate, and media
  time;
- CSS animation and page visibility state.

Capture at least an early frame, a middle frame, and a frame immediately before
the loop boundary. Add target-specific interaction frames such as hover reveal,
scroll midpoint, paused state, and error fallback. Wait for fonts, layout,
`seeked`, and a presented media frame before each screenshot.

Compare stable UI and video regions deliberately:

- Use a strict mask for typography, controls, and layout.
- Compare the full frame at fixed media time with a codec-appropriate pixel
  threshold.
- Use an additional crop mask around recognizable video landmarks.
- Treat cross-platform decoder noise separately from geometry, crop, opacity,
  and overlay errors.

Run the bundled comparator when Pillow is available:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/clone-any-website/scripts/compare-screenshots.py" \
  docs/research/original-2.000.png \
  docs/research/clone-2.000.png \
  --mask docs/research/stable-ui-mask.png \
  --output docs/research/diff-2.000.png \
  --pixel-threshold 16
```

The script reports RGB MAE, RMSE, p95 maximum-channel delta, and mismatched
pixel ratio. With no `--max-*` option, it is measurement-only and reports
`"gates_configured": false` and `"passed": null`. Establish gates from repeated
captures of the same target state; do not invent a universal zero-difference
threshold for decoded video. After storing calibrated limits in the shell, run
the same comparison as a gate:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/clone-any-website/scripts/compare-screenshots.py" \
  docs/research/original-2.000.png \
  docs/research/clone-2.000.png \
  --mask docs/research/stable-ui-mask.png \
  --output docs/research/diff-2.000.png \
  --pixel-threshold 16 \
  --max-mismatch-ratio "$CALIBRATED_MAX_MISMATCH_RATIO" \
  --max-mae "$CALIBRATED_MAX_MAE"
```

Fix deltas in this order:

1. viewport, bounding boxes, and crop;
2. media time and loop phase;
3. overlay, mask, opacity, and color grade;
4. typography and controls;
5. secondary motion and codec-level residuals.

## I. Test lifecycle, performance, and failures

Exercise:

- loading surface and first decoded frame;
- autoplay rejection and user-gesture recovery;
- tab backgrounding and refocus;
- offscreen pause/resume behavior;
- slow network, offline, bad MIME, CORS denial, and Range failure;
- HLS master, variant, map, and segment failure;
- loop seam and long-running clock drift;
- reduced motion, Save-Data, low-memory mobile, and thermal pressure;
- source swap at every responsive boundary;
- audio unlock, mute, and captions when the media is meaningful;
- repeated mount/unmount without leaked players, object URLs, or listeners.

Count concurrent decoders. Pause or unload offscreen players only when it
matches the target or is recorded as a resilience improvement. Never ship a
desktop/mobile pair that downloads both sources accidentally. Confirm the final
runtime makes zero requests to the original host.

## J. Acceptance checklist

- [ ] Every player has a recorded role, source topology, clock owner, crop,
      responsive state, and exact/approximate decision.
- [ ] Public access and redistribution rights were assessed separately.
- [ ] No DRM, access control, expiring token, credential, or target-host runtime
      dependency was copied into the result.
- [ ] The normal path matches the target before resilience improvements are
      evaluated.
- [ ] Original and clone frames were captured at identical environment,
      interaction, and media-time anchors.
- [ ] Crop, masks, gradients, blend, typography, and controls were compared in
      the final composited screenshot.
- [ ] Poster/loading, first frame, active playback, loop boundary, mobile,
      failure, muted/audio, and reduced-performance states were exercised when
      applicable.
- [ ] Screenshot metrics and heatmaps were retained with the research evidence.
- [ ] The final build was tested with correct video/HLS MIME and Range behavior.
- [ ] Exact behavior, approximations, visible hardening changes, and unresolved
      media licensing were reported at handoff.
