# Three.js and R3F

## Contents

- Recommended project shape and loading
- Renderer, materials, geometry, and animation
- GLB scene inspection and surgical asset editing
- Camera-relative elements and physics
- Performance and canvas validation

Read this reference for WebGL, Three.js, React Three Fiber, skinned characters,
custom materials, or 3D physics.

## Recommended Shape

Use the existing project structure when one exists. For a new R3F project,
prefer:

```text
src/
  app/
  components/r3f/
  lib/<topic>/
    loaders/
    r3f/
    assets.ts
    audio.ts
public/<topic>/
  geometries/
  images/
  audio/
  libs/
docs/research/
```

Keep runtime paths behind one base-path helper so local development, a root
deployment, and a GitHub Pages subpath all resolve the same assets.

## Loading

- Load async scene assets through Suspense-aware hooks.
- Wrap independent NPCs or props in separate Suspense boundaries when streaming
  should not block the entire scene.
- Signal readiness from an effect after the rendered subtree commits.
- Preload only what the next interaction needs.
- Surface HTTP and decoder failures visibly during development.

## Renderer First

Match these before tuning object colors:

- output color space;
- tone mapping and exposure;
- DPR and antialiasing;
- clear color or sky;
- light intensities;
- postprocessing order.

A color mismatch at this level invalidates material-by-material tuning.

## Atlases and Toon Materials

Small palette atlases often color terrain, clothing, and props through authored
UVs. Configure them with:

- nearest filtering;
- sRGB color space for color data;
- clamp-to-edge wrapping;
- no guessed per-mesh replacement colors.

When a custom engine shader is too coupled to port, combine the same atlas with
a standard toon material, a small `DataTexture` gradient, and an independent
outline pass. Compare final pixels before deciding it is insufficient.

## Skinned Meshes

- Rebuild the exact bone hierarchy.
- Preserve bind transforms and parent indices.
- Bind every clothing and body mesh to the intended skeleton.
- Call `normalizeSkinWeights()` after binding when decoded weights are not
  guaranteed to sum to one.
- Reuse clips deliberately; do not share mutable mixers accidentally.
- Dispose per-instance materials and mixers on unmount.

React Strict Mode can mount, clean up, and mount again. Make animation playback
self-healing:

```ts
if (!action.isRunning()) {
  action.reset().play();
}
```

## Batched Geometry

Inspect actual attributes. If geometry represents multiple logical objects:

1. identify the per-vertex or per-face object id;
2. split triangles without losing material attributes;
3. recompute bounds and normals only when needed;
4. apply the source layout formula;
5. verify every element, not only the first.

## GLB Scene Inspection and Surgical Asset Editing

Visible labels, logos, and props may be baked geometry rather than DOM
or runtime text. Inspect the scene graph before adding an overlay. Record:

- node and mesh names;
- parent order, local translation, rotation, and scale;
- accessor bounds, indices, normals, UV ranges, and material name;
- `extras` / `userData` used by gameplay;
- collider children and physics naming conventions;
- compression extensions and the runtime-selected asset variant.

Prefer a surgical glTF edit over re-exporting the whole scene through another
authoring tool. Preserve unrelated nodes, hierarchy, materials, animations,
extras, and extension contracts. When the project ships both `model.glb` and a
compressed variant, update and load-test both or deliberately change the loader
to one documented source of truth.

Palette-atlas assets often use a constant UV for an entire mesh. Preserve that
UV on every generated vertex; assigning the material name without its authored
UV can sample the wrong palette color.

When editing Draco assets through glTF-Transform, register the matching decoder
and encoder. Inspect the written file again: newly generated non-indexed
primitives may remain uncompressed even when the rest of the file uses Draco.
Accept the size delta explicitly or run a compatible optimization pass.

## Camera-Relative Elements

For an element that stays in front of the camera while the world moves, keep it
in the scene and update it every frame:

```ts
position.copy(camera.position).addScaledVector(forward, distance);
quaternion.copy(camera.quaternion);
```

Do not assume an R3F camera is attached to the rendered scene graph. Parenting
an element to it can make the element disappear.

## Physics

- Match world units before tuning force.
- Separate visual geometry from simple collision geometry when appropriate.
- Match mass, damping, friction, restitution, sleeping, and solver step.
- Apply small impulses and verify the first contact before adding dramatic
  motion.
- Change damping after impact when the original settles quickly.
- Validate edge-on, sliced, or fractured faces with the intended material side.
- When replacing a visible physics-backed mesh, preserve its node name, extras,
  collider ownership, initial transform, and reset registration.

## Audio and Slow-Load Stability

Do not run per-frame audio setters against sounds that have not loaded. Some
audio libraries queue `rate`, `volume`, `mute`, or `seek` calls until readiness;
issuing them every render tick can produce a large deferred queue and recursive
overflow on a slow first load. Gate spatial/rate/volume updates on the library's
loaded state, then verify mute, blur/focus, and click-to-start audio unlock.

## Performance

- Merge truly static meshes by material.
- Reuse geometry and textures.
- Instance repeated props.
- Throttle noncritical raycasts.
- Cap DPR.
- Scale shadow maps by device tier.
- Drop normal passes, MSAA, outlines, or expensive particles on low tier.
- Add touch controls only when the target supports mobile interaction.
- Dispose render targets, materials, and generated geometry.
- Define an evidence-based frame-time, load-time, memory, or draw-call budget
  when performance is part of the observed experience; do not call a branch
  optimized without a recorded target and measurement.

## Canvas Validation

Confirm:

- the canvas contains nonbackground pixels;
- it remains nonblank after resize and interaction;
- the main subject stays framed at desktop and mobile sizes;
- dynamic content moves between captures;
- WebGL-unavailable and context-loss behavior matches the observed target when
  it provides a fallback or recovery path;
- no UI overlaps the canvas incorrectly;
- all assets load from the clone's origin.

Use normal browser screenshots for WebGL. Avoid using `canvas.toDataURL()` as the
primary test when drawing-buffer preservation is disabled.
