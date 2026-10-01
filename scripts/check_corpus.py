#!/usr/bin/env python3
"""Integrity check for the RPM archive corpus.

Run from the repository root:  python3 scripts/check_corpus.py

The site does not depend on this script; it reads the CSVs directly. The check
exists to catch the failures the archive's rules forbid before they reach the
site: a code without a witness, a claim citing a unit that does not exist, an
in-hand unit without construction fields, a gap closed by nothing.

Exit status 0 when there are no errors (warnings are allowed), 1 otherwise.
Standard library only.
"""
import csv
import os
import re
import sys

SCHEMA = {
    "corpus/rpm-units.csv": ["unit_id", "model_name", "style_code", "color_suffix", "colorway_name", "production_date", "factory_code", "label_photo", "label_form_notes", "hangtag", "hangtag_photo", "qr_sticker", "custody", "source_ref", "first_documented", "observed_date", "body_material", "print_motif", "modular_attachment", "molle", "padding", "hardware", "region_labels", "condition", "notes"],
    "corpus/rpm-codes.csv": ["style_code", "model_name", "status", "release_date", "release_source_id", "first_documented", "first_documented_source_id", "color_suffixes_observed", "production_dates_observed", "factories_observed", "unit_count", "witness_unit_ids", "period_assignment", "notes"],
    "corpus/rpm-sources.csv": ["source_id", "source_type", "publisher", "url", "archived_url", "publication_date", "accessed_date", "attests", "style_codes_named", "model_names_named", "earliest_known_for", "notes"],
    "corpus/rpm-gaps.csv": ["gap_id", "gap_type", "span", "description", "what_would_close_it", "searched_where", "last_searched", "status", "closed_by"],
    "corpus/rpm-claims.csv": ["claim_id", "statement", "claim_type", "evidence_unit_ids", "evidence_source_ids", "construction_criterion", "status", "confidence", "raised_date", "superseded_by", "notes"],
    "corpus/rpm-sessions.csv": ["session_date", "units_added", "units_edited", "codes_touched", "gaps_opened", "gaps_closed", "claims_changed", "minutes", "next_action", "notes"],
    "legacy/catalog.csv": ["sku", "name", "era", "status", "colorway", "notes", "corpus_note"],
}
CUSTODY = {"in_hand", "incoming", "watching", "observed_listing", "observed_thirdparty", "cancelled"}
CONSTRUCTION = ["body_material", "print_motif", "modular_attachment", "molle", "padding", "hardware"]
CODE_STATUS = {"attested", "reported"}
CLAIM_STATUS = {"speculative", "open", "supported", "superseded", "retracted"}
GAP_STATUS = {"open", "closed"}
MARK = re.compile(r"\[(confirm|infer)\]")

errors, warnings = [], []


def err(where, msg):
    errors.append(f"ERROR  {where}: {msg}")


def warn(where, msg):
    warnings.append(f"warn   {where}: {msg}")


def clean(value):
    return MARK.sub("", value or "").strip()


def ids(value):
    return [x for x in re.split(r"[;,\s]+", clean(value)) if x]


def load(path):
    if not os.path.exists(path):
        err(path, "file missing")
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        header = [h.strip() for h in (reader.fieldnames or [])]
        if header != SCHEMA[path]:
            err(path, f"header does not match the schema.\n         expected: {','.join(SCHEMA[path])}\n         found:    {','.join(header)}")
        rows = []
        for n, row in enumerate(reader, start=2):
            if None in row:
                err(f"{path} line {n}", "more cells than columns (unquoted comma?)")
            rows.append({k.strip(): (v or "").strip() for k, v in row.items() if k is not None})
            rows[-1]["_line"] = n
        return rows


def check_ids(path, rows, key, pattern):
    seen = set()
    for r in rows:
        where = f"{path} line {r['_line']}"
        value = r.get(key, "")
        if not re.fullmatch(pattern, value):
            err(where, f"{key} '{value}' does not match {pattern}")
        if value in seen:
            err(where, f"duplicate {key} '{value}'")
        seen.add(value)
    return seen


def main():
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    units = load("corpus/rpm-units.csv")
    codes = load("corpus/rpm-codes.csv")
    sources = load("corpus/rpm-sources.csv")
    gaps = load("corpus/rpm-gaps.csv")
    claims = load("corpus/rpm-claims.csv")
    load("corpus/rpm-sessions.csv")
    legacy = load("legacy/catalog.csv")

    unit_ids = check_ids("rpm-units", units, "unit_id", r"RPM-UNIT-\d{3}")
    source_ids = check_ids("rpm-sources", sources, "source_id", r"RPM-SOURCE-\d{3}")
    claim_ids = check_ids("rpm-claims", claims, "claim_id", r"RPM-CLAIM-\d{3}")
    check_ids("rpm-gaps", gaps, "gap_id", r"RPM-GAP-\d{3}")
    by_unit = {u["unit_id"]: u for u in units}

    def has_photo(unit):
        return bool(clean(unit.get("label_photo", "")))

    for u in units:
        where = f"rpm-units {u['unit_id']}"
        custody = u["custody"]
        if custody not in CUSTODY:
            err(where, f"custody '{custody}' must be declared as one of {sorted(CUSTODY)}")
        date = u["production_date"]
        if date and not re.fullmatch(r"(\d{2}/\d{4})?\s*(\[(confirm|infer)\])?", date):
            err(where, f"production_date '{date}' is not MM/YYYY")
        if custody == "in_hand":
            missing = [f for f in CONSTRUCTION if not u[f]]
            if missing:
                err(where, f"in_hand unit is missing construction fields: {', '.join(missing)} (use [confirm] if not yet read)")
        if not has_photo(u):
            warn(where, "no label photograph recorded")
        else:
            photo = clean(u["label_photo"])
            path = photo if "/" in photo else os.path.join("photos", "labels", photo)
            if not os.path.exists(path):
                warn(where, f"label photograph '{photo}' is not in the repository (fine if it lives in Drive; the site will not show it)")
        ref = clean(u["source_ref"])
        if ref.startswith("RPM-SOURCE-") and ref not in source_ids:
            err(where, f"source_ref '{ref}' does not exist")

    for c in codes:
        where = f"rpm-codes {c['style_code'] or 'line ' + str(c['_line'])}"
        status = clean(c["status"])
        witnesses = ids(c["witness_unit_ids"])
        for w in witnesses:
            if w not in by_unit:
                err(where, f"witness '{w}' is not a logged unit")
        for key in ("release_source_id", "first_documented_source_id"):
            s = clean(c[key])
            if s and s not in source_ids:
                err(where, f"{key} '{s}' does not exist")
        if status not in CODE_STATUS:
            err(where, f"status '{c['status']}' must be one of {sorted(CODE_STATUS)}")
        elif status == "attested" and not any(w in by_unit and has_photo(by_unit[w]) for w in witnesses):
            err(where, "attested, but no witness unit carries a label photograph (no code without a witness)")
        elif status == "reported" and not (clean(c["release_source_id"]) or clean(c["first_documented_source_id"])):
            err(where, "reported, but no source_id points at dated documentary evidence")

    for c in claims:
        where = f"rpm-claims {c['claim_id']}"
        status = clean(c["status"])
        if status not in CLAIM_STATUS:
            err(where, f"status '{c['status']}' must be one of {sorted(CLAIM_STATUS)}")
        cited = ids(c["evidence_unit_ids"])
        for x in cited:
            if x not in unit_ids:
                err(where, f"cites unit '{x}', which is not logged")
        for x in ids(c["evidence_source_ids"]):
            if x not in source_ids:
                err(where, f"cites source '{x}', which does not exist")
        if not cited and status in {"open", "supported"}:
            err(where, f"status '{status}' but cites no unit_ids; a claim that cannot cite units is speculative")
        sup = clean(c["superseded_by"])
        if sup and sup not in claim_ids:
            err(where, f"superseded_by '{sup}' does not exist")

    for g in gaps:
        where = f"rpm-gaps {g['gap_id']}"
        status = clean(g["status"])
        if status not in GAP_STATUS:
            err(where, f"status '{g['status']}' must be open or closed")
        closer = clean(g["closed_by"])
        if status == "closed" and closer not in unit_ids | source_ids:
            err(where, "closed, but closed_by does not name a logged unit or source")

    unit_codes = set()
    for u in units:
        s, x = clean(u["style_code"]), clean(u["color_suffix"])
        unit_codes.add(f"{s}-{x}" if s and x and "-" not in s else s)
    seen = set()
    for r in legacy:
        where = f"legacy {r['sku'] or 'line ' + str(r['_line'])}"
        if not re.fullmatch(r"[A-Z]{2}\d{4}-\d{3}", r["sku"]):
            err(where, "sku is not in Nike format (BA5403-010)")
        if r["sku"] in seen:
            err(where, "duplicate sku")
        seen.add(r["sku"])
        if r["sku"] in unit_codes:
            warn(where, "a unit with this code is now logged; retire the register row")

    for line in errors + warnings:
        print(line)
    print(f"\n{len(units)} units, {len(codes)} codes, {len(sources)} sources, {len(claims)} claims, {len(gaps)} gaps, {len(legacy)} pre-corpus rows.")
    print(f"{len(errors)} errors, {len(warnings)} warnings.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
