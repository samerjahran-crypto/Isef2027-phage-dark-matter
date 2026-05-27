# In Silico Functional Annotation of the Ocean Bacteriophage Dark Matter Proteome
### A Protein Language Model Framework for Marine Viromics

**Samer Ali Saeed Alghamdi** | Jeddah, Saudi Arabia  
ISEF 2027 — Computational Biology & Bioinformatics  
📧 samerjahran@gmail.com

---

> **70% of marine phage proteins are functionally unknown.**  
> This project uses protein language model embeddings to illuminate that darkness  
> and finds that the surface ocean selects for a strikingly different viral strategy.

---

## The Problem

Marine bacteriophages are the most abundant biological entities on Earth (~10³¹ particles), killing 20–40% of marine bacteria daily. Despite exponential growth in ocean sequencing, approximately 70% of phage proteins have no detectable homology to any characterized sequence the viral "dark matter." Traditional BLAST-based annotation fails here by design: these proteins are too evolutionarily distant.

## The Approach

Rather than searching for sequence similarity, this project embeds proteins into a **480-dimensional biological meaning space** using ESM-2 (Lin et al. 2023, *Science*)  a protein language model trained on 250 million sequences. Functionally related proteins cluster in this space regardless of sequence identity.

An MLP classifier trained on 43,475 VOG-labeled phage proteins achieves **Macro F1 = 0.917** across four functional classes, then predicts function for **184,394 uncharacterized proteins** from NCBI RefSeq the largest phage dark matter functional atlas produced to date.

## Key Finding: Surface Ocean Phage Ecology

Three independent datasets converge on the same signal:

| Functional Class | Global Baseline | Tara Oceans (ERR315858) | Red Sea (SRR2102994) |
|-----------------|----------------|--------------------------|----------------------|
| host_interaction | 77.8% | **87.2%** *** | **86.8%** *** |
| structural | 10.0% | **3.8%** *** | **5.1%** *** |
| replication | 9.0% | 8.1% ns | 7.2% *** |
| transcription | 3.1% | 0.9% *** | 0.9% *** |

*p < 0.001 after Bonferroni correction. Red Sea and Tara Oceans show nearly identical composition despite different oceans, sequencing platforms, and assembly pipelines.*

**Interpretation:** Surface ocean oligotrophy selects for host versatility over structural complexity  consistent with kill-the-winner dynamics (Thingstad 2000) and nutrient-constrained capsid economics.

## Classifier Performance

| Feature Set | Macro F1 | Notes |
|-------------|----------|-------|
| **ESM-2 embeddings (this work)** | **0.917** | |
| k-mer frequencies | 0.804 | Sequence statistics only |
| Amino acid composition | 0.680 | Sequence statistics only |
| Length only | 0.208 | Trivial baseline |
| Shuffled labels | 0.208 | Permutation control |
| Random embeddings | 0.208 | Embedding control |

The controls confirm ESM-2 captures genuine biological signal, not sequence artifacts.

## BLAST Validation

Representative high-confidence predictions were BLASTed against NCBI nr and Swiss-Prot:

- **BLAST nr:** All four classes confirmed by homology  
  *(e.g., transcription → Holliday junction resolvases; structural → phage coat proteins; replication → DNA pilot protein VP2)*
- **BLAST Swiss-Prot:** Zero hits across all classes

These proteins are validated by database homology but have never been experimentally characterized — confirming genuine novelty.

## Pipeline Overview

```
RefSeq phage genomes
       │
       ▼
 CD-HIT clustering (90% identity)
       │
       ├──► VOG-labeled (43,475)  ──► ESM-2 embeddings ──► MLP training (F1=0.917)
       │                                                          │
       └──► Dark matter (184,394) ──► ESM-2 embeddings ──► Prediction (164,288 HC)
                                                                  │
                                              ┌───────────────────┼───────────────────┐
                                              ▼                   ▼                   ▼
                                        Global atlas       Tara Oceans          Red Sea
                                        (RefSeq)          ERR315858            SRR2102994
                                                          Indian Ocean          KAUST data
                                              └───────────────────┴───────────────────┘
                                                         Z-tests + Bonferroni correction
                                                    → Convergent surface ocean ecology signal
```

## Repository Contents

```
public-repo/
├── README.md                  ← You are here
├── demo/
│   ├── embed_and_predict.py   ← Predict function for your own proteins (demo)
│   └── example_proteins.faa   ← 10 example sequences to test
├── methods/
│   └── methods_overview.md    ← Detailed methods without full pipeline code
└── figures/
    ├── fig_ablation.png        ← Ablation study results
    ├── fig_three_dataset.png   ← Hero three-dataset comparison
    └── fig_confusion_matrix.png
```

> **Note:** Full pipeline notebooks and raw analysis code are held in a private repository  
> and will be made public following competition submission (September 2026).  
> Pre-trained models will be deposited to Zenodo with a citable DOI at that time.

## Methods Summary

**Protein embedding:** ESM-2 `esm2_t12_35M_UR50D`, 480-dimensional mean-pooled representations  
**Classifier:** `sklearn.neural_network.MLPClassifier` (480→256→128→4), Adam, stratified 80/20 split  
**Clustering:** CD-HIT at 90% identity  
**Metagenome assembly:** MEGAHIT v1.2.9  
**Gene prediction:** Prodigal v2.6.3 (meta mode)  
**Statistics:** `proportions_ztest` (two-tailed), Bonferroni correction (α = 0.0125, k=4)  
**Confidence threshold:** softmax probability ≥ 0.85  

Full methods with parameters available in [`methods/methods_overview.md`](methods/methods_overview.md).

## Data Sources

| Dataset | Accession | Reference |
|---------|-----------|-----------|
| RefSeq phage proteins | NCBI RefSeq | — |
| VOG annotations | vogdb.org | — |
| Tara Oceans surface | ERR315858 | Sunagawa et al. 2015, *Science* 348:1261359 |
| Red Sea KAUST Expedition | SRR2102994 | Thompson et al. 2017, *ISME J* 11:138 |

## Key References

- Lin et al. (2023). *Science* 379:1123 — ESM-2
- Sunagawa et al. (2015). *Science* 348:1261359 — Tara Oceans
- Thompson et al. (2017). *ISME J* 11:138 — Red Sea dataset
- Suttle (2007). *Nat Rev Microbiol* 5:801 — marine viruses
- Thingstad (2000). *Limnol Oceanogr* 45:1320 — kill-the-winner

## Contact

Questions about the project or methodology: **samerjahran@gmail.com**

---

*Mawhiba Ibdaa 2027 | Regeneron ISEF 2027 | Computational Biology & Bioinformatics*
