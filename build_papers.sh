#!/usr/bin/env bash
#
# build_papers.sh — compile each published paper standalone to a PDF that the
# thesis embeds verbatim via \includepaper (pdfpages). Run this BEFORE compiling
# edengths.tex, and again whenever a paper's source changes.
#
# Each paper lives in its own directory with its own conference .sty/.bst/.bib and
# figures, so it must be compiled from inside that directory (relative paths).
#
# Usage:  ./build_papers.sh            # build all three
#         ./build_papers.sh chapter3_dred   # build just one
set -euo pipefail

PAPERS=(chapter2_deac chapter3_dred chapter4_persist)
[ "$#" -gt 0 ] && PAPERS=("$@")

root="$(cd "$(dirname "$0")" && pwd)"
for ch in "${PAPERS[@]}"; do
  dir="$root/$ch/paper"
  echo "==== building $ch/paper/main_text.pdf ===="
  ( cd "$dir" && latexmk -pdf -interaction=nonstopmode -halt-on-error main_text.tex )
  echo "==== done: $ch/paper/main_text.pdf ===="
done
echo "All requested papers built. Now compile the thesis: latexmk -pdf edengths.tex"
