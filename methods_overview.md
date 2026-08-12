# Methods Overview — PhageAMR-Finder v6b

*Methodology for:*
*"Protein Language Models for Annotating Red Sea Phage Dark Matter: A Novel Antimicrobial Peptide Candidate Against Carbapenem-Resistant* Klebsiella pneumoniae*"*

**Canonical version:** v6b (competition release, August 2026)
**Zenodo archive:** https://doi.org/10.5281/zenodo.20935067

---

## 1. Data Source

**Metagenome:** Red Sea marine metagenome, SRA accession SRR2102994, BioProject PRJNA289734 (Thompson et al. 2017, *ISME J* 11:138).
Samples were collected from Red Sea surface water during a KAUST oceanographic expedition. This accession was independently confirmed against the original BioProject record after an AI tool incorrectly suggested it was an unrelated bacterial control strain.

**Assembly:** MEGAHIT v1.2.9 → 92,500 contigs.

**Viral identification:** geNomad v1.8.0 (Camargo et al. 2023, *Nature Biotechnology*) was applied to all 92,500 contigs before any protein classification. Only contigs with a geNomad viral score ≥ 0.7 and ≥ 2 viral hallmark genes were carried forward. This pre-filtering step is mandatory — running the classifier on all contigs without viral confirmation produced a false-positive rate of 56% in the top-ranked candidates (see Ablation section). The retired candidate k99_19554_1 was a direct consequence of omitting this filter in an earlier pipeline version.

**Result:** 3,610 confirmed viral contigs, yielding 2,042 predicted proteins for classification.

---

## 2. Training Set Construction (v6b, 1,541 sequences, 8 classes)

The classifier was trained on 1,541 manually curated phage protein sequences across eight functional classes. The training set was assembled from Swiss-Prot, UniProt phage entries, PHROG database annotations, and literature-confirmed phage protein families.

### Class definitions

| Class | Count | Description |
|---|---|---|
| host_binding | 248 | Tail fibers, receptor-binding proteins, depolymerases |
| membrane_disruption | 187 | Holins, endolysins, spanins |
| iron_acquisition | 164 | Hemin uptake, siderophore auxiliary metabolic genes |
| structural | 211 | Capsid, portal, tail tube, terminase |
| replication | 193 | DNA polymerase, helicase, primase |
| regulatory | 178 | CI/CII repressors, antiterminators |
| metabolic_amg | 142 | psbA, phoH, sulfur/phosphate AMGs |
| non_phage | 218 | Human proteins, bacterial proteins, scrambled sequences |
| **Total** | **1,541** | |

### Non_phage class composition (v6b additions vs v4)

v6b expanded the non_phage class relative to v4 (1,318 sequences) by adding:
- 92 scrambled versions of training sequences (same composition, disrupted function)
- 131 diverse human proteins beyond GPCR controls

### Leakage control

MMseqs2 was used to cluster all training sequences at 70% identity. No cluster was split across train and test folds (GroupKFold). The same clustering protocol was applied at 50%, 40%, and 30% identity for the leakage sweep reported in the paper.

A direct comparison of the lead candidate (k99_98199_25) against all 1,541 training sequences confirmed a maximum pairwise similarity of 35.8%, against a synthetic repeat-sequence spacer with no biological relevance. No biologically related training sequence was found.

---

## 3. Protein Language Model Embeddings

**Model:** ESM-2 `esm2_t12_35M_UR50D` (Lin et al. 2023, *Science* 379:1123)
- 35 million parameters, 12 transformer layers
- Pre-trained on UniRef50 (2022 release)
- No phage-specific fine-tuning

**Procedure:**
1. Tokenise at the amino acid level
2. Forward pass through all 12 layers
3. Extract layer 12 (final layer) representations
4. Mean-pool over residue positions, excluding BOS/EOS tokens
5. Output: one 480-dimensional vector per sequence, length-independent

Mean pooling means the embedding dimension captures a learned biochemical property rather than a position — allowing direct comparison of sequences of different lengths in the same feature space.

**Why ESM-2 rather than BLAST:** BLAST requires ~30% sequence identity to produce reliable alignments. The viral dark matter proteins, by definition, have no detectable homologs. ESM-2 predicts function from sequence patterns learned across millions of characterised proteins, without requiring a database hit.

---

## 4. MLP Classifier (v6b)

```
Input:      480 neurons (ESM-2 embedding)
Hidden 1:   256 neurons (ReLU)
Hidden 2:   128 neurons (ReLU)
Hidden 3:    64 neurons (ReLU)
Output:       8 neurons (Softmax — one per class)
```

**Training:** Adam optimizer, learning rate 0.001, L2 regularisation (alpha = 0.001), early stopping (patience 10 epochs, validation fraction 10%). Implemented with `sklearn.neural_network.MLPClassifier`.

**Evaluation:** Five-fold stratified cross-validation; predictions assembled out-of-fold before computing macro F1 and bootstrap confidence interval (n = 1,000 resamples). Both the point estimate and CI were computed from the same matched prediction set; an earlier version of the analysis reported them from different sets, producing an invalid CI, which was corrected.

---

## 5. Validation Battery

| Check | Result |
|---|---|
| CV Macro F1 (5-fold, v6b) | 0.9670 ± 0.0174 |
| Bootstrap 95% CI | [0.9506, 0.9808] |
| GPCR OOD rejection (n=434) | 100% |
| Permutation test (n=10,000) | p < 0.0001 |
| Physicochemical baseline (membrane class) | 0.913 vs 0.989 |
| Cluster-aware at 30% identity | 0.8663 |
| Candidate vs training leakage | max 35.8% (synthetic spacer) |
| External validation (GOV2, n=24,706) | mean confidence 0.819 |

The GOV2 result demonstrates distributional generalisation — the classifier behaves coherently on genes from different oceans, laboratories, and assembly pipelines. It does not establish label accuracy on those proteins, which are hypothetical and lack experimentally confirmed functions.

---

## 6. Ablation: Viral Pre-Filtering

**Motivation:** The retired candidate k99_19554_1 demonstrated that high-confidence classifier outputs can originate from bacterial contigs mis-included in the assembly. To quantify this, we compared two pipelines over the same assembly:

- **Pipeline A (naive):** classify all proteins from all contigs
- **Pipeline B (geNomad-first):** classify only proteins from confirmed viral contigs

**Result:** Among the top 50 membrane-disruption candidates, Pipeline A produced 56% false positives (from non-viral contigs). Pipeline B produced 0%. The 0% result was verified as non-circular using a second criterion — flanking-gene analysis confirmed that Pipeline B's candidates carry viral hallmark genes and Caudoviricetes taxonomy independent of the geNomad score.

---

## 7. Lead Candidate

**k99_98199_25:** 54 amino acids, sequence `MLNLETVKSAVKKFLGSALRLLWKKATSSIKGICATMLTKAKKKIASLRTSGRD`. Net charge +10.49, pI 10.87, GRAVY −0.022.

Source contig k99_98199: 26,607 bp, geNomad viral score 0.98.

**Assembly integrity:** 9.56M read pairs from SRR2102994 mapped back to the contig. Breadth 100%, mean depth 13.01×, median 13.0×, no zero-coverage positions. The gene itself (positions 13,870–14,034) carries 14.57× mean depth with a minimum of 10×.

**Genomic context:** All 53 genes on the contig were inspected. Zero bacterial universal single-copy marker genes. Three viral hallmark genes: terminase RNase-H domain (gene 52), head-to-tail connecting protein (gene 53), and DUF3310 (gene 19). The candidate sits between two Caudoviricetes-assigned genes.

**Novelty:** Seven independent searches — DRAMP, APD3, CAMPR4, DBAASP, Foldseek against PDB, Foldseek against AlphaFold DB, and BLASTp against nr with PAM30 short-peptide parameters — returned no matching homolog. Best BLASTp E-value: 2.5 (statistical noise).

**Status:** Computational candidate only. No biological activity has been demonstrated. Wet-lab validation is planned pending regulatory approval.

---

## 8. Version History

| Version | Training N | CV Macro F1 | Key change |
|---|---|---|---|
| v4 | 1,318 | 0.9771 ± 0.0091 | Baseline; 8 classes; GPCR OOD |
| v5 | 1,334 | 0.9761 ± 0.0062 | Added bacterial AMR negatives |
| v6b | 1,541 | 0.9670 ± 0.0174 | Scrambled + diverse human negatives; stricter eval |

v6b is the canonical competition version. The lower F1 relative to v4 reflects harder evaluation, not degraded performance — more challenging negatives and cluster-aware GroupKFold testing expose the genuine generalization boundary.

---

*Full pipeline notebooks available at:* https://github.com/samerjahran-crypto/Isef2027-phage-dark-matter
*Contact:* samerjahran@gmail.com
