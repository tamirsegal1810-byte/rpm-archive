# Nike SB RPM Master Archive

A **community-driven digital museum** dedicated to the **Nike SB RPM Backpack (2007–Present)**.

🌐 **[View the Live Archive Dashboard](https://rpmarchive.net)**  
Click above to access the visual terminal and search the database.

---

## 📂 Project Structure

| Path | What it is |
|---|---|
| `data/master_metadata.csv` | **The catalog: one row per SKU.** The only place to add or edit a bag. |
| `index.html` | The website. It reads its catalog from the CSV above. |
| `scripts/sku_validator.py` | Checks that every SKU in the CSV is in Nike format (`BA5403-010`). |
| `docs/Methodology.md` | Research notes behind the Year Zero (BA2037) essay. |
| `CNAME` | Serves the site at rpmarchive.net (GitHub Pages). |

### Catalog columns

`sku`, `name`, `era`, `status`, `notes`, then the Dublin Core fields `dc_title` … `dc_rights`, then `colorway` and `rarity`.
Leave a cell empty when it's unknown; the site hides empty fields.

### Checking changes locally

```bash
python3 scripts/sku_validator.py   # every SKU well-formed?
python3 -m http.server             # then open http://localhost:8000
```

The page loads the CSV, so open it through the local server; double-clicking `index.html` won't load the catalog.
