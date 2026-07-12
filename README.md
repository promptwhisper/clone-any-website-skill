# Clone Any Website Skill

A Codex skill for rebuilding public websites as clean, maintainable projects
with disciplined visual and interaction QA.

It covers:

- stack triage for DOM, Three.js, Pixi.js, and Canvas2D targets;
- browser reconnaissance and responsive state capture;
- local static-asset mirroring;
- video-first MP4/WebM/HLS reconstruction with frame-aligned visual QA;
- client-bundle analysis as a behavioral reference;
- clean-room implementation;
- screenshot, interaction, network, build, and deployment validation.

The skill is based on practical lessons from video-led product pages,
interactive WebGL scenes, skinned characters, physics toys, sprite-atlas games,
and animated screen toys.

## Install

Clone the repository and link the skill into your Codex skills directory:

```bash
git clone https://github.com/promptwhisper/clone-any-website-skill.git
mkdir -p ~/.codex/skills
ln -s "$PWD/clone-any-website-skill/clone-any-website" ~/.codex/skills/clone-any-website
```

Restart Codex after installation.

## Use

Invoke it explicitly:

```text
Use $clone-any-website to rebuild https://example.com in a clean local project.
```

It also triggers on requests such as:

- "复刻这个公开网站"
- "Clone this interactive Three.js page"
- "Rebuild this HLS video landing page frame by frame"
- "Port this Pixi screen toy to TypeScript"
- "Rebuild this page with pixel-accurate responsive behavior"

## Scope

Use this workflow for public targets. Do not bypass authentication, payment,
access controls, or technical restrictions. Reimplement application logic as
clean source code instead of redistributing the original compiled application.

## Structure

```text
clone-any-website/
  SKILL.md
  agents/openai.yaml
  references/
    bundle-analysis.md
    pixi-canvas.md
    qa-and-gotchas.md
    recon-and-assets.md
    three-r3f.md
    video-first.md
  scripts/
    compare-screenshots.py
```

`SKILL.md` contains the core workflow. Detailed 3D, 2D, reconnaissance,
video-first, bundle-analysis, and QA guidance is loaded from `references/` only
when needed. The screenshot comparator reports repeatable pixel-difference
metrics and can emit a heatmap for fixed states and media times.

## License

MIT. See [LICENSE](LICENSE).
