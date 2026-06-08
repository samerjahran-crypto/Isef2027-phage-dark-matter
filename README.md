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
| Classifier macro F1 (5-fold CV) | 0.9086 ± 0.0059 |
| vs k-mer baseline | +0.113 F1 points |
| vs SVM (RBF) | +0.240 F1 points |
| vs Random Forest | +0.389 F1 points |
| External validation accuracy (n=200) | 100.0% (macro F1 = 1.0000) |
| Near-relative tier BLAST hit rate (conf >0.99) | 95.6% |
| Genuinely novel tier BLAST hit rate (conf 0.85-0.99) | 44.0% (56% dark fraction, 95% CI 47–65%) |
| Structural validation: zero-homology proteins matched known folds | 17/17 (100% concordance) |
| Two-tier functional gap | +25 to +26 pp stable across cutoffs 0.95–0.999 |
| Permutation test p-value | p<0.0001 (n=10,000 shuffles) |

---

## Two-Tier Dark Matter Discovery

| Population | n | BLAST hit rate | Host-interaction % |
|------------|---|----------------|-------------------|
| Near-relatives (conf >0.99) | 135,100 | 95.6% | 82% |
| Genuinely novel (conf 0.85–0.99) | 29,188 | 44.0% | 57% |

Note: The 0% BLAST hit rate in the Core Finding refers to the structural validation subset (n=9), not the full genuinely novel tier. The full tier BLAST hit rate is 44.0% (95% CI 47–65%), confirming a 56% dark fraction with no homology to any characterized protein.

The depth gradient in host-interaction enrichment (+9pp at surface, p<0.0001) is driven by the near-relative population. Genuinely novel proteins show depth-invariant functional composition across all four ocean datasets.

---

## AMR Relevance

Phage therapy against ESBL-producing and carbapenem-resistant bacteria requires knowing which phage proteins mediate host recognition. This project annotates 4,764 host-interaction proteins in the Red Sea genuinely novel tier — proteins with zero sequence homology to anything characterized, now functionally annotated for the first time.

---

## AMR Candidate: k99_19554_1

| Evidence | Result |
|----------|--------|
| BLAST hits | Zero (viral + bacterial databases) |
| ESMFold pLDDT | 88.2 |
| Foldseek CcmB match | Probability 1.0 |
| TM helices (Phobius) | 7 predicted |
| GRAVY score | 1.335 (membrane protein) |
| ESM-2 prediction | host_interaction, 93.6% confidence |
| RNA-seq validation | Hemin transport upregulated in CRE Klebsiella ST258 (PMID 29669884) |

---

## Benchmark vs Pharokka

Pharokka v1.9.1 (PHROGs + CARD + VFDB) was run on the target contig containing k99_19554_1. Pharokka annotated 1/2 genes (50%) and missed k99_19554_1 entirely — no genes called, no functions assigned on that contig. ESM-2 successfully classified k99_19554_1 as host_interaction at 93.6% confidence. Sequence-alignment tools are blind to proteins with zero homology; embedding-based methods are not.

---

## Reproducibility

Models archived at: https://doi.org/10.5281/zenodo.20435564

Web Tool: https://huggingface.co/spaces/Samerjahran/phage-dark-matter-annotator

GitHub: https://github.com/samerjahran-crypto/Isef2027-phage-dark-matter

---

## Ocean Metagenome Datasets

| Dataset | Ocean | Depth | HC Proteins |
|---------|-------|-------|-------------|
| Tara Oceans ERR315858 | Indian Ocean | 0 m | 2,010 |
| Red Sea SRR2102994 | Red Sea | 10 m | 81,359 |
| Malaspina ERR770958 | Atlantic Ocean | 200 m | 5,313 |
| Tara Oceans ERR599370 | Pacific Ocean | 800 m | 118,208 |
| Tara Oceans ERR599376 | Pacific Ocean | Surface | In progress |
