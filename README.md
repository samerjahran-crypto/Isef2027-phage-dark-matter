# PhageAMR-Finder

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20935067.svg)](https://doi.org/10.5281/zenodo.20935067)
[![Web Tool](https://img.shields.io/badge/Web%20Tool-HuggingFace-yellow)](https://huggingface.co/spaces/Samerjahran/phage-dark-matter-annotator)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Mawhiba Ibdaa 2027 | Samer Ali Alghamdi**
Al-Andalus International School, Jeddah, Saudi Arabia
samerjahran@gmail.com

---

## What this project is about

The ocean is full of viruses we've never characterized. Most of their proteins return zero BLAST hits — no known relatives, no functional annotation, nothing. Standard tools just skip them.

This project uses ESM-2 protein language model embeddings to annotate those proteins without needing sequence similarity to anything previously described. Instead of asking "does this look like something we've seen before?", the model learns what functional classes look like in 3D structural space — and can recognize them even when the sequence is completely novel.

The work started because I found one protein in Red Sea viral dark matter that looked genuinely strange. It turned out to have two functional domains fused together in a way that, if it works the way the structural evidence suggests, creates a trap that drug-resistant *Klebsiella pneumoniae* ST258 cannot escape. That protein — k99_19554_1 — is what this project is built around.

**[Try the web tool →](https://huggingface.co/spaces/Samerjahran/phage-dark-matter-annotator)**

---

## The core finding: k99_19554_1

k99_19554_1 is a 218 amino acid protein from an uncultivated Red Sea phage (metagenomic contig SRR2102994, KAUST expedition, 10m depth). It has zero BLAST hits in any global database — it genuinely doesn't look like anything that's been described before.

Structural matching via Foldseek 3Di revealed two domains:

**N-terminal (residues 1–109) — CcmB heme exporter fold**
Foldseek probability 1.0. CcmB is part of the iron acquisition pathway that *Klebsiella* ST258 depends on to survive in human blood — serum iron is held at around 10⁻¹⁸ M as an immune defense, so the bacterium has to steal iron from hemoglobin to survive. This locus is conserved in 98.9% of 2,242 sequenced ST258 clinical genomes (Lan 2023). It can't be easily mutated away without killing the cell.

**C-terminal (residues 110–218) — Class II holin fold**
Foldseek match to AF-R3WJF2 (E-value 2.40), covering the TMH1-loop-TMH2 hairpin — the core pore-forming machinery of Class II holins. The 7th transmembrane helix maps to this domain.

**The evolutionary trap:** if *Klebsiella* mutates away from the CcmB pathway, it loses its iron source and starves. If it keeps the pathway, the holin domain can dock into the inner membrane, oligomerize, and lyse the cell. There's no single mutation that escapes both consequences simultaneously.

Sixteen independent evidence lines — structural, physicochemical, ecological, and computational — support this interpretation. Wet-lab validation (propidium iodide pore-forming kinetics assay on the C-terminal domain, hemin-biotin dot-blot on the N-terminal domain) is planned for August–September 2026 at KAUST.

---

## Classifier performance (v4)

| Metric | Value |
|--------|-------|
| CV Macro F1 (5-fold, 1318 sequences) | 0.9771 ± 0.0091 |
| Bootstrap 95% CI | [0.9936, 0.9994] |
| OOD rejection — human GPCRs → non_phage | 100% (434/434) |
| Permutation test p-value | p < 0.0001 (n=10,000) |
| MMseqs2 leakage check (70% identity threshold) | Zero overlap |

**8 functional classes:** host_binding, membrane_disruption, iron_acquisition, structural, replication, regulatory, metabolic_amg, non_phage

Version 4 added a non_phage class trained on 200 human GPCR sequences. Human proteins are now correctly rejected at 100% rather than being forced into a phage functional class. This was a genuine limitation of earlier versions that's now fixed.

**One honest caveat:** k99_19554_1 itself classifies as metabolic_amg under mean-pooled ESM-2 embeddings. This is a known limitation of mean-pooling for highly hydrophobic multi-transmembrane proteins — documented in Meier et al. 2021 (NeurIPS) and supported by silhouette analysis (membrane_disruption cluster score 0.05, iron_acquisition 0.06). The functional annotation of k99 is based on the Foldseek structural evidence, not the classifier output.

---

## Ecological finding

The pipeline was run on four ocean metagenomes across different depths and ocean basins:

| Dataset | Ocean | Depth |
|---------|-------|-------|
| Tara Oceans ERR315858 | Indian Ocean | 0 m |
| Red Sea SRR2102994 | Red Sea | 10 m |
| Malaspina ERR770958 | Atlantic Ocean | 200 m |
| Tara Oceans ERR599370 | Pacific Ocean | 800 m |

The novel dark matter tier shows depth-invariant functional composition across all four datasets (Two-Way ANOVA, depth effect p > 0.05). The near-relative tier follows the expected published depth gradient in the same data. Since both tiers were processed through the same pipeline, the difference is biological, not methodological.

---

## Pipeline overview

```
Raw metagenomic reads
        ↓
  Assembly (MEGAHIT)
        ↓
  ORF prediction (Prodigal)
        ↓
  ESM-2 embeddings (esm2_t12_35M_UR50D, layer 12, mean-pooled, 480-dim)
        ↓
  MLP classifier (8 classes, 5-fold CV, Macro F1 = 0.9771)
        ↓
  Functional annotation + confidence tiering (threshold 0.50)
        ↓
  AMR candidate identification
        ↓
  Structural validation (ESMFold + Foldseek 3Di)
```

---

## Resources

| Resource | Link |
|----------|------|
| Web tool | https://huggingface.co/spaces/Samerjahran/phage-dark-matter-annotator |
| Zenodo v2 (current models) | https://doi.org/10.5281/zenodo.20935067 |
| Zenodo v1 | https://doi.org/10.5281/zenodo.20435564 |
| GitHub | https://github.com/samerjahran-crypto/Isef2027-phage-dark-matter |

---

## Citation

```
Alghamdi, S. A. (2026). ESM-2 MLP Classifier for Ocean Phage Dark Matter
Functional Annotation — Ibdaa 2027 (v2). Zenodo.
https://doi.org/10.5281/zenodo.20935067
```

---

*Grade 9 | Al-Andalus International School | Jeddah, Saudi Arabia*
*Computational methodology reviewed by Prof. Robert Hoehndorf, King Abdullah University of Science and Technology (KAUST)*
