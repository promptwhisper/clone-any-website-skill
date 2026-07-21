# DOM-Heavy Pages

Read this reference for product pages, marketing sites, documentation, portals,
dashboards, and application screens whose primary experience is rendered as
HTML and CSS rather than canvas.

## Contents

- Reconnaissance
- Component boundaries
- Computed-style extraction
- States and behavior
- Responsive reconstruction
- Implementation order
- DOM-specific QA

## Reconnaissance

Capture the full page at desktop and mobile, then perform the interaction sweep
before defining components. Scroll slowly before clicking anything so sticky,
snap, reveal, parallax, and scroll-driven selection behavior are not mistaken
for click-based UI. Test tablet width when it presents a distinct layout.

Map every flow section, fixed or sticky overlay, portal, modal, and persistent
navigation element. Record which element owns scrolling and whether a smooth
scroll library or CSS scroll timeline is active.

## Component Boundaries

Define a component or subsystem boundary when an area has independent layout,
content variants, responsive behavior, interaction state, or verification
criteria. Do not split every wrapper into a component. Do not combine unrelated
sections merely because they appear next to each other.

Write one specification before implementing each independent boundary. Split a
spec further when it contains multiple complex interactive children or cannot
be verified with a focused screenshot and interaction path.

## Computed-Style Extraction

Use `getComputedStyle()` and element bounds instead of translating appearances
directly into framework utility classes. Capture only relevant properties, but
cover at least:

- typography: family, loaded weight, size, line height, letter spacing, color;
- geometry: bounding rectangle, width constraints, padding, margin, and gap;
- layout: display, grid tracks, flex alignment, order, position, inset, z-index;
- surface: background, border, radius, shadow, opacity, filter, and blend mode;
- media: intrinsic dimensions, `object-fit`, `object-position`, and crop;
- behavior: transform, transition, animation, overflow, scroll snap, and cursor.

Record the exact viewport and state with every extraction. An isolated computed
value without its inherited context or containing-block geometry is not a
usable specification.

Extract real text, alt text, accessible names, input placeholders, and every
state's content. Enumerate descendant images, videos, SVGs, CSS backgrounds,
pseudo-elements, and absolutely positioned overlays; a composition that looks
like one image may use several layers.

## States and Behavior

Classify each subsystem as static, scroll-driven, click-driven, hover-driven,
pointer-driven, keyboard-driven, time-driven, or mixed. For each state change:

1. capture state A;
2. trigger the behavior through the real input path;
3. capture state B at a stable readiness condition;
4. record changed styles, DOM, content, media, URL, focus, and accessibility
   state;
5. measure trigger threshold, duration, delay, easing, interruption, and reset.

Exercise every tab, accordion item, carousel slide, menu, dialog, and form state
that is within scope. Test focus-visible and keyboard paths when the original
provides them. Preserve observed reduced-motion and accessibility behavior. If
the user wants improvements beyond the source, implement and validate them as a
separate customization so fidelity comparisons remain meaningful.

## Responsive Reconstruction

Observe at 1440 px, approximately 768 px, and 390 px, then probe around suspected
breakpoints to find the actual change. Record what changes, not only the width:
layout mode, element order, visibility, type scale, crop, overflow, sticky
behavior, navigation model, and interaction model can all differ.

Prefer intrinsic layout and content-driven constraints over many screenshot-
specific breakpoints. Match the observed breakpoints when behavior depends on
them; do not inherit framework defaults without evidence.

## Implementation Order

1. document flow, page width, section heights, backgrounds, and scroll owner;
2. fonts, type metrics, color tokens, icons, and shared controls;
3. header, primary navigation, hero, and dominant media;
4. section grids, cards, and real content;
5. sticky, scroll-driven, modal, tab, and form behaviors;
6. responsive and reduced-motion branches;
7. secondary decoration and micro-interactions.

Implement semantic structure and focus behavior together with visuals. Use the
existing repository's stack and conventions unless target behavior requires a
specific library.

## DOM-Specific QA

Compare in this order: page geometry, fonts and line wrapping, dominant media,
section spacing, controls, borders and shadows, then micro-interactions. Verify
full-page captures and focused component states because one does not replace the
other.

Inspect layout shift, horizontal overflow, font-loading changes, console errors,
broken anchors, focus traps, hover on pointer devices, and touch on mobile. Do
not declare fidelity from a desktop screenshot alone.
