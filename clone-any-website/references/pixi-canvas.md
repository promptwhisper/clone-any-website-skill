# Pixi.js and Canvas2D

Read this reference for sprite-atlas games, CRT-style screen toys, 2D WebGL, or
Canvas2D animation.

## Stack

Use Vite + TypeScript and match the target library's major version. Avoid React
or R3F when the experience is a single canvas game and DOM state is minimal.

For an unminified, single-file art toy, a compact structure is often enough:

```text
src/
  config.ts
  game.ts
  main.ts
```

Split further only when it creates a real ownership boundary.

## Coordinate System

Keep authored sprite positions, polygons, and hit areas in the original design
coordinate system. Scale one world container to the viewport:

- fit by the target's dominant dimension;
- preserve aspect ratio;
- center with the source alignment rule;
- do not recompute every hit polygon on resize.

## Pixi v8

Initialize asynchronously:

```ts
await app.init({
  canvas,
  resizeTo: window,
  autoDensity: true,
  resolution: Math.min(devicePixelRatio, dprCap),
});
```

Load a TexturePacker atlas through `Assets`, then use the returned spritesheet's
texture map. When multiple atlases intentionally override duplicate texture
names, distinguish harmless cache warnings from actual wrong assets.

## Audio and Start Gates

Expect a user gesture before audio starts. Implement the click-to-start surface
as a full-world interactive region, then remove it after activation.

Keep mute as an accessible DOM button over the canvas unless the source requires
canvas-native UI. Match the original audio library major when timing or pooling
depends on it.

## CRT and Distortion

A CRT-style composite commonly uses:

1. a playfield rendered into a texture;
2. a subdivided mesh;
3. bilinear corner interpolation;
4. radial barrel distortion;
5. a mask or overlay texture.

Extract subdivisions, corner points, center offset, radius, and strength from
the target. Do not substitute a generic CSS perspective transform when the
warped hit area or screen curvature is visible.

## Intentional Frame Rate

Some toys render the inner screen at 30 fps while the outer scene runs at 60.
Throttle the inner renderer with an elapsed-time guard. Provide an unthrottled
final render at the end of each state transition so the scene never stops on a
stale frame.

## Canvas2D

- Match canvas backing resolution and CSS size separately.
- Apply DPR once.
- Reset transforms before clearing or resizing.
- Use the original draw order and composite operations.
- Predecode images and fonts before the first timed sequence.
- Keep deterministic time progression for screenshot tests when possible.

## Validation

- Verify alpha edges and sprite filtering.
- Verify pointer coordinates after every resize rule.
- Check the first frame after start and the final frame after each animation.
- Compare mobile asset variants.
- Confirm no frame is stale after a throttled transition.
- Test audio unlock, mute, restart, and tab refocus.
