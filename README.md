# Lexi

**An adaptive reading engine that rewrites documents to fit how *you* read — not the other way around.**

[Demo Video](#) · [Live Demo](#) · [Kaggle Write-up](#)

---

## The Problem

Millions of people process text differently than the "default" reader a document is written for — people with dyslexia, people with ADHD, screen-reader users navigating poorly structured PDFs, and non-native speakers hitting walls with dense academic phrasing. Today, the burden falls entirely on the reader: squint harder, re-read five times, ask someone to explain, or give up.

ReadEasy flips that. The document adapts to the reader.

## What It Does

Lexi isn't a one-button "make text simpler" tool. It's a personalized reading accessibility engine powered by a three-stage Gemma 4 pipeline:

1. **Mode-specific rewriting** — the user picks their barrier (dyslexia / focus-ADHD / screen-reader / non-native speaker), and Gemma 4 rewrites the document differently depending on what actually helps.
2. **Meaning-preservation self-check** — Gemma 4 compares the simplified version against the original and flags anything it isn't fully confident preserved the original meaning, facts, or numbers.
3. **Grounded Q&A companion** — the user can ask follow-up questions about the document and get answers tied specifically to the original text.

Every output is also read aloud via browser-native text-to-speech, with adjustable pacing.

## Why It's Different

| Typical "simplifier" tools | Lexi |
|---|---|
| One-size-fits-all vocabulary shrinking | Four distinct rewriting modes for four distinct barriers |
| Silent output, no accuracy check | Self-check pass that flags uncertain simplifications |
| Static, one-way transformation | Interactive Q&A grounded in the original document |
| Text-only | Audio-first, with pacing control |

## User Flow

1. Upload a document or paste text
2. Pick a reading mode (or let Gemma 4 suggest one)
3. Gemma 4 rewrites the content for that mode
4. Gemma 4 self-checks the rewrite and flags uncertain simplifications
5. User reads/listens to the result, side-by-side with the original
6. User asks follow-up questions, answered in context
7. Optional: export the simplified version

## Architecture

```
┌─────────────┐      ┌──────────────────────────────────────┐      ┌─────────────┐
│  Frontend   │────▶|           Backend (Gemma 4)           │────▶│  Frontend   │
│  Upload/UI  │      │                                      │      │  Display    │
└─────────────┘      │  1. Rewrite  (mode-specific prompt)  │      └─────────────┘
                     │  2. Self-check (original vs. rewrite)│
                     │  3. Q&A (grounded in original doc)   │
                     └──────────────────────────────────────┘
```

- **Frontend:** [tech stack — fill in]
- **Backend:** [tech stack — fill in]
- **Model:** Gemma 4, 3 sequential calls per document
- **Text-to-speech:** Browser-native Web Speech API
- **No datasets, no training, no external ML models** — all "smart" behavior comes from the prompt pipeline

## Reading Modes

- **Dyslexia mode** — shorter sentences, common words over rare synonyms, one idea per line, reduced clause-nesting
- **Focus/ADHD mode** — small labeled chunks, clear breakpoints, bolded key terms, filler removed
- **Screen-reader mode** — rebuilt heading hierarchy, descriptive structure, logical reading order
- **Non-native speaker mode** — simplified idioms and academic phrasing, technical accuracy preserved

## Setup

```bash
# Clone the repo
git clone [repo-url]
cd lexi

# Backend
[setup instructions — fill in]

# Frontend
[setup instructions — fill in]

# Environment variables
[.env instructions — fill in, e.g. GEMMA_API_KEY]
```

## Team

| Name | Role |
|---|---|
| Jannatul Ferdaus Chowa | Backend / Gemma Pipeline Lead |
| Dipannita Paul Orni | Frontend / UX Lead |
| Mahashweta Manjari Barua | Content, Testing & Presentation Lead |

## Real-World Impact

- Students with dyslexia/ADHD navigating dense academic material
- Screen-reader users dealing with poorly structured PDFs and forms
- Non-native speakers working through complex documents
- Anyone facing dense government forms, legal notices, or medical information

## Screenshots / Demo

[placeholder — add screenshots or GIF once frontend is live]
