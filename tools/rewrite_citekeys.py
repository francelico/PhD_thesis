#!/usr/bin/env python3
"""rewrite_citekeys.py - rewrite citation keys in .tex bodies per a dedup map.

Replaces old citation keys with their canonical equivalents (from a JSON map
produced by tools/dedup_bib.py) inside cite-family commands only, matching each
key as a COMPLETE token in the comma-separated key list -- never as a substring
(critical: keys like "DR", "ted", "pse" must not corrupt "DRED", "rejected",...).
Optional cite arguments (\citep[see][p.3]{key}) are preserved.

Usage: rewrite_citekeys.py --map MAP.json FILE [FILE ...]
"""
import argparse
import json
import re

# cite-family commands (apacite / natbib), starred or not, with up to two
# optional bracket arguments before the mandatory key list.
CITE = re.compile(
    r"(\\(?:[Cc]ite[a-zA-Z]*|nocite|fullcite)\*?(?:\[[^\]]*\])?(?:\[[^\]]*\])?)\{([^}]*)\}"
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()
    mapping = json.load(open(args.map, encoding="utf-8"))

    total = 0
    for path in args.files:
        text = open(path, encoding="utf-8").read()
        n = [0]

        def repl(m):
            head, keys = m.group(1), m.group(2)
            out = []
            for tok in keys.split(","):
                k = tok.strip()
                if k in mapping:
                    n[0] += 1
                    lead = tok[: len(tok) - len(tok.lstrip())]
                    trail = tok[len(tok.rstrip()):]
                    out.append(f"{lead}{mapping[k]}{trail}")
                else:
                    out.append(tok)
            return head + "{" + ",".join(out) + "}"

        new = CITE.sub(repl, text)
        if new != text:
            open(path, "w", encoding="utf-8").write(new)
        print(f"{path}: {n[0]} key(s) rewritten")
        total += n[0]
    print(f"total: {total}")


if __name__ == "__main__":
    main()
