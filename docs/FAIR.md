# longevity-loop — FAIR dataset scorecard

_Generated from `data/datasets.yml` by `scripts/fair.py` — do not edit by hand._

How **FAIR** (Findable · Accessible · Interoperable · Reusable) are the open aging datasets this loop uses? The field lacks shared FAIR/metadata standards for multi-omic aging data (gaps-analysis.md G2), so each dataset is scored on a transparent rubric and the loop prefers to build on the FAIR-est open data.

**Panel FAIR score: 86/100** across 7 datasets. 🟢 yes = 1 · 🟡 partial = 0.5 · 🔴 no = 0. Unknown ⇒ no (never a fake pass).

| Dataset | Access | F | A | I | R | FAIR | How to load |
|---|:--|:-:|:-:|:-:|:-:|--:|---|
| [Tabula Muris Senis](https://registry.opendata.aws/tabula-muris-senis/) | open | 🟢 | 🟢 | 🟢 | 🟢 | 100 | `aws s3 sync s3://czb-tabula-muris-senis/ . --no-sign-request # or figshare download` |
| [Human Cell Atlas](https://data.humancellatlas.org/) | open | 🟢 | 🟢 | 🟢 | 🟢 | 100 | `Browse the Data Portal → download by project UUID (or use the hca-util / matrix API).` |
| [Biomarkers of Aging Challenge (Biolearn)](https://www.longevityprize.com/prize/biomarker) | open | 🟢 | 🟢 | 🟢 | 🟢 | 100 | `pip install biolearn; from biolearn.data_library import DataLibrary # standardized loaders` |
| [HAGR (GenAge / CellAge)](https://genomics.senescence.info/) | open | 🟢 | 🟢 | 🟡 | 🟢 | 88 | `Download GenAge/CellAge CSVs from the HAGR download pages.` |
| [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) | open | 🟢 | 🟢 | 🟡 | 🟡 | 75 | `GEOparse.get_GEO('GSExxxxx') # accession is the stable handle` |
| [GTEx Portal](https://gtexportal.org/) | open | 🟢 | 🟡 | 🟢 | 🟡 | 75 | `Download bulk expression TSVs from the portal; genotypes need dbGaP approval.` |
| [UK Biobank](https://www.ukbiobank.ac.uk/use-our-data/apply-for-access/) | gated | 🟢 | 🔴 | 🟢 | 🟡 | 62 | `Apply for access → analyse on the Research Analysis Platform (not laptop-downloadable).` |

## Per-dataset provenance

### Tabula Muris Senis — FAIR 100/100
- **Access:** open · **License:** CC-BY-4.0
- **Format:** AnnData/h5ad + loom (standard single-cell) · **Persistent id:** AWS Open Data registry + figshare DOI
- **Load:** `aws s3 sync s3://czb-tabula-muris-senis/ . --no-sign-request # or figshare download`
- **Note:** Registered open dataset, open license, standard formats, documented — the FAIR exemplar here.

### Human Cell Atlas — FAIR 100/100
- **Access:** open · **License:** CC-BY-4.0
- **Format:** AnnData/loom (HCA standard schema) · **Persistent id:** HCA project UUIDs
- **Load:** `Browse the Data Portal → download by project UUID (or use the hca-util / matrix API).`
- **Note:** Standardized schema + open license across projects.

### Biomarkers of Aging Challenge (Biolearn) — FAIR 100/100
- **Access:** open · **License:** challenge terms (open, code-only)
- **Format:** standardized methylation/proteomics/outcomes via Biolearn · **Persistent id:** Biolearn dataset ids
- **Load:** `pip install biolearn; from biolearn.data_library import DataLibrary # standardized loaders`
- **Note:** The North-Star leaderboard set; Biolearn gives one standardized loader interface.

### HAGR (GenAge / CellAge) — FAIR 88/100
- **Access:** open · **License:** CC-BY / academic use
- **Format:** CSV/TSV curated tables · **Persistent id:** HAGR entry IDs (stable URLs)
- **Load:** `Download GenAge/CellAge CSVs from the HAGR download pages.`
- **Note:** Curated + documented; custom table schema rather than a community standard (I partial).

### NCBI GEO — FAIR 75/100
- **Access:** open · **License:** US-Gov public domain; per-series terms vary by submitter
- **Format:** varied (submitter-dependent: matrices, CEL, supplementary) · **Persistent id:** GEO GSE / GSM accessions
- **Load:** `GEOparse.get_GEO('GSExxxxx') # accession is the stable handle`
- **Note:** Stable accessions + open access, but format/metadata quality varies per submitter (I/R partial).

### GTEx Portal — FAIR 75/100
- **Access:** open · **License:** GTEx Terms (expression open; genotypes dbGaP-controlled)
- **Format:** TSV expression matrices; VCF (protected) · **Persistent id:** dbGaP phs000424
- **Load:** `Download bulk expression TSVs from the portal; genotypes need dbGaP approval.`
- **Note:** Expression downloads freely; genotype/protected tiers are access-controlled (A/R partial).

### UK Biobank — FAIR 62/100
- **Access:** gated · **License:** UK Biobank Access Agreement (application + fee)
- **Format:** standardized field IDs; cloud-only RAP · **Persistent id:** UKB field IDs / showcase
- **Load:** `Apply for access → analyse on the Research Analysis Platform (not laptop-downloadable).`
- **Note:** Well-documented + standardized, but access-gated (application/fee/cloud-only) — Accessible: no.

---

PR a dataset to `data/datasets.yml` with an honest FAIR self-assessment (unknown ⇒ `no`). Rubric: Findable (persistent id), Accessible (open, no gate), Interoperable (standard format), Reusable (clear license + load recipe).
