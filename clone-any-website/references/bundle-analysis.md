# Bundle Analysis

Read this reference when observable behavior cannot be reproduced reliably from
screenshots and interaction alone.

## Purpose

Use client-delivered JavaScript as a read-only specification of public behavior.
Extract facts and reimplement them. Do not redistribute the bundle, source map,
or long source excerpts.

## Inspect Before Transforming

1. Read the first and last portions of each application bundle.
2. Check for comments, descriptive symbols, module boundaries, and source maps.
3. Skip beautification when the file is already readable.
4. For a large minified file, search for an anchor and print only a bounded
   region around it.

Useful anchors:

- asset filenames;
- visible text;
- component or scene names;
- shader identifiers;
- sound cue names;
- unusual constants;
- `requestAnimationFrame`;
- loader and worker constructors.

Use `rg` for search. Use a small script or structured parser for bounded
extraction rather than loading a multi-megabyte single line into every tool.

## Extraction Checklist

### Renderer

- WebGL version and antialiasing;
- output color space;
- tone mapping and exposure;
- alpha, premultiplication, and clear behavior;
- pixel ratio and mobile cap;
- shadow map type, size, bias, and normal bias;
- resize behavior and fixed aspect-ratio gates.

Common Three.js tone mapping numeric values include Linear 1, Reinhard 2,
Cineon 3, ACES 4, AgX 6, and Neutral 7. Confirm against the version in use.

### Scene and Camera

- world-unit conversion;
- FOV, near, far, and projection updates;
- Cartesian versus spherical camera formulas;
- follow, orbit, collision, and smoothing constants;
- camera-relative elements and billboards;
- sky dome versus CSS or renderer clear color.

### Lighting

- color and intensity;
- position formulas;
- shadow frustum and radius;
- ambient, hemisphere, environment, and emissive contribution.

### Materials

- map roles and color spaces;
- nearest versus linear filtering;
- wrapping and mipmap behavior;
- roughness, metalness, alpha test, side, depth write, and blending;
- `onBeforeCompile` patches;
- atlas sampling by mesh UV;
- toon ramps and outline settings.

### Postprocessing

- pass order;
- render-target formats;
- depth and normal requirements;
- LUT domain and interpolation;
- bloom, depth of field, vignette, grain, halftone, and outline thresholds;
- desktop versus mobile pass selection.

Treat shared UBOs, MRT outputs, and engine-global shader includes as a cost
signal. Approximate with standard materials and a clean custom effect when the
rendered result can match. Port a unique shader only when the effect cannot be
reproduced otherwise.

### Geometry and Animation

- bounds and authored scale;
- batched object identifiers;
- skeleton hierarchy and bind transforms;
- animation frame rate, interpolation, and state transitions;
- normalized skin weights;
- collision geometry and authored spawn positions.

One decoded geometry may contain many logical elements at the origin. Inspect
`Object.keys(geometry.attributes)` and split by the actual identifier instead of
guessing `batchId`, `elementId`, or `surfaceId`.

### Interaction

- pointer and touch event sequence;
- click-versus-drag distance;
- accumulated delta and dominant-axis choice;
- wheel and pinch scaling;
- snapping thresholds;
- easing curves and spring parameters;
- keyboard mappings and repeat behavior;
- audio cue timing.

Translate an animation library's behavior into an equivalent clean
implementation when the clone does not use that library. Preserve timing and
damping, not function names.

### Loading and Device Tiers

- every asset that increments progress;
- audio and video tasks;
- error and retry behavior;
- low-memory and mobile branches;
- low-resolution asset variants;
- disabled postprocessing and shadow features.

## Exact Versus Approximate

Record a decision for each subsystem:

| Choose exact behavior when | Choose an approximation when |
| --- | --- |
| A numeric threshold controls feel | Internal architecture is irrelevant |
| Layout depends on authored constants | A standard material matches pixels |
| Tone mapping changes the whole frame | A proprietary shader depends on a large engine |
| Asset framing must decode correctly | The effect can be reproduced independently |
| Input timing is user-visible | Exact source would require redistribution |

Judge success from stable screenshots, interaction traces, and runtime metrics,
not from source similarity.
