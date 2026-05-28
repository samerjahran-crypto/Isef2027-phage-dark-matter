# In Silico Functional Annotation of the Ocean Bacteriophage Dark Matter Proteome
### A Depth-Resolved Protein Language Model Framework for Marine Viromics

**Samer Ali Saeed Alghamdi** | Jeddah, Saudi Arabia
ISEF 2027 — Computational Biology & Bioinformatics
📧 samerjahran@gmail.com

---

> **70% of marine phage proteins are functionally unknown.**
> This project uses protein language model embeddings to illuminate that darkness
> and finds that phage functional composition is stratified by ocean depth.

---

## The Problem

Marine bacteriophages are the most abundant biological entities on Earth (~10³¹ particles), killing 20–40% of marine bacteria daily. Despite exponential growth in ocean sequencing, approximately 70% of phage proteins have no detectable homology to any characterized sequence — the viral dark matter. Traditional BLAST-based annotation fails here by design: these proteins are too evolutionarily distant.

## The Approach

Rather than searching for sequence similarity, this project embeds proteins into a **480-dimensional biological meaning space** using ESM-2 (Lin et al. 2023, *Science*) — a protein language model trained on 250 million sequences. Functionally related proteins cluster in this space regardless of sequence identity.

An MLP classifier trained on 43,475 VOG-labeled phage proteins achieves **Macro F1 = 0.9086 ± 0.0059 (five-fold CV)** across four functional classes, then predicts function for **184,394 uncharacterized proteins** from NCBI RefSeq — the largest phage dark matter functional atlas produced to date.

## Key Finding: A Depth-Stratified Functional Gradient

Four independent datasets across two depth zones reveal a clear depth gradient:

| Functional Class | Global Baseline | Surface 0m (Tara) | Surface 10m (Red Sea) | Mesopelagic 800m |
|-----------------|----------------|-------------------|----------------------|-----------------|
| host_interaction | 77.8% | **87.2%** *** | **86.8%** *** | **81.3%** *** |
| structural | 10.0% | **3.8%** *** | **5.1%** *** | **7.5%** *** |
| replication | 9.0% | 8.1% ns | 7.2% *** | 9.9% *** |
| transcription | 3.1% | 0.9% *** | 0.9% *** | 1.3% *** |

*p < 0.001 after Bonferroni correction (α = 0.0125, k = 4)*

**The depth gradient is monotonic:** host-interaction proteins decrease from surface (87%) to mesopelagic (81.3%) to global baseline (77.8%). Structural proteins show the opposite trend. This is consistent with oligotrophic selection pressure and kill-the-winner dynamics (Thingstad 2000) — forces that are strongest at the nutrient-depleted, diverse surface and attenuate with depth.

## Classifier Performance

| Feature Set | Macro F1 |
|-------------|----------|
| **ESM-2 embeddings (this work)** | **0.9086 ± 0.0059** |
| k-mer frequencies | 0.804 |
| Amino acid composition | 0.680 |
| Length only | 0.208 |
| Shuffled labels (control) | 0.208 |
| Random embeddings (control) | 0.208 |

Controls confirm ESM-2 captures genuine biological signal, not sequence artifacts or embedding dimensionality.

## BLAST Validation

90 high-confidence predictions (25 per class, 15 transcription) were BLASTed against NCBI nr and Swiss-Prot:

- **BLAST nr:** 86/90 hits (95.6%) — replication 100%, transcription 100%, structural 96%, host_interaction 88%
- **BLAST Swiss-Prot:** Zero hits across all classes

These proteins are validated by nr homology but have never been experimentally characterized — confirming genuine novelty.

## Pipeline Overview

```
RefSeq phage genomes
       |
       v
 CD-HIT clustering (90% identity)
       |
       |---> VOG-labeled (43,475) ---> ESM-2 embeddings ---> MLP training (F1=0.9086)
       |                                                            |
       \---> Dark matter (184,394) --> ESM-2 embeddings ---> Prediction (164,288 HC)
                                                                    |
                              +-----------------+------------------+------------------+
                              v                 v                  v                  v
                         Global atlas     Tara Oceans          Red Sea          Mesopelagic
                         (RefSeq)        ERR315858            SRR2102994        ERR599370
                                         0m Indian Ocean      10m Red Sea       800m Pacific
                              +-----------------+------------------+------------------+
                                         Z-tests + Bonferroni correction
                                    --> Depth-stratified functional gradient
```

## Repository Contents

```
isef2027-phage-dark-matter/
|-- README.md
|-- requirements.txt
|-- LICENSE
|-- demo/
|   |-- embed_and_predict.py    <- Predict function for your own proteins
|   \-- example_proteins.faa   <- 10 example sequences to test
\-- methods/
    \-- methods_overview.md    <- Full methods without pipeline code
```

Full pipeline notebooks are in a private repository and will be released after competition submission (September 2026).

## Pre-trained Models

Trained models are permanently archived on Zenodo with a citable DOI:

**DOI: https://doi.org/10.5281/zenodo.20435564**

Download `mlp_classifier.pkl` and `label_encoder.pkl` from Zenodo, place in a `models/` directory, and load with `joblib.load()`.

## Methods Summary

**Protein embedding:** ESM-2 `esm2_t12_35M_UR50D`, 480-dim mean-pooled representations
**Classifier:** `sklearn.neural_network.MLPClassifier` (480->256->128->4), Adam, five-fold stratified CV
**Clustering:** CD-HIT at 90% identity
**Metagenome assembly:** MEGAHIT v1.2.9 (--min-contig-len 500)
**Gene prediction:** Prodigal v2.6.3 (meta mode)
**Statistics:** `proportions_ztest` (two-tailed), Bonferroni correction (alpha = 0.0125, k = 4)
**Confidence threshold:** softmax probability >= 0.85

## Data Sources

| Dataset | Accession | Depth | Reference |
|---------|-----------|-------|-----------|
| RefSeq phage proteins | NCBI RefSeq | — | — |
| VOG annotations | vogdb.org | — | — |
| Tara Oceans surface | ERR315858 | 0 m | Sunagawa et al. 2015, *Science* 348:1261359 |
| Red Sea KAUST Expedition | SRR2102994 | 10 m | Thompson et al. 2017, *Nature* 551:457 |
| Tara Oceans mesopelagic | ERR599370 | 800 m | Sunagawa et al. 2015, *Science* 348:1261359 |

## Key References

- Lin et al. (2023). *Science* 379:1123 — ESM-2
- Sunagawa et al. (2015). *Science* 348:1261359 — Tara Oceans
- Thompson et al. (2017). *Nature* 551:457 — Red Sea dataset
- Suttle (2007). *Nat Rev Microbiol* 5:801 — marine viruses
- Thingstad (2000). *Limnol Oceanogr* 45:1320 — kill-the-winner
- Murray et al. (2022). *Lancet* 399:629 — AMR burden

## Contact

samerjahran@gmail.com | github.com/samerjahran-crypto/Isef2027-phage-dark-matter

---

*Mawhiba Ibdaa 2027 | Regeneron ISEF 2027 | Computational Biology & Bioinformatics*
