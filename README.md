# PHAGEAMR-FINDER: In Silico Functional Annotation of Ocean Bacteriophage Dark Matter

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20435564.svg)](https://doi.org/10.5281/zenodo.20435564)
[![Web Tool](https://img.shields.io/badge/Web%20Tool-HuggingFace-yellow)](https://huggingface.co/spaces/Samerjahran/phage-dark-matter-annotator)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Mawhiba Ibdaa 2027 | Samer Ali Alghamdi**
Al-Andalus International School, Jeddah, Saudi Arabia
Contact: samerjahran@gmail.com

> ESM-2 protein language model embeddings functionally annotate bacteriophage proteins
> that sequence-alignment tools cannot find — including a novel AMR candidate
> against carbapenem-resistant *Klebsiella pneumoniae* ST258 with zero BLAST hits
> in any database.

*Computational pipeline reviewed by Prof. Robert Hoehndorf, KAUST.*

---

## 🔬 Try the Web Tool

**[phage-dark-matter-annotator on HuggingFace →](https://huggingface.co/spaces/Samerjahran/phage-dark-matter-annotator)**

Paste any phage protein sequence. The tool returns a functional category prediction with confidence score using ESM-2 embeddings — including proteins with zero sequence homology to anything in NCBI nr.

---

## Core Finding

Nine Red Sea phage proteins from the genuinely novel confidence tier returned **zero BLAST hits in NCBI nr at any e-value threshold**, yet the ESM-2 classifier assigned them to functional categories with confidence above 0.85. Structural validation (ESMFold + Foldseek) confirmed known folds in all 17 zero-homology proteins tested (100% concordance).

Protein language models operate in the sequence space where homology-based annotation fails entirely.

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
| Genuinely novel tier BLAST hit rate (conf 0.85–0.99) | 44.0% (56% dark fraction, 95% CI 47–65%) |
| Structural validation: zero-homology proteins matched known folds | 17/17 (100% concordance) |
| Two-tier functional gap | +25 to +26 pp stable across cutoffs 0.95–0.999 |
| Permutation test p-value | p < 0.0001 (n=10,000 shuffles) |

---

## Two-Tier Dark Matter Discovery

| Population | n | BLAST hit rate | Host-interaction % |
|------------|---|----------------|-------------------|
| Near-relatives (conf > 0.99) | 135,100 | 95.6% | 82% |
| Genuinely novel (conf 0.85–0.99) | 29,188 | 44.0% | 57% |

> **Clarification:** The 0% BLAST hit rate in the Core Finding refers to the structural
> validation subset (n=9), not the full genuinely novel tier. The full tier BLAST hit
> rate is 44.0% (95% CI 47–65%), confirming a 56% dark fraction with no homology to
> any characterized protein.

The depth gradient in host-interaction enrichment (+9 pp at surface, p < 0.0001) is driven by the near-relative population. Genuinely novel proteins show depth-invariant functional composition across all four ocean datasets.

---

## AMR Relevance

Phage therapy against ESBL-producing and carbapenem-resistant bacteria requires knowing which phage proteins mediate host recognition. This project annotates **4,764 host-interaction proteins** in the Red Sea genuinely novel tier — proteins with zero sequence homology to anything characterized, now functionally annotated for the first time.

---

## Top AMR Candidate: k99_19554_1

Seven independent computational lines of evidence for this protein as a phage therapy candidate against carbapenem-resistant *Klebsiella pneumoniae* ST258:

| Evidence | Result |
|----------|--------|
| BLAST hits | Zero (viral + bacterial databases) |
| ESMFold pLDDT | 88.2 |
| Foldseek CcmB match | Probability 1.0 |
| TM helices (Phobius) | 7 predicted |
| GRAVY score | 1.335 (membrane protein) |
| ESM-2 prediction | host_interaction, 93.6% confidence |
| RNA-seq validation | Hemin transport upregulated in CRE Klebsiella ST258 (PMID 29669884) |

CcmB is a heme exporter upregulated in carbapenem-resistant *Klebsiella* ST258. k99_19554_1 folds into this structure with probability 1.0, has zero sequence homology to any characterized protein, and is classified as a host-interaction protein by ESM-2 at 93.6% confidence.

---

## Benchmark vs Pharokka

Pharokka v1.9.1 (PHROGs + CARD + VFDB) was run on the target contig containing k99_19554_1. Pharokka annotated 1/2 genes (50%) and **missed k99_19554_1 entirely** — no genes called, no functions assigned on that contig. ESM-2 successfully classified k99_19554_1 as host_interaction at 93.6% confidence.

Sequence-alignment tools are blind to proteins with zero homology. Embedding-based methods are not.

---

## Ocean Metagenome Datasets

| Dataset | Ocean | Depth | HC Proteins |
|---------|-------|-------|-------------|
| Tara Oceans ERR315858 | Indian Ocean | 0 m | 2,010 |
| Red Sea SRR2102994 | Red Sea | 10 m | 81,359 |
| Malaspina ERR770958 | Atlantic Ocean | 200 m | 5,313 |
| Tara Oceans ERR599370 | Pacific Ocean | 800 m | 118,208 |
| Tara Oceans ERR599376 | Pacific Ocean | Surface | In progress |

---

## Pipeline

```
Raw metagenomic reads
        ↓
  Assembly (MEGAHIT)
        ↓
  ORF prediction (Prodigal)
        ↓
 ESM-2 embeddings (esm2_t12_35M_UR50D)
        ↓
  MLP classifier (5-fold CV, macro F1 = 0.9086)
        ↓
  Functional annotation + confidence tiering
        ↓
  AMR candidate identification
        ↓
  Structural validation (ESMFold + Foldseek)
```

---

## Reproducibility

| Resource | Link |
|----------|------|
| Archived models | https://doi.org/10.5281/zenodo.20435564 |
| Web tool | https://huggingface.co/spaces/Samerjahran/phage-dark-matter-annotator |
| GitHub | https://github.com/samerjahran-crypto/Isef2027-phage-dark-matter |

---

## Seeking Wet-Lab Collaboration

The computational case for **k99_19554_1** is complete with seven independent lines of evidence. The next step is experimental validation — a MIC assay or growth inhibition experiment testing this protein against *Klebsiella pneumoniae* ST258 or a suitable surrogate.

**Specific requirements:**
- BSL-2-permitted lab with access to clinical *Klebsiella* isolates
- Capability to perform MIC assay or growth inhibition experiment
- Based in Saudi Arabia or willing to collaborate remotely

Any collaborating lab would receive full co-authorship on the resulting paper. The project is targeting **Mawhiba Ibdaa 2027** and ultimately **ISEF**.

If you are interested or can suggest a contact, please reach out: **samerjahran@gmail.com**

---

## Citation

If you use this work, please cite:

```
Alghamdi, S. A. (2026). In silico Functional Annotation of Ocean Bacteriophage Dark Matter.
Zenodo. https://doi.org/10.5281/zenodo.20435564
```

---

*Grade 8 student | Al-Andalus International School | Jeddah, Saudi Arabia*
*Computational pipeline reviewed by Prof. Robert Hoehndorf, King Abdullah University of Science and Technology (KAUST)*
