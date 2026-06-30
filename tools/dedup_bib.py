#!/usr/bin/env python3
"""dedup_bib.py - Phase-2 semantic bibliography dedup + conflict detection.

Parses the thesis bib + the three papers' .bib files and finds:
  * exact-key collisions whose CONTENT differs across files (silent conflicts the
    Phase-1 first-occurrence merge hid);
  * different keys that denote the SAME work (matched by normalised title),
    split into:
      - DUPLICATE  : same title + same year + same/again-absent venue
                     -> unify to one key, rewrite the others in the bodies;
      - CONFLICT   : same title but different year/venue/journal
                     -> keep one, the rest go in commented %[REF CONFLICT] blocks.

Report mode (default) prints the groups. With --apply it writes:
  * the deduped bib to --out, and
  * a JSON key-rewrite map {oldkey: newkey} to --rewrite-map
for the body rewriter (tools/rewrite_citekeys.py).

Canonical key preference = source order given on the command line (thesis first).
"""
import argparse
import json
import re
import sys

ENTRY_START = re.compile(r"@(\w+)\s*[{(]\s*([^,\s]+)\s*,", re.IGNORECASE)


def iter_raw(text):
    i, n = 0, len(text)
    while i < n:
        at = text.find("@", i)
        if at == -1:
            return
        m = ENTRY_START.match(text, at)
        if not m:
            i = at + 1
            continue
        open_pos = text.index("{" if "{" in text[at:m.end()] else "(", at)
        opener = text[open_pos]
        closer = "}" if opener == "{" else ")"
        depth, j = 0, open_pos
        while j < n:
            c = text[j]
            if c == opener:
                depth += 1
            elif c == closer:
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        yield (m.group(1), m.group(2), text[at:j])
        i = j


def parse_fields(raw):
    """Extract a {fieldname: value} dict from an entry's raw text (brace-aware)."""
    # strip the "@type{key," head and trailing "}"
    head = ENTRY_START.match(raw)
    body = raw[head.end():]
    body = body.rsplit("}", 1)[0] if "}" in body else body
    fields = {}
    i, n = 0, len(body)
    while i < n:
        # field name
        m = re.match(r"\s*([A-Za-z][\w-]*)\s*=\s*", body[i:])
        if not m:
            break
        name = m.group(1).lower()
        i += m.end()
        if i >= n:
            break
        if body[i] == "{":
            depth, j = 0, i
            while j < n:
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
                j += 1
            val = body[i + 1:j - 1]
            i = j
        elif body[i] == '"':
            j = i + 1
            while j < n and body[j] != '"':
                j += 1
            val = body[i + 1:j]
            i = j + 1
        else:
            j = i
            while j < n and body[j] != ",":
                j += 1
            val = body[i:j].strip()
            i = j
        fields[name] = " ".join(val.split())
        # skip to next comma
        while i < n and body[i] != ",":
            i += 1
        i += 1
    return fields


def norm_title(s):
    s = re.sub(r"[{}\\]", "", s or "")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return s.strip()


def norm_venue(f):
    v = f.get("booktitle") or f.get("journal") or f.get("publisher") or ""
    v = re.sub(r"[{}\\]", "", v).lower()
    v = re.sub(r"\b(proceedings|conference|the|on|of|in|advances|neural information processing systems)\b", " ", v)
    return re.sub(r"[^a-z0-9]+", " ", v).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--rewrite-map")
    args = ap.parse_args()

    # parse all, remember source order/priority
    kept = {}          # lowerkey -> entry dict (first occurrence)
    same_key_conflicts = []   # (key, [raw variants])
    order = []         # lowerkeys in kept order
    for src in args.inputs:
        text = open(src, encoding="utf-8", errors="replace").read()
        for typ, key, raw in iter_raw(text):
            lk = key.lower()
            fields = parse_fields(raw)
            ent = dict(key=key, lk=lk, type=typ.lower(), fields=fields, raw=raw.strip(), src=src)
            if lk not in kept:
                kept[lk] = ent
                order.append(lk)
            else:
                prev = kept[lk]
                # same key, different content?
                if norm_title(prev["fields"].get("title", "")) != norm_title(fields.get("title", "")):
                    same_key_conflicts.append((key, prev, ent))
    # group kept by normalised title
    by_title = {}
    for lk in order:
        e = kept[lk]
        t = norm_title(e["fields"].get("title", ""))
        if not t:
            continue
        by_title.setdefault(t, []).append(e)

    duplicates, conflicts = [], []
    for t, group in by_title.items():
        if len(group) < 2:
            continue
        canon = group[0]
        cy, cv = canon["fields"].get("year", ""), norm_venue(canon["fields"])
        is_conflict = False
        for e in group[1:]:
            ey, ev = e["fields"].get("year", ""), norm_venue(e["fields"])
            if (ey and cy and ey != cy) or (ev and cv and ev != cv):
                is_conflict = True
        (conflicts if is_conflict else duplicates).append(group)

    # ---- report ----
    def fmt(e):
        f = e["fields"]
        return f"{e['key']:35s} [{e['type']}] y={f.get('year','?')} venue={norm_venue(f) or '-'}  ({e['src'].split('/')[0]})"

    print(f"== Parsed {len(kept)} unique-key entries from {len(args.inputs)} files ==\n")
    print(f"-- SAME-KEY, DIFFERENT TITLE (hidden conflicts): {len(same_key_conflicts)} --")
    for key, a, b in same_key_conflicts:
        print(f"  {key}: '{a['fields'].get('title','')[:50]}' vs '{b['fields'].get('title','')[:50]}'")
    print(f"\n-- DIFFERENT-KEY DUPLICATES (same work, unify): {len(duplicates)} groups --")
    for g in duplicates:
        print(f"  title: {g[0]['fields'].get('title','')[:70]}")
        for e in g:
            print(f"      {fmt(e)}")
    print(f"\n-- CONFLICTS (same title, different venue/year): {len(conflicts)} groups --")
    for g in conflicts:
        print(f"  title: {g[0]['fields'].get('title','')[:70]}")
        for e in g:
            print(f"      {fmt(e)}")

    if args.apply:
        rewrite = {}
        drop = set()
        conflict_alts = {}   # canon_lk -> [alt entries]
        for g in duplicates:
            canon = g[0]
            for e in g[1:]:
                rewrite[e["key"]] = canon["key"]
                drop.add(e["lk"])
        for g in conflicts:
            canon = g[0]
            alts = []
            for e in g[1:]:
                rewrite[e["key"]] = canon["key"]
                drop.add(e["lk"])
                alts.append(e)
            conflict_alts[canon["lk"]] = alts
        # write deduped bib
        with open(args.out, "w", encoding="utf-8") as out:
            out.write("%% AUTO-GENERATED by tools/dedup_bib.py -- Phase-2 deduped bibliography.\n")
            out.write("%% Exact-dup keys removed; same-work-different-key entries unified\n")
            out.write("%% (citations rewritten in the bodies); same-title-different-venue\n")
            out.write("%% conflicts kept adjacent, all but one commented as %[REF CONFLICT].\n\n")
            for lk in order:
                if lk in drop:
                    continue
                e = kept[lk]
                out.write(e["raw"] + "\n\n")
                if lk in conflict_alts:
                    out.write("%[REF CONFLICT] Alternate entry/entries for the title above (same work,\n")
                    out.write("%[REF CONFLICT] different venue/year). BibTeX ignores the @comment{...} wrapper;\n")
                    out.write("%[REF CONFLICT] to use one instead, lift it out of the wrapper, wrap the active\n")
                    out.write("%[REF CONFLICT] entry above, and recheck citations. NB: '%' does NOT comment out\n")
                    out.write("%[REF CONFLICT] a bib entry -- the @comment{} wrapper is what disables it.\n")
                    for alt in conflict_alts[lk]:
                        out.write("@comment{\n" + alt["raw"] + "\n}\n\n")
        with open(args.rewrite_map, "w", encoding="utf-8") as mf:
            json.dump(rewrite, mf, indent=2, ensure_ascii=False)
        print(f"\nAPPLIED: wrote {args.out} ({len(order)-len(drop)} entries) and "
              f"{args.rewrite_map} ({len(rewrite)} key rewrites).")


if __name__ == "__main__":
    main()
