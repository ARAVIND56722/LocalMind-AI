# Visual Design & UX Specification
## The Lenny Growth Assistant — "Editorial Research Studio"
**Visual Direction:** Warm, tactile, publication-grade editorial interface.  
**Inspiration:** The Economist Intelligence Unit, The Paris Review, Matter, high-craft editorial studios.  

---

### 1. Visual Philosophy & Identity
The Lenny Growth Assistant avoids the clichéd "AI dark mode" (deep blue neon gradients, generic chat bubbles, floating purple orbs). Instead, it adopts the tactile, thoughtful aesthetic of a **prestigious editorial research studio**.

- **Surfaces:** Warm ivory, unbleached cotton, and tactile parchment (#FBF9F5, #F4EFE6, #FFFFFF).
- **Typography:**
  - Headings: Serif authority with modern warmth (Playfair Display / Georgia / Merriweather).
  - Body & UI: Crisp, legible, accessible sans-serif (Inter / Newsreader / Plus Jakarta Sans).
  - Monospace: Editorial code clarity (JetBrains Mono / Fira Code).
- **Accents:**
  - **Primary Editorial Accent:** Terracotta Vermilion (`#E05338` / `#FF5A36`) — symbolizes editorial revision, urgency, and intellectual spark.
  - **Secondary Focus Accent:** Fresh Sage / Editorial Chartreuse (`#D2E823` / `#B5D33D`) — highlights verified citations, high-confidence grounding, and active states.
  - **Typography & Ink:** Deep Charcoal Ink (`#1E221E` / `#2D312E`) and warm graphite (`#5C625D`).

---

### 2. Design Tokens & Color Palette

```css
:root {
  /* Surfaces */
  --color-paper-50: #FDFAF5;
  --color-paper-100: #F7F3EB;
  --color-paper-200: #EDE6D8;
  --color-paper-300: #DED3BF;
  
  /* Inks */
  --color-ink-900: #1B1E1B;
  --color-ink-800: #2C302B;
  --color-ink-600: #585F56;
  --color-ink-400: #889086;

  /* Accents */
  --color-vermilion: #E34A26;
  --color-vermilion-light: #FFEDE8;
  --color-vermilion-hover: #C93917;
  
  --color-sage: #B4CE5F;
  --color-sage-subtle: #F3F8E2;
  
  /* Borders & Dividers */
  --border-subtle: rgba(44, 48, 43, 0.08);
  --border-medium: rgba(44, 48, 43, 0.16);

  /* Shadows */
  --shadow-editorial: 0 4px 20px -2px rgba(44, 48, 43, 0.06), 0 2px 6px -1px rgba(44, 48, 43, 0.04);
}
```

---

### 3. Application Layout & Component Architecture

1. **Editorial Masthead & Navigation Sidebar (Left, 280px):**
   - Studio title: "The Lenny Growth Assistant" with issue stamp.
   - Provider status badge: Real-time connectivity indicator (Ollama Local vs Cloud API).
   - "New Research Session" primary action button with hotkey (`⌘N`).
   - Chronological session library with active session highlight.
   - Quick-access to Generated Artifacts & Essays.

2. **Main Conversation Studio (Center):**
   - Spacious column (max-width 880px) with generous breathing room.
   - Welcoming empty state with curated editorial prompt starters:
     - *"How does Elena Verna define Product-Led Sales vs Product-Led Growth?"*
     - *"What are Shreyas Doshi’s 7 principles of PM leverage?"*
     - *"Draft a Ship 30 essay on finding true Product-Market Fit."*
   - Clear distinction between User queries (neat paper card) and Assistant research responses (editorial memo layout with serif section titles).
   - Grounded Citation Drawer: Interactive badges showing episode title, speaker, and timestamp that expand into the verified transcript quote on hover/click.

3. **Artifact Workspace (Right / Split View):**
   - Automatically slides in when an essay, PRD, or HTML artifact is produced.
   - Top action bar: Artifact Title, Word Count, Type Badge (Markdown / HTML), Copy Source, Full-Screen toggle, and Close.
   - Segmented Tabs: **Rendered Preview** | **Raw Source**.
   - HTML view rendered in a fully sandboxed security frame.
