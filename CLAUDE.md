# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A LaTeX PhD thesis — *The Simulation Bottleneck of Reinforcement Learning* by Samuel Garcin (University of Edinburgh, 2026). It is built on the unofficial Edinburgh `edengths` thesis template (GNU GPL). The repository was seeded from an Overleaf export ("Initial Overleaf Import").

## Building

There is no Makefile or `latexmkrc`; the project is compiled the standard LaTeX way (and on Overleaf, where it originated). The master driver is `edengths.tex` and the output PDF is `edengths.pdf`.

```sh
# Bibliography uses apacite (bibtex, not biber)
latexmk -pdf edengths.tex
# or manually:
pdflatex edengths && bibtex edengths && pdflatex edengths && pdflatex edengths
```

To compile a subset while drafting, uncomment and edit the `\includeonly{...}` line in `edengths.tex`.

## Structure

- `edengths.tex` — master driver: document class options, title/author metadata, the `\include` list of chapters, and the bibliography call. **This is the file that controls what gets compiled.**
- `edengths.cls` — the template class file (upstream `edengths`). Avoid editing unless changing template behaviour.
- `edengfmt.tex` — formatting: page geometry, headers/footers, ToC, line spacing, **and the `hyperref` PDF metadata (`pdftitle`/`pdfauthor`) which must be kept in sync with the title block in `edengths.tex`** when the `hyper` option is active.
- `packages.tex` — user package imports (loaded automatically by the class). Many common packages are already provided by the class — see the list at the top of this file before adding one.
- `defintns.tex` — user-defined macros (`\input` by the driver).
- `bib/edengref.bib` — the single bibliography database. Citation style is `apacite` (`\citep`, APA-style, surname-first).
- `front/` — front matter (`frontmtr.tex`, pre-content title page in `precntnt.tex`, Edinburgh crest images).
- `introduction/`, `conclusions/` — framing chapters authored directly in this repo.

## Chapter model (important)

Each research chapter lives in its own directory and is included via its `preamble.tex`:

- `chapter2_deac/` — Information Specialisation in Learned Representations of Actor-Critic Algorithms
- `chapter3_dred/` — Data-Regularised Environment Design (DRED)
- `chapter4_persist/` — Learning World Models with Persistent Environment Representations (PERSIST)

The `preamble.tex` in each is a `\chapter{...}` heading plus a "Preamble" section that summarises the work, ending with the published paper "reproduced without modification." Each chapter maps to one of the thesis's three "simulation bottleneck" conditions (representations/overfitting → chapter 2, scenario diversity → chapter 3, simulator existence → chapter 4); preserve this narrative framing when editing preambles.

To add a chapter, place its content under a new directory and add an `\include{<dir>/<file>}` to the body of `edengths.tex` in reading order.

### Thesis by publication (embedded papers)

The three research chapters reproduce published papers **verbatim**, so they must render exactly as they do standalone. They are NOT merged as LaTeX source (each is a self-contained conference `\documentclass{article}` with its own styles, `math_commands.tex`, and bibliography — merging would clash and not render identically). Instead each paper is compiled **standalone to a PDF** and embedded page-by-page with `pdfpages`.

- Paper sources live in `chapterN_*/paper/` (extracted from the original submission zips) and are kept **byte-for-byte unmodified**.
- Each paper dir has a thin **build wrapper `_thesis_main.tex`** (the *only* thesis-specific file there). It `\input`s the unmodified `main_text.tex` and applies adjustments without touching the publication. `build_papers.sh` compiles the wrapper **from inside each dir** (relative figure/style/bib paths), producing `chapterN_*/paper/_thesis_main.pdf`.
- The chapter's `preamble.tex` ends with `\clearpage` + `\includepaper{chapterN_*/paper/_thesis_main.pdf}`. `\includepaper` is defined in `defintns.tex` and wraps `\includepdf` (pdfpages, loaded in `packages.tex`). **Tune the A4 fit (`scale`, currently 0.92) in that one macro** — papers are US Letter, the thesis is A4, so pages scale down uniformly.
- **Global page numbering:** the wrappers blank each paper's *own* page number (`\AtBeginDocument{\renewcommand{\thepage}{}}`); the thesis stamps the continuous number via `pagecommand={\thispagestyle{plain}}`. Conference running headers/titles are intentionally left intact.
- **DEAC toolchain fix (chapter 2 wrapper only):** under TeX Live 2026 the kernel's `firstaid/aliascounter` hook for amsthm collides with thmtools 0.76 when the ICLR paper declares `sibling=theorem` lemmas (`\c@lemma already defined`). The wrapper removes that one hook (`\RemoveFromHook{package/amsthm/after}[firstaid/aliascounter]` and the cleveref one). Rendering is unaffected. This is purely a TL2026-vs-Overleaf version skew; it does not occur on the TeX Live the papers were authored against.

**Build order:** run `./build_papers.sh` (rebuild a paper whenever its source changes) *before* `latexmk -pdf edengths.tex` — the thesis depends on the three `_thesis_main.pdf` artifacts existing.

The papers are camera-ready/accepted in their current source (`\iclrfinalcopy`, `[accepted]` for the two ICML papers) — that is the intended rendering.

## Template leftovers — not part of the thesis

These come from the upstream template and are **not** compiled by `edengths.tex`. Do not treat them as thesis content:

- `class_examples/` — alternative `.cls` files the template was derived from.
- `template_chapter1/`, `template_chapter2/` — demo chapters.
- `appendix/edengapp.tex`, `appendix/appendx1.tex` — example appendix scaffolding (the appendix `\include`s are commented out in the driver).
- The CI badges and credits in `README.md` describe the upstream `edengths` project, not this thesis.

Note: `\graphicspath` in `edengths.tex` lists the real content directories, so `\includegraphics` resolves figures from any chapter dir without a path prefix; add new directories there when adding chapters.
