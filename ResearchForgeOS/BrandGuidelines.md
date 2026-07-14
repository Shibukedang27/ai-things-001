# Brand Guidelines

ResearchForge OS should feel calm, intelligent, premium, and deeply useful. The visual system should create immediate trust without looking generic, loud, or AI-generated.

## Brand Position

**ResearchForge OS is the knowledge operating system for people who turn information into leverage.**

It should feel like a focused professional tool, not a toy demo.

## Personality

- Calm
- Precise
- Editorial
- Fast
- Thoughtful
- Technically credible
- Quietly premium

## Voice

Use concise, specific language. Avoid hype, exaggerated claims, and vague AI wording.

Preferred:

- "Build a knowledge graph from this collection."
- "Trace this claim to its source."
- "Create a revision plan from weak concepts."
- "Compare these papers by assumptions, methods, and findings."

Avoid:

- "Unlock the power of your PDFs."
- "Chat with your documents."
- "Supercharge your productivity."
- "AI magic for research."

## Visual Direction

The product is light theme only.

| Token | Value |
| --- | --- |
| Background | Warm white |
| Surfaces | Pure white |
| Text | Ink black and soft graphite |
| Borders | Subtle warm gray |
| Accent | Research blue with restrained use |
| Success | Deep green |
| Warning | Amber |
| Error | Measured red |

## Color Palette

| Name | Hex | Use |
| --- | --- | --- |
| Warm White | `#FAF9F6` | App background |
| Surface | `#FFFFFF` | Panels, cards, menus |
| Ink | `#171717` | Primary text |
| Graphite | `#44403C` | Secondary text |
| Muted | `#78716C` | Metadata |
| Border | `#E7E5E0` | Dividers and outlines |
| Soft Border | `#F0EEE9` | Large quiet surfaces |
| Research Blue | `#2457D6` | Primary action and active states |
| Citation Teal | `#167A72` | Citations and evidence |
| Memory Green | `#2F7D4F` | Progress and mastery |
| Amber | `#B7791F` | Review-needed states |
| Red | `#B42318` | Errors and destructive actions |

## Typography

Use a modern, highly readable sans-serif. The preferred stack:

```css
Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
```

Guidelines:

- Use generous line height for reading views.
- Avoid oversized dashboard headings.
- Use strong hierarchy through weight, spacing, and layout before color.
- Keep letter spacing at zero.

## Layout

- Use full-width work surfaces with constrained reading regions.
- Prefer dense, organized professional layouts over marketing-style cards.
- Cards should be used for individual repeated objects, not as nested page structure.
- Keep border radii restrained.
- Preserve whitespace around important reading and thinking areas.

## Motion

Motion should feel natural, quiet, and useful.

| Interaction | Motion Direction |
| --- | --- |
| Page transition | Soft fade with slight vertical movement |
| Search expand | Smooth width and opacity transition |
| Cards appearing | Gentle fade and lift |
| Graph nodes | Slow, purposeful settling motion |
| Hover states | Fast border, shadow, or background response |

Avoid excessive bounce, flashy gradients, glassmorphism, and decorative motion that does not clarify state.

## Component Philosophy

Every page should have its own identity:

- Landing Page: editorial, confident, product-forward
- Research Dashboard: operational, scan-friendly, high trust
- Knowledge Graph: spatial, exploratory, traceable
- Document Viewer: readable, citation-first, focused
- AI Workspace: structured reasoning, not loose chat
- Mind Map: calm visual synthesis
- Notebook: personal, durable, editable
- Flashcards and Quiz: focused learning loops
- Analytics: learning progress and knowledge quality, not vanity metrics

## Design-System Foundation

The initial token source is stored in [assets/design-tokens.json](assets/design-tokens.json). Future frontend work should implement tokens from that file before building product pages.
