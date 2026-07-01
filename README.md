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

**The pipeline is geNomad-first:** viral contig classification before any functional analysis. This is a hard requirement. ESM-2 functional classification alone is insufficient — bacterial proteins from metagenomic assemblies can score high on AMR-relevant classes without being phage-derived. Genomic context verification is not optional.

**[Try the web tool →](https://huggingface.co/spaces/Samerjahran/phage-dark-matter-annotator)**

---

## Pipeline

```
Raw reads → MEGAHIT assembly (92,500 contigs)
         → geNomad viral classification (3,610 phage contigs, score >0.9)
         → Protein extraction from ≥3 kb contigs with ≥2 hallmarks
         → ESM-2 v6b classification (8 classes)
         → BLAST novelty screen (clustered nr)
         → ESMFold + Foldseek structural search
         → Candidate identification
```

---

## Primary candidate: k99_98199_25

A 54 aa cationic membrane-disrupting peptide from a confirmed Red Sea phage contig.

**Contig context:** k99_98199, 26,607 bp, geNomad virus score 0.9815  
**Hallmark genes:** terminase large subunit (gene 52), head-to-tail connecting protein (gene 53)  
**Partner endolysin:** k99_98199_51 (SLT domain, 171 aa, gram-negative cell wall specificity confirmed by BLAST to Citrobacter/Burkholderia phage hits)

**Candidate protein evidence:**

| Evidence | Result |
|----------|--------|
| Sequence | `MLNLETVKSAVKKFLGSALRLLWKKATSSIKGICATMLTKAKKKIASLRTSGRD` |
| Length | 54 aa |
| ESM-2 class | membrane_disruption, 0.9713 confidence |
| BLAST (clustered nr) | **Zero hits** |
| Foldseek (all 8 databases) | **Zero hits** |
| ESMFold pLDDT | 88.225 |
| Predicted structure | Single alpha-helix |
| pI | 10.87 |
| Charge at pH 7 | +10.49 |
| GRAVY | -0.022 |
| TMHMM | 0 TM helices, outside |
| Phobius | Non-cytoplasmic |
| Instability index | 17.54 (stable) |

The strongly cationic architecture (+10.49 at pH 7) provides intrinsic selectivity for negatively charged bacterial membranes over zwitterionic mammalian membranes. Structure is deposited in `/structures/k99_98199_25.pdb`.

---

## Pipeline false positive: k99_19554_1 (retired)

k99_19554_1 (206 aa) was identified in an earlier pipeline version before geNomad-first validation was implemented. It returned zero BLAST hits against phage-specific databases and showed high ESM-2 classification confidence. However, multi-assembler validation (MetaSPAdes + MEGAHIT on BayesHammer-corrected reads) and flanking ORF analysis revealed the harboring contig encodes a complete CcmABC cytochrome c maturation operon from Paracoccaceae bacterium. Current blastp against NCBI clustered nr returns CcmB at 98.06% identity, 100% coverage, e=5e-134.

k99_19554_1 is bacterial CcmB, not a phage protein. It is retained as a methodological case study demonstrating the necessity of geNomad-first validation. Its structure (`structures/k99_19554_1.pdb`) and all associated files are kept for reproducibility.

---

## Classifier performance (v6b, current)

| Metric | Value |
|--------|-------|
| CV Macro F1 (5-fold, 1,541 sequences) | 0.9670 ± 0.0174 |
| OOD rejection — human GPCRs | 100% (3/3) |
| OOD rejection — bacterial AMR proteins | 100% (5/5) |
| OOD rejection — scrambled sequences | 100% (100/100) |
| Permutation test | p < 0.0001 (n=10,000) |
| Training-dark matter leakage (MMseqs2, 70%) | Zero overlap |

**8 classes:** host_binding, membrane_disruption, iron_acquisition, structural, replication, regulatory, metabolic_amg, non_phage

### Version history

| Version | Sequences | CV F1 | Key change |
|---------|-----------|-------|------------|
| v4 | 1,318 | 0.9771 ± 0.0091 | Baseline, GPCR OOD |
| v5 | 1,334 | 0.9761 ± 0.0062 | Bacterial AMR negatives |
| v6b | 1,541 | 0.9670 ± 0.0174 | Scrambled + diverse human protein negatives |
| v7 (not deployed) | 1,340 | 0.9561 samples F1 | Multi-label — insufficient specificity |

---

## Ecological finding

Depth-invariant functional composition in the genuinely novel dark matter tier (confidence 0.85–0.99) across four ocean metagenomes (Indian Ocean 0 m, Red Sea 10 m, Atlantic 200 m, Pacific 800 m). The depth gradient reported in prior ocean virome studies is driven entirely by the near-relative tier (confidence >0.99), not by genuinely novel proteins.

---

## Comparison to existing tools

| Tool | Approach | Zero-BLAST-hit proteins |
|------|----------|------------------------|
| Pharokka / PHROG | Sequence homology | No |
| Phold | Structural homology | Partial |
| Phynteny (Grigson 2025) | Synteny + PHROG | No |
| **PhageAMR-Finder** | ESM-2 + geNomad validation | Yes |

---

## Repository structure

```
/
├── embed_and_predict.py         CLI tool for protein annotation
├── app.py                       [on HuggingFace Space only]
├── README.md
├── methods_overview.md
├── structures/
│   ├── k99_98199_25.pdb         Primary candidate (54 aa, pLDDT 88.225)
│   ├── k99_19554_1.pdb          Retired false positive (206 aa, bacterial CcmB)
│   └── [other structures]
├── results/
│   ├── dark_matter_candidates.tsv   14 geNomad-validated dark matter candidates
│   └── [other result files]
└── notebooks/
    └── [training notebooks]
```

---

## Citation

Alghamdi, S. A. (2026). PhageAMR-Finder: ESM-2 MLP Classifier for Ocean Phage Dark Matter Functional Annotation (v3). Zenodo. https://doi.org/10.5281/zenodo.20935067

---

Grade 9 · Al-Andalus International School · Jeddah, Saudi Arabia
