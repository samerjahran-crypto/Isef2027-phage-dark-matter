# Methods Overview

*Detailed methodology for:*  
*"In Silico Functional Annotation of the Uncharacterized Ocean Bacteriophage Proteome via Protein Language Model Embeddings"*

---

## 1. Training Data Construction

**Source:** NCBI RefSeq phage genomes (downloaded January 2026)  
**Total proteins:** 227,996 after translation

**Redundancy reduction:** CD-HIT v4.8.1 at 90% sequence identity (`-c 0.90 -n 5`)  
This prevents the classifier from learning sequence identity rather than functional signal.

**Functional annotation:** Virus Orthologous Groups (VOG) database (vogdb.org)  
VOG assigns proteins to functional categories based on phylogenetic clustering.  
Four classes retained (sufficient training examples, biologically interpretable):

| Class | Count | Description |
|-------|-------|-------------|
| host_interaction | 31,027 | Tail fibers, receptor-binding proteins, anti-restriction systems |
| replication | 6,013 | DNA/RNA polymerases, helicases, primases |
| structural | 5,117 | Capsid, tail, baseplate proteins |
| transcription | 1,318 | Sigma factors, anti-sigma factors, transcriptional regulators |
| **Total labeled** | **43,475** | |
| Dark matter (unlabeled) | 184,394 | No VOG match — prediction targets |

---

## 2. Protein Language Model Embeddings

**Model:** ESM-2 `esm2_t12_35M_UR50D` (Lin et al. 2023, *Science* 379:1123)  
- 35 million parameters, 12 transformer layers
- Pre-trained on 250 million protein sequences from UniRef50 (2022 release)
- No phage-specific fine-tuning; embeddings are general-purpose

**Embedding procedure:**
1. Each protein sequence is tokenized at the amino acid level
2. Forward pass through all 12 transformer layers
3. Layer 12 (final) representations extracted per token
4. Mean-pooled over sequence length (excluding BOS/EOS tokens)
5. Result: one 480-dimensional vector per protein, independent of sequence length

**Batch processing:** Batch size 32; adaptive halving on GPU out-of-memory error  
**Hardware:** NVIDIA A100 (Google Colab Pro)  
**Runtime:** ~2 hours for 227,996 proteins

**Why ESM-2 rather than BLAST:**  
BLAST detects sequence homology — it requires ~30% sequence identity to produce reliable alignments. The dark matter proteins, by definition, share <30% identity with any characterized protein. ESM-2 captures protein *function* through learned representations of amino acid co-evolution patterns, enabling comparison in "biological meaning space" where sequence-dissimilar but functionally similar proteins can be identified.

---

## 3. MLP Classifier

**Architecture:**
```
Input layer:   480 neurons  (ESM-2 embedding dimensions)
Hidden layer 1: 256 neurons (ReLU activation)
Hidden layer 2: 128 neurons (ReLU activation)
Output layer:    4 neurons  (Softmax — one per class)
```

**Training configuration:**
- Optimizer: Adam (learning rate 0.001, auto-adjusted)
- Regularization: L2 (alpha = 0.0001); early stopping (patience = 10 epochs, validation fraction 10%)
- Train/test split: 80% train / 20% test, stratified by class to preserve class imbalance
- Implementation: `sklearn.neural_network.MLPClassifier`

**Class imbalance:** Not artificially balanced. The model learns real-world class frequencies.  
A balanced model would produce unrealistic predictions when applied to the dark matter set.

---

## 4. Ablation Study

To confirm ESM-2 captures biological signal (not sequence statistics), five feature sets were compared on identical train/test splits:

| Feature Set | Dimensionality | Macro F1 |
|-------------|---------------|----------|
| ESM-2 embeddings | 480 | **0.917** |
| k-mer frequencies (k=3,4) | ~8,400 | 0.804 |
| Amino acid composition | 20 | 0.680 |
| Protein length | 1 | 0.208 |
| Shuffled labels (permutation control) | 480 | 0.208 |
| Random Gaussian embeddings (embedding control) | 480 | 0.208 |

Controls confirm that neither the classifier architecture nor the embedding dimensionality alone drives performance — the biological content of ESM-2 representations is essential.

---

## 5. Confidence Filtering

The MLP outputs a 4-class softmax probability vector per protein.  
**Confidence threshold: ≥ 0.85** (maximum class probability)

- Below threshold: prediction discarded ("low_confidence")
- At threshold: prediction retained for downstream analysis

Applied to 184,394 dark matter proteins:  
- High-confidence: 164,288 (89.1%)
- 92.3% of high-confidence predictions exceed 95% confidence

The 0.85 threshold was selected by inspecting the precision-recall curve on the held-out test set. It corresponds to an empirical precision of ~0.95 on the test data.

---

## 6. Metagenomic Datasets

### Tara Oceans — ERR315858
- **Source:** European Nucleotide Archive (ENA)
- **Location:** Indian Ocean surface (0–5 m), TARA_070 station
- **Reference:** Sunagawa et al. 2015, *Science* 348:1261359
- **Assembly:** MEGAHIT v1.2.9 (`--min-contig-len 500`)
- **Gene prediction:** Prodigal v2.6.3 (meta mode, `-p meta`)
- **Output:** 2,010 high-confidence phage protein predictions

### Red Sea KAUST Expedition — SRR2102994
- **Source:** NCBI SRA
- **Location:** Red Sea surface, KAUST Expedition 2010–2011
- **Reference:** Thompson et al. 2017, *ISME J* 11:138
- **Assembly:** MEGAHIT v1.2.9 (`--min-contig-len 500`)
- **Contigs assembled:** 42,673
- **Gene prediction:** Prodigal v2.6.3 (meta mode)
- **Proteins predicted:** 87,185
- **High-confidence predictions:** 81,359 (93.3%)

---

## 7. Statistical Testing

**Test:** `statsmodels.stats.proportion.proportions_ztest` (two-tailed)  
Each class proportion in the ocean dataset is tested against the global RefSeq baseline.

**Correction:** Bonferroni correction for 4 simultaneous comparisons  
- Unadjusted α = 0.05
- Adjusted α = 0.05 / 4 = **0.0125**

All reported significance levels (***) exceed this corrected threshold by multiple orders of magnitude (all z > 5, all p < 10⁻⁶).

---

## 8. BLAST Validation

Representative high-confidence predictions (n = 40, 10 per class) were BLASTed against:
- **NCBI nr** (non-redundant protein database) — confirms annotation class
- **Swiss-Prot** (manually curated experimental annotations) — checks experimental characterization

Results: All four classes confirmed by nr homology; zero Swiss-Prot hits across all classes.  
Interpretation: The predicted proteins exist in sequence space (validated by nr) but have never been biochemically characterized (no Swiss-Prot entry) — true dark matter illuminated.

---

## 9. Biological Interpretation Framework

The convergent surface-ocean signal (host_interaction enrichment, structural depletion) is interpreted through three established ecological frameworks:

1. **Kill-the-winner dynamics** (Thingstad 2000, *Limnol Oceanogr* 45:1320): Dominant bacterial taxa attract phage predation → arms race lives in receptor-binding proteins → selection pressure on host_interaction class
2. **Oligotrophic capsid economics:** Building elaborate capsid structures costs amino acids and ATP; nutrient-poor surface waters favor simpler capsid architectures → structural depletion
3. **Host range breadth:** Hyper-diverse, fast-dividing surface bacterial communities reward generalist receptor-binding over specialist → host_interaction enrichment

---

*Full pipeline notebooks available after competition submission (September 2026).*  
*Contact: samerjahran@gmail.com*
