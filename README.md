<div align="center">

# Lexi

### Text that adapts to *how you read*, not the other way around.

**Every document assumes one kind of reader. Lexi rewrites it for the rest of us and checks its own work before it hands anything back.**

<p align="center">
  <img width="1548" height="791" alt="WhatsApp Image 2026-07-25 at 11 33 48 PM" src="https://github.com/user-attachments/assets/b96effd3-1f1c-47c8-9551-58c986a98ec7" />

</p>


Built on  
![Gemma 4](https://img.shields.io/badge/Gemma_4-8E75B2?logo=google&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white) ![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black) ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![Vite](https://img.shields.io/badge/Vite-646CFF?logo=vite&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)

**[▶ Watch the demo](YOUR_VIDEO_LINK_HERE)**

[The problem](#the-problem) · [The approach](#the-approach) · [What makes it different](#what-makes-it-different) · [How it works](#how-it-works) · [Architecture](#architecture) · [The seven modes](#the-seven-modes) · [Real-world impact](#real-world-impact) · [Why Gemma](#why-gemma-is-the-whole-engine) · [Tech stack](#tech-stack) · [Run it](#run-it-locally)

<br/>


</div>

---

## The problem

Almost everything written down assumes the same reader: someone who can hold a long sentence in working memory, decode unfamiliar words on the fly, and follow structure that exists only visually on the page.

A very large number of people do not read that way and the cost of ignoring them is not abstract.

- A student with **dyslexia** facing forty pages of assigned reading, where every long sentence destabilises comprehension.
- Someone with **ADHD** who has reopened the same paragraph six times because it is an unbroken wall of text.
- - A **screen-reader user** handed a document whose structure exists only visually — no real headings — so it reads as a flat, shapeless stream by ear.
- A **non-native reader** blocked not by the concepts, but by idiom, register, and jargon.
- Anyone standing in front of a **government form** where a single misread line costs them a benefit they are owed.

The tools that exist treat all of this as one problem with one fix: a single **"Simplify"** button. But shortening sentences helps a dyslexic reader and does nothing for a screen-reader user who needs real headings. Chunking a wall of text helps someone with ADHD and is irrelevant to someone who simply needs the vocabulary translated. **One output cannot serve opposite needs.**

And there is a second, quieter problem underneath the first. Simplification can silently change what a document *means* — and the people who most need simplified text are the least equipped to notice when it has gone wrong. A confidently mis-simplified medical instruction or legal notice is more dangerous than the original.

---

## The approach

Lexi is built on two convictions that shape every part of it:

**1. Different reading barriers need genuinely different rewrites — not the same output relabelled.**
Seven modes, each restructuring text along different axes: sentence length, ordering, emphasis, vocabulary, and how numbers and structure are presented.

**2. An AI that simplifies text for vulnerable readers has a duty to say when it isn't sure.**
Every rewrite is checked by a second pass that compares it against the original and flags where meaning may have drifted — with a confidence score and both versions shown.

The result is a reading tool that is willing to look *less* impressive — flagging its own uncertainty instead of projecting false confidence — because for the people it serves, that trade is the entire point.

---

## What makes it different

### 1. Seven genuinely different rewrites — not one, relabelled
The same paragraph comes out meaningfully different depending on who is reading it. This is the core thesis, and it is enforced by seven distinct rule sets, not seven tone presets.

<p align="center">
  <em>
    Lexi adapts the same document to different reading needs — from
    dyslexia-friendly and focus-oriented rewriting to screen-reader,
    civic, dyscalculia, and low-vision modes.
  </em>
</p>

<h3 align="center">The seven reading modes</h3>

<table align="center">
  <tr>
    <td align="center"><strong>01</strong><br>Dyslexia-Friendly</td>
    <td align="center"><strong>02</strong><br>Focus Mode</td>
    <td align="center"><strong>03</strong><br>Screen Reader</td>
    <td align="center"><strong>04</strong><br>Non-Native English</td>
  </tr>
  <tr>
    <td align="center"><strong>05</strong><br>Civic / Forms</td>
    <td align="center"><strong>06</strong><br>Dyscalculia</td>
    <td align="center"><strong>07</strong><br>ADHD-Friendly</td>
    <td></td>
  </tr>
</table>


### 2. It checks its own work
After every rewrite, a **second Gemma pass** compares the new version against the original and flags any passage where the meaning may have drifted — showing both excerpts side by side, with a confidence score.

For a birthday card, that is overkill. For a medical dosage, a legal notice, or a form that decides whether someone receives support, **a confidently wrong simplification is worse than none at all.** So Lexi tells you exactly where to look twice.

<div align="center">
  <img width="1355" height="805" alt="WhatsApp Image 2026-07-25 at 9 41 35 PM" src="https://github.com/user-attachments/assets/e45b064f-52ba-4e06-a0ad-75e2bdd28388" />

  <br/><em>Lexi shows exactly where it wasn't certain — original and rewritten wording side by side.</em>
</div>

### 3. Answers grounded in *your* document - or an honest "I don't know"
Ask a question and the answer is drawn from your document, with the supporting line quoted back. If the answer isn't in the text, Lexi says so, rather than inventing one.

---

## How it works

<div align="center">
  <img src="docs/screenshots/workspace.png" alt="Lexi rewriting a document in the split workspace" width="880" />
  <br/><em>A dense form, rewritten for dyslexia — original on the left, rewrite on the right, readability deltas above.</em>
</div>

<br/>

Lexi runs a document through **three distinct passes** — read, rewrite, verify — rather than a single "make it simpler" call.

```mermaid
flowchart LR
    U["Upload<br/>PDF · DOCX · text"] --> E["<b>1 · Extract</b><br/>parse &amp; split into<br/>token-budgeted chunks"]
    E --> R["<b>2 · Rewrite</b><br/>apply the rules for the<br/>chosen mode + level (Gemma)"]
    R --> V["<b>3 · Verify</b><br/>compare rewrite to original,<br/>flag drift, score it (Gemma)"]
    V --> Out["Result<br/>+ flags + confidence"]

    style E fill:#F2E9EF,stroke:#5A3A52,color:#221C18
    style R fill:#F7EEDF,stroke:#B85C38,color:#221C18
    style V fill:#EAF0E7,stroke:#5B7355,color:#221C18
    style Out fill:#fff,stroke:#5A3A52,color:#221C18
    style U fill:#fff,stroke:#9C9086,color:#221C18
```

Everything downstream - grounded Q&A, key points, glossary, flashcards and diagram generation - reuses the same extracted, chunked document.

---

## Architecture

A clean split: a **stateless FastAPI reasoning core** and a **provider-isolated React client**. Every AI capability is one HTTP call away and the frontend never knows or cares which model sits behind the API.

```mermaid
flowchart TB
    subgraph FE["React · Vite"]
        direction TB
        Pages["Landing · About · FAQ"]
        Work["Workspace<br/>7 modes · level slider · before/after<br/>self-check flags · grounded chat · study tools"]
        API["lib/api.js<br/><i>the only file that knows a backend exists</i>"]
        Pages --- Work --- API
    end

    subgraph BE["FastAPI · Python"]
        direction TB
        Routes["Routes<br/>upload · process · verify · ask · key-points<br/>glossary · flashcards · visualize · export · modes"]
        Client["<b>gemma_client.py</b><br/>single choke-point for every model call<br/>retries · timeouts · structured errors"]
        Store["rewrite · verify · qa · document_store (SQLite)"]
        Prompts["prompts/ — mode rules defined ONCE<br/>frontend mode list is derived from here"]
        Routes --- Client --- Store --- Prompts
    end

    Gemma["<b>Gemma 4</b><br/>gemma-4-31b-it - all reasoning &amp; generation<br/>gemma-4-12b-it - audio-in (dictation)"]

    API -->|JSON over HTTP| Routes
    Client --> Gemma

    style FE fill:#F2E9EF,stroke:#5A3A52,color:#221C18
    style BE fill:#F7EEDF,stroke:#B85C38,color:#221C18
    style Gemma fill:#EAF0E7,stroke:#5B7355,color:#221C18
    style Client fill:#fff,stroke:#B85C38,stroke-width:2px,color:#221C18
    style API fill:#fff,stroke:#5A3A52,stroke-width:2px,color:#221C18
```

**Engineering decisions worth calling out:**

- **One choke-point for the model.** Every Gemma call flows through `gemma_client.py`, which owns retries, timeouts and structured error codes. Nothing else in the codebase talks to the model directly - so behaviour is consistent and testable across all ten AI features.
- **Prompts defined once.** Mode rules live in `prompts/rewrite_prompts.py`; the frontend's mode list is served from `/modes`, derived from those same keys. Frontend and backend cannot drift out of sync.
- **The frontend is provider-agnostic by construction.** `lib/api.js` is the only file aware a backend exists. Point `VITE_API_BASE` elsewhere and nothing else moves.
- **Long documents are chunked to a token budget**, so each piece is rewritten with care rather than a whole document being loosely summarised - the difference between a rewrite and a lossy summary.

---

## The seven modes

Each mode is a genuinely different transformation, not a tone setting.

| # | Mode | What it changes |
|---|------|-----------------|
| 01 | **Dyslexia-Friendly** | Short sentences, common words, one idea per line, generous spacing. |
| 02 | **Focus Mode** | Key points surfaced first, bulleted structure, essentials in bold. |
| 03 | **ADHD-Friendly** | Small chunks, the most important action first, one action per line, nothing buried. |
| 04 | **Screen Reader** | Real heading structure and speech-friendly punctuation for listening, not looking. |
| 05 | **Non-Native English** | Plain vocabulary with idiom and jargon clarified inline. |
| 06 | **Civic / Forms** | Requirements, deadlines, fees, and steps pulled out of bureaucratic prose. |
| 07 | **Dyscalculia** | Numbers, tables, and percentages explained in plain language. |

On top of the mode sits a **1–5 simplification level** - *which barrier* and *how far to go* are separate questions, so they get separate controls.

---

## Everything you can do with a document

Once a document is loaded, every feature works from that same source:

- **Adaptive rewrite** with before/after comparison and readability deltas (grade level, words-per-sentence, sentence count).
- **Self-verification** with a confidence score and flagged passages.
- **Grounded Q&A** - ask in English or Bangla, get answers from the document with the supporting excerpt.
- **Key points**, **glossary**, and **flashcards** generated on request.
- **Diagram generation** - flowcharts and charts when the content has structure worth drawing.
- **Read aloud** with the browser's speech engine, and **dictation** to speak text in.
- **Export** to a branded PDF (with full Bangla support) or plain text.

---

## Real-world impact

Lexi is built for people, in a place, with a language — not for a demo.

**It works in বাংলা, end to end.** The interface, the rewriting, and the grounded Q&A all operate in Bangla as well as English. For a reader in Bangladesh facing an English-heavy government form, or a Bangla document written in dense officialese, this is the difference between understanding a document and guessing at it. PDF export embeds Unicode fonts so Bangla survives the round-trip intact — a detail most tools quietly get wrong.

**The interface is itself an accessibility surface**, not a wrapper around one. Adjustable text size, relaxed line spacing, dark mode, full keyboard navigation, and screen-reader labelling throughout. Body text is set in **Lexend**, a typeface independently designed to improve reading proficiency.

**Nothing is stored and nothing trains a model.** Documents live only for the length of a session and are never persisted or reused — because the people most likely to paste in a medical letter or a legal notice are exactly the people who most need that guarantee.

The through-line: the readers Lexi is built for are usually an afterthought. Here they are the entire specification.

---

## Why Gemma is the whole engine

Nothing in Lexi works by keyword matching or hand-written rules. Every capability is real language reasoning:

- deciding *which* clause in a legal paragraph is the fragile one,
- rewriting for a specific cognitive barrier **without losing meaning**,
- judging whether a rewrite has drifted from its source,
- answering a question grounded in one specific document — and admitting when the answer isn't there.

**Every generative call in Lexi runs on Gemma 4.** Rewriting, verification, grounded Q&A, glossary, flashcards, key points, and visualisation — all of it. Dictation uses Gemma's audio-capable variant. Strip Gemma out and there is no fallback; there is nothing.

> **One honest note on retrieval.** For grounded Q&A, Lexi ranks document chunks with a hosted embedding model, because Gemma exposes no embedding endpoint. Embeddings are **not generative** — they encode text as vectors so the right passage can be located *before* Gemma answers from it. Every piece of reasoning and every word of output remains Gemma's.

---

## Tech stack

Every choice below was made for a reason — not pulled in by default.

### Backend — a stateless reasoning core

| Layer | Choice | Why |
|-------|--------|-----|
| **API framework** | **FastAPI** + Uvicorn | Async-native, so the many Gemma calls per document don't block; automatic OpenAPI docs at `/docs`. |
| **AI model** | **Gemma 4** via Google AI Studio | The entire reasoning engine — hosted, so no local GPU is needed to run the project. |
| **HTTP client** | **httpx** | Async calls to the Gemma API, with retries and timeouts centralised in one client. |
| **Validation** | **Pydantic v2** + pydantic-settings | Every request and response is a typed model; config loads from env, never hardcoded. |
| **Document extraction** | **PyMuPDF** · **pdfplumber** · **python-docx** | Layered PDF and DOCX text extraction — pdfplumber recovers tables PyMuPDF alone would miss. |
| **Storage** | **SQLite** | Session-scoped document store — zero-config, no external database to stand up. |
| **Export** | **fpdf2** | Branded PDF export with embedded Unicode fonts, so **Bangla survives the export** intact. |
| **Tests** | **pytest** + pytest-asyncio | The async pipeline is covered by tests, not just run by hand. |

### Frontend — a provider-agnostic client

| Layer | Choice | Why |
|-------|--------|-----|
| **Framework** | **React 18** + **Vite** | Fast dev loop; the component model suits the modular workspace. |
| **Routing** | **React Router** | Clean separation of the marketing pages and the tool itself. |
| **Diagrams** | **Mermaid** | Renders Gemma-generated flowcharts as real, in-browser diagrams. |
| **Typography** | **Lexend** · Fraunces · Poppins · Noto Sans Bengali | Lexend is independently designed to improve reading speed — an accessibility choice, not a cosmetic one. Noto Sans Bengali gives full বাংলা coverage. |
| **State & i18n** | Native React + a bilingual string layer | No heavyweight state library; EN / বাংলা handled in one `strings.js`. |
| **API isolation** | A single `lib/api.js` | The only file that knows a backend exists — the whole provider can be swapped from one place. |

---

## Run it locally

### 1 · Backend

```bash
cd lexi-backend-v3
python -m venv venv
venv\Scripts\activate            # Windows  ·  source venv/bin/activate on macOS/Linux
pip install -r requirements.txt

copy .env.example .env           # macOS/Linux: cp .env.example .env
```

Open `.env` and set your key:

```
GEMMA_API_KEY=your_key_here      # from https://aistudio.google.com/apikey
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

```bash
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/health` — a green `"reachable"` means Gemma is wired up.

### 2 · Frontend

```bash
cd lexi
npm install
npm run dev                      # http://localhost:5173
```

---

## Project structure

```
.
├── lexi-backend-v3/            FastAPI backend
│   ├── app/
│   │   ├── api/                route handlers (one file per endpoint)
│   │   ├── services/           gemma_client · rewrite · verify · qa · document_store
│   │   ├── prompts/            mode rules + few-shot examples (single source of truth)
│   │   ├── schemas/            Pydantic request/response models
│   │   └── config.py           all tunables, loaded from .env
│   └── requirements.txt
│
└── lexi/                       React frontend
    └── src/
        ├── pages/              Landing · About · FAQ · AppPage
        ├── components/         workspace, modes, result view, chat, history…
        └── lib/                api.js (provider isolation) · strings.js (EN/বাংলা)
```

---

<div align="center">

**Lexi** · Reading, on your terms.

</div>
