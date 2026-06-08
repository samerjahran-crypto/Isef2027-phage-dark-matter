# In silico Functional Annotation of Ocean Bacteriophage Dark Matter

**Mawhiba Ibdaa | Samer Ali Alghamdi**
**Al-Andalus International School, Jeddah, Saudi Arabia**

---

## Core Finding

ESM-2 protein language model embeddings functionally annotate bacteriophage proteins that BLAST cannot find. Nine Red Sea phage proteins from the genuinely novel confidence tier returned **zero BLAST hits in NCBI nr at any e-value threshold**, yet the classifier assigned them to functional categories with confidence above 0.85.

Protein language models operate in the sequence space where homology fails.

---

## Key Results

| Result | Value |
|--------|-------|
| Classifier macro F1 (5-fold CV) | 0.9086 +/- 0.0059 |
| vs k-mer baseline | +0.113 F1 points |
| vs SVM (RBF) | +0.240 F1 points |
| vs Random Forest | +0.389 F1 points |
| Near-relative tier BLAST hit rate (conf >0.99) | 95.6% |
| Genuinely novel tier BLAST hit rate (conf 0.85-0.99) | **0% at any e-value** |
| Two-tier functional gap | +25 to +26 pp stable across cutoffs 0.95-0.999 |
| Permutation test p-value | 0.0000 (n=10,000 shuffles) |

---

## Two-Tier Dark Matter Discovery

| Population | n | BLAST hit rate | Host-interaction % |
|------------|---|----------------|-------------------|
| Near-relatives (conf >0.99) | 135,100 | 95.6% | 82% |
| Genuinely novel (conf 0.85-0.99) | 29,188 | **0%** | 57% |

The depth gradient in host-interaction enrichment (+9pp at surface) is driven by the near-relative population. Genuinely novel proteins show depth-invariant functional composition across all four ocean datasets.

---

## AMR Relevance

Phage therapy against ESBL-producing and carbapenem-resistant bacteria requires knowing which phage proteins mediate host recognition. This project annotates 4,764 host-interaction proteins in the Red Sea genuinely novel tier — proteins with zero sequence homology to anything characterized, now functionally annotated for the first time.

---

## Reproducibility

Models archived at: https://doi.org/10.5281/zenodo.20435564
Web Tool: https://huggingface.co/spaces/Samerjahran/phage-dark-matter-annotator
---

## Ocean Metagenome Datasets

| Dataset | Ocean | Depth | HC Proteins |
|---------|-------|-------|-------------|
| Tara Oceans ERR315858 | Indian Ocean | 0 m | 2,010 |
| Red Sea SRR2102994 | Red Sea | 10 m | 81,359 |
| Malaspina ERR770958 | Atlantic Ocean | 200 m | 5,313 |
| Tara Oceans ERR599370 | Pacific Ocean | 800 m | 118,208 |
