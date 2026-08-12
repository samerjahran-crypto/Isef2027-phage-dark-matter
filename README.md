# PhageAMR-Finder

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20935067.svg)](https://doi.org/10.5281/zenodo.20935067)
[![Web Tool](https://img.shields.io/badge/Web%20Tool-HuggingFace-yellow)](https://huggingface.co/spaces/Samerjahran/phage-dark-matter-annotator)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Mawhiba Ibdaa 2027 · Samer Ali Alghamdi**  
Al-Andalus International School, Jeddah, Saudi Arabia  
samerjahran@gmail.com

---

## What this project does

Most ocean phage proteins return zero BLAST hits — no known relatives, no functional annotation. Standard tools skip them entirely. This project uses ESM-2 protein language model embeddings to annotate those proteins without needing sequence similarity to anything previously described.

**The pipeline is geNomad-first:** viral contig classification before any functional analysis. This is a hard requirement, not a preference. Without it, 56% of the top-ranked candidates originate from non-viral contigs (measured; see Ablation below). ESM-2 classification alone is insufficient.

**[Try the web tool →](https://huggingface.co/spaces/Samerjahran/phage-dark-matter-annotator)**

---

## Pipeline

```
Raw reads → MEGAHIT assembly (92,500 contigs)
         → geNomad viral classification (3,610 phage contigs, score >0.9)
         → Protein extraction from confirmed viral contigs
         → ESM-2 v6b classification (8 classes)
         → BLAST novelty screen (full nr, PAM30 short-peptide parameters)
         → Foldseek structural search (PDB + AlphaFold DB)
         → Candidate identification and assembly verification
```

---

## Why geNomad-first is mandatory: ablation result

Classifying proteins from all 92,500 contigs without viral pre-filtering and then running Prodigal gene calling:

| Pipeline | Top-50 candidates | From non-viral contigs | False-positive rate |
|---|---|---|---|
| A — no pre-filter | 2,688 ranked | 28 of top 50 | **56%** |
| B — geNomad-first | 280 ranked | 0 of top 50 | **0%** |

The 0% result is not circular. An independent flanking-gene audit of Pipeline B's top candidates confirmed that 10/10 carry viral hallmark genes or Caudoviricetes taxonomy — evidence not derived from the geNomad viral score.

The retired candidate (k99_19554_1, see below) was caught by this same flanking-gene check. Its discovery was what prompted the ablation measurement.

---

## Primary candidate: k99_98199_25

A 54 aa cationic membrane-disrupting peptide from a confirmed Red Sea phage contig.

**Contig context:** k99_98199, 26,607 bp, geNomad virus score 0.9815  
**Hallmark genes:** terminase large subunit (gene 52), head-to-tail connecting protein (gene 53)  
**Partner endolysin:** k99_98199_51 (SLT domain, 171 aa; BLAST matches to Citrobacter and Burkholderia phage proteins, consistent with gram-negative host range — not biochemical confirmation of substrate specificity)

**Candidate protein evidence:**

| Evidence | Result |
|---|---|
| Sequence | `MLNLETVKSAVKKFLGSALRLLWKKATSSIKGICATMLTKAKKKIASLRTSGRD` |
| Length | 54 aa |
| ESM-2 class (v6b) | membrane_disruption, 0.9713 confidence |
| BLASTp vs full nr (PAM30, -seg no) | 66 apparent hits, best E-value 2.5 — noise, not homology |
| DRAMP | No hit |
| APD3 | No hit |
| CAMPR4 | No hit |
| DBAASP | No hit |
| Foldseek vs PDB (ProstT5) | No hit |
| Foldseek vs AlphaFold DB (structure) | No hit |
| ESMFold pLDDT | 88.225 (mean) |
| Secondary structure | Single alpha-helix, residues 4–52 (90.7%) |
| pI | 10.87 |
| Charge at pH 7 | +10.49 |
| GRAVY | −0.022 |
| Instability index | 17.54 (stable) |

**Assembly verification:**  
9,560,317 read pairs mapped back to contig k99_98199. Breadth 100%, mean depth 13.01×, median 13.0×, zero-coverage positions 0. Gene k99_98199_25 at positions 13,870–14,034 averages 14.57× with a minimum of 10×. No zero-coverage gap exists anywhere on the 26,607 bp sequence.

**Genomic context:**  
53 genes on the contig. Zero bacterial universal single-copy marker genes (USCGs). Three viral hallmark genes. The candidate sits between two Caudoviricetes-assigned genes with 16 bp and 0 bp intergenic gaps.

> **Important:** The candidate is a computational lead. No biological activity has been demonstrated. Novelty means no database homolog was found; it does not establish antimicrobial function. Wet-lab validation is planned pending regulatory approval.

---

## Pipeline false positive: k99_19554_1 (retired)

k99_19554_1 (206 aa) was identified in an earlier pipeline version before geNomad-first validation was implemented. It returned zero BLAST hits against phage databases and showed high classification confidence. Flanking ORF analysis resolved it as bacterial CcmB: CcmA (96% identity) and CcmC (100% identity) flank it in the same *Paracoccaceae* genome in nr. Current BLASTp returns CcmB at 98% identity, e = 5e-134.

k99_19554_1 is bacterial CcmB, not a phage protein. It is retained in this repository as a documented false-positive case study. Its structure and associated files remain for reproducibility.

---

## Classifier performance (v6b, current)

| Metric | Value |
|---|---|
| CV Macro F1 (5-fold stratified) | 0.9670 ± 0.0174 |
| Bootstrap 95% CI | [0.9506, 0.9848] |
| OOD rejection — human GPCRs (n=434) | 100% |
| OOD rejection — bacterial AMR proteins (n=5) | 100% |
| OOD rejection — scrambled sequences (n=100) | 100% |
| Permutation test | p < 0.0001 (n=10,000) |
| Physicochemical baseline (membrane class) | 0.913 vs 0.989 |
| GOV2 external transfer (n=24,706) | mean confidence 0.819 |

**Cluster-aware leakage sweep** (MMseqs2 GroupKFold, whole clusters held out):

| Identity threshold | Macro F1 |
|---|---|
| 70% | 0.9724 |
| 50% | 0.9685 |
| 40% | 0.9724 |
| 30% | 0.8663 |

The 30% decline is reported openly. It represents genuine generalization difficulty at extreme divergence — the regime where viral dark matter proteins actually live. It is not hidden.

**Candidate-vs-training leakage:** Maximum pairwise similarity between k99_98199_25 and any training sequence is 35.8%, against a synthetic repeating-pentamer spacer with no biological relevance. No biologically related training sequence was found.

**8 classes:** host_binding, membrane_disruption, iron_acquisition, structural, replication, regulatory, metabolic_amg, non_phage

### Version history

| Version | Sequences | CV F1 | Key change |
|---|---|---|---|
| v4 | 1,318 | 0.9771 ± 0.0091 | Baseline, GPCR OOD |
| v5 | 1,334 | 0.9761 ± 0.0062 | Bacterial AMR negatives |
| v6b | 1,541 | 0.9670 ± 0.0174 | Scrambled + diverse human protein negatives; cluster-aware evaluation |
| v7 (not deployed) | 1,340 | 0.9561 macro F1 | Multi-label attempt — insufficient specificity |

The lower v6b F1 relative to v4 reflects harder evaluation conditions, not degraded performance.

---

## Comparison to related work

| Method | Core approach | Annotates zero-BLAST-hit proteins | Published |
|---|---|---|---|
| Pharokka / PHROG HMM | Sequence homology | No | 2022 |
| Phold | Structural homology (Foldseek vs annotated DB) | Partial | 2024 |
| Phynteny (Grigson 2025) | Synteny + PHROG HMM | No | 2025 |
| GOPhage (Guan 2025) | ESM-2 + Transformer over genomic context | Yes | Jan 2025 |
| Empathi (Boulay 2025) | ProtT5 + hierarchical assignment | Yes | Oct 2025 |
| VPF-PLM (Flamholz 2024) | ESM-2 + PHROG multilabel | Partial | 2024 |
| **PhageAMR-Finder** | ESM-2 + MLP + geNomad-first validation | Yes | 2026 |

**Note:** GOPhage and Empathi are serious published systems using overlapping methods. A quantitative head-to-head benchmark against these tools on a shared homology-controlled labeled set is the most important planned upgrade. The current comparison is qualitative.

---

## Ecological finding (secondary result)

No significant depth effect was detected on the genuinely novel dark-matter tier (confidence 0.85–0.99) across four ocean metagenomes (two-way ANOVA, p > 0.05). The depth gradients reported in prior virome studies appear to originate from the near-relative tier rather than from genuinely novel proteins.

> **Note:** A non-significant ANOVA does not establish depth-invariance. It establishes that a depth effect was not detected. This result is presented as a secondary finding pending a formal equivalence analysis.

---

## Repository structure

```
/
├── embed_and_predict.py         CLI tool — annotate proteins using v6b
├── methods_overview.md          Full methodology documentation
├── README.md
├── structures/
│   ├── k99_98199_25.pdb         Primary candidate (54 aa, pLDDT 88.225)
│   ├── k99_19554_1.pdb          Retired false positive (bacterial CcmB)
│   └── [other structures]
└── results/
    ├── dark_matter_candidates.tsv   Membrane-disruption candidates
    └── [other result files]
```

Model files (classifier_v6b.pkl, label_encoder_v6b.pkl) are archived at Zenodo.

---

## Installation and usage

```bash
pip install fair-esm scikit-learn torch joblib
```

Download model files from Zenodo (link above), then:

```bash
python embed_and_predict.py --fasta your_sequences.faa \
    --classifier classifier_v6b.pkl \
    --label_enc label_encoder_v6b.pkl \
    --threshold 0.50
```

Optional flags: `--batch_size 4` (reduce if GPU OOM), `--verbose` (show all class probabilities)

---

## Citation

Alghamdi, S. A. (2026). PhageAMR-Finder: ESM-2 MLP Classifier for Ocean Phage Dark Matter Functional Annotation. Zenodo. https://doi.org/10.5281/zenodo.20935067

---

Grade 9 · Al-Andalus International School · Jeddah, Saudi Arabia
