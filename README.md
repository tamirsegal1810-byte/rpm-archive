# Nike SB RPM Archive

A documentary corpus of the Nike SB bags line (the RPM backpack and the models released alongside it), built from primary evidence: interior labels, construction, and dated sources.

**Site:** [rpmarchive.net](https://rpmarchive.net)

## How the record is organised

Evidence and argument are kept in separate files. A bag is recorded once, as what was observed; anything argued about it (its date, its period, its place in a sequence) lives in a claim that cites it.

| File | One row per | What it holds |
|---|---|---|
| `corpus/rpm-units.csv` | physical bag | Witness record transcribed from the interior label, plus construction and custody. `unit_id` is `RPM-UNIT-NNN`. |
| `corpus/rpm-codes.csv` | base style code (e.g. `BA2037`) | Code register, aggregated from units. A code enters only when a unit carries a label photograph (`attested`) or a dated source reports it (`reported`). |
| `corpus/rpm-sources.csv` | dated document | Shop pages, period media, catalogues, listings. `RPM-SOURCE-NNN`. |
| `corpus/rpm-claims.csv` | argument | Dating, periodisation, sequence, attribution. Cites `unit_id`s; a claim that cites none is `speculative`. Retracted claims stay. `RPM-CLAIM-NNN`. |
| `corpus/rpm-gaps.csv` | documented absence | What is missing, what would close it, where it has been searched, when. `RPM-GAP-NNN`. |
| `corpus/rpm-sessions.csv` | work session | Session log; `next_action` is the load-bearing field. |
| `legacy/catalog.csv` | style code | The catalog published before 1 October 2026. Not corpus: nothing in it is backed by a logged unit or source. A row leaves when its first unit is logged. |

The column sets are the canonical schemas from the project's intake system. These repository files are the canonical corpus; the header-only copies in the Drive folder `01-corpus` are retired (a note there points here). Photographs stay in Drive. Leave a field empty when it was not read; write `[confirm]` for a field still to be read and `[infer]` for one taken from context. Both markers are meant to stay in place and show on the site as small flags.

The three dates never share a column: `production_date` (from the label, on the unit), `release_date` (from a dated source, on the code), `first_documented` (earliest dated mention).

## The site

`index.html` reads the corpus CSVs directly and joins them in the browser. There is no build step and nothing to keep running.

Every record has one address, the same in both reading modes:

- `#/unit/RPM-UNIT-001`: a physical bag, the archive's basic unit. The address is stable, but the record behind it changes as the CSVs change.
- `#/code/BA2037`: all units, register entries and legacy rows under one base code.
- `#/claim/RPM-CLAIM-001`, `#/gap/RPM-GAP-001`, `#/source/RPM-SOURCE-001`
- `#/legacy/BA2037-089`: a pre-corpus entry.
- Old `#/record/<sku>` links redirect to the unit, the code page, or the legacy entry.

**General** mode shows the bag, and only units that a live claim cites. **Scholarly** mode shows the full witness record, every unit, the claims, gaps and sources, and the `[confirm]` flags.

Label photographs go in `photos/labels/`, hangtags in `photos/hangtags/`, with the file named after the unit (`RPM-UNIT-001.jpg`). A whole-bag photo goes in `photos/construction/<unit_id>-bag.jpg` and shows on the unit page in both modes. The unit's `label_photo` field holds the file name. A code counts as `attested` only when a witness unit's label photograph is published here, so anyone can trace a claim to the unit, the photograph and the transcription without access to private storage. Full-resolution originals stay in Drive.

### Citing

Each record page gives a citation with its address, the corpus version (the last commit that changed `corpus/`, linked to that commit's frozen copy of the files) and the access date. The version is what pins the exact text cited. A tagged release with a Zenodo DOI will follow once the first units are logged.

## Logging a unit

1. Photograph the interior label (and hangtag, if present). Put the label crop in `photos/labels/<unit_id>.jpg`.
2. Add one row to `corpus/rpm-units.csv`: label fields first, in the fixed reading order, then construction. Declare custody.
3. If this is the first photographed unit of its code, add or update the code's row in `corpus/rpm-codes.csv`.
4. If the code was in `legacy/catalog.csv`, delete that row.
5. Add a session row.

## Checking changes

```bash
python3 scripts/check_corpus.py   # schemas, ids, references, public-witness rule, construction fields
python3 -m http.server            # then open http://localhost:8000
```

The page loads the CSVs, so open it through a server; double-clicking `index.html` won't load them. The check is optional: the site does not depend on it.

## Other files

| Path | What it is |
|---|---|
| `docs/Methodology.md` | Research notes behind the Year Zero (BA2037) essay. |
| `CNAME` | Serves the site at rpmarchive.net (GitHub Pages). |

An independent collector's archive, not affiliated with Nike, Inc.
