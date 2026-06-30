#!/usr/bin/env python3
"""integrate_paper.py - mechanical passes for embedding a paper into the thesis.

Operates IN PLACE on a paper source file (main_text.tex / supplementary.tex),
applying the two deterministic transformations that are too error-prone to do by
hand across a 1000+ line file:

  1. Per-chapter label/cross-reference prefixing. Every \\label key and every key
     inside a cross-reference command is prefixed with e.g. ``c3:`` so the three
     papers (which all reuse fig:/sec:/eq:/tab:/app:/...) do not collide in the
     single merged thesis. Comma-lists (\\cref{a,b}) and range commands
     (\\crefrange{a}{b}) are handled key-by-key. Citation commands (\\cite*) are
     left untouched -- bibliography keys are a separate workstream.

  2. Full-width float un-starring: \\begin{figure*}/\\begin{table*} -> figure/table
     (single-column thesis: a normal float already spans the full text block).
     Subfigure GRID contents inside are left intact; only the star is dropped.

wrapfigure -> figure conversion is done separately by hand (only 4, each needs a
width check), so it is NOT handled here.

Usage:
    integrate_paper.py --prefix c3 [--dry-run] FILE [FILE ...]

Re-running double-prefixes, so run exactly once per file (git is the safety net).
"""
import argparse
import re
import sys

# Cross-ref commands whose single brace argument is a (possibly comma-separated)
# list of label keys.
LIST_CMDS = [
    "cref", "Cref", "crefrange",  # crefrange handled below as 2-arg; listed for ordering
    "ref", "autoref", "eqref", "pageref", "nameref",
    "labelcref", "cpageref", "Cpageref", "vref", "Vref",
]
# (cref/Cref must be matched before ref so the regex alternation is greedy-correct;
#  we build an explicit alternation ordered longest-first below.)
SINGLE_ARG_CMDS = [
    "labelcref", "autoref", "nameref", "pageref",
    "cpageref", "Cpageref", "eqref",
    "Cref", "cref", "Vref", "vref", "ref",
]
RANGE_CMDS = ["cpagerefrange", "Cpagerefrange", "crefrange", "Crefrange"]


def prefix_keylist(keys: str, prefix: str) -> str:
    """Prefix each comma-separated key, preserving surrounding whitespace."""
    out = []
    for tok in keys.split(","):
        stripped = tok.strip()
        if not stripped:
            out.append(tok)
            continue
        lead = tok[: len(tok) - len(tok.lstrip())]
        trail = tok[len(tok.rstrip()):]
        out.append(f"{lead}{prefix}:{stripped}{trail}")
    return ",".join(out)


def transform(text: str, prefix: str):
    counts = {"label": 0, "ref": 0, "range": 0, "hyperref": 0, "figstar": 0, "tabstar": 0}

    # 1. \label{...}
    def repl_label(m):
        counts["label"] += 1
        return f"\\label{{{prefix}:{m.group(1).strip()}}}"
    text = re.sub(r"\\label\{([^}]*)\}", repl_label, text)

    # 2. range commands: \crefrange{a}{b} (two single-key args)
    range_alt = "|".join(RANGE_CMDS)
    def repl_range(m):
        counts["range"] += 1
        a, b = m.group(2).strip(), m.group(3).strip()
        return f"\\{m.group(1)}{{{prefix}:{a}}}{{{prefix}:{b}}}"
    text = re.sub(r"\\(" + range_alt + r")\*?\{([^}]*)\}\{([^}]*)\}", repl_range, text)

    # 3. single-arg (comma-list) cross-ref commands. Ordered longest-first so e.g.
    #    \Cref is not partially matched by \ref.
    single_alt = "|".join(SINGLE_ARG_CMDS)
    def repl_single(m):
        counts["ref"] += 1
        star = m.group(2) or ""
        return f"\\{m.group(1)}{star}{{{prefix_keylist(m.group(3), prefix)}}}"
    text = re.sub(r"\\(" + single_alt + r")(\*?)\{([^}]*)\}", repl_single, text)

    # 4. \hyperref[key]{text}
    def repl_hyperref(m):
        counts["hyperref"] += 1
        return f"\\hyperref[{prefix}:{m.group(1).strip()}]"
    text = re.sub(r"\\hyperref\[([^\]]*)\]", repl_hyperref, text)

    # 5. full-width floats -> normal floats (keep grid contents)
    text, n = re.subn(r"(\\(?:begin|end)\{figure)\*\}", r"\1}", text)
    counts["figstar"] = n
    text, n = re.subn(r"(\\(?:begin|end)\{table)\*\}", r"\1}", text)
    counts["tabstar"] = n

    return text, counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", required=True, help="chapter prefix, e.g. c3")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()

    for path in args.files:
        with open(path, encoding="utf-8") as f:
            original = f.read()
        new, counts = transform(original, args.prefix)
        summary = ", ".join(f"{k}={v}" for k, v in counts.items())
        action = "DRY-RUN" if args.dry_run else "wrote"
        print(f"[{args.prefix}] {action} {path}: {summary}")
        if not args.dry_run and new != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)


if __name__ == "__main__":
    main()
