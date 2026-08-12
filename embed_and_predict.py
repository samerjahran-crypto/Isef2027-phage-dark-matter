"""
embed_and_predict.py
--------------------
Predict the functional class of phage proteins using ESM-2 embeddings
and the PhageAMR-Finder v6b MLP classifier.

This script is a working demo of the core pipeline. Give it a FASTA file
of phage protein sequences and it will return a functional class prediction
for each one — even proteins with zero BLAST hits.

The classifier (v6b) was trained on 1,541 sequences across 8 functional
classes and achieves a cross-validated macro F1 of 0.9670 ± 0.0174 under
strict cluster-aware GroupKFold evaluation at a 70% identity threshold.
Performance at stricter thresholds: 50% → 0.9685, 40% → 0.9724,
30% → 0.8663. The model includes a non_phage class that correctly rejects
human G-protein coupled receptors (n=434) 100% of the time.

Note on model versioning
------------------------
Earlier versions of this pipeline (v4, v5) used smaller training sets and
less rigorous evaluation. v6b added scrambled-sequence and diverse human
protein negatives, tightening the out-of-distribution rejection. The
lower headline F1 (0.9670 vs 0.9771 in v4) reflects harder evaluation,
not degraded performance. v6b is the canonical competition version.

Note on the candidate
----------------------
The lead antimicrobial peptide candidate identified by this pipeline is
k99_98199_25: a 54-aa cationic peptide (net charge +10.49) from a
Caudoviricetes-like contig in the Red Sea metagenome SRR2102994.
An earlier candidate (k99_19554_1) was retired after flanking-ORF
analysis showed it was bacterial CcmB in an intact CcmABC operon, not
a phage protein. The pipeline was redesigned in response: geNomad viral
contig filtering now runs before classification. The retired candidate
is documented as a false-positive case study in the accompanying paper.

Model files (classifier_v6b.pkl, label_encoder_v6b.pkl) are available at:
    https://doi.org/10.5281/zenodo.20935067

Requirements:
    pip install fair-esm scikit-learn torch joblib

Usage:
    python embed_and_predict.py --fasta your_sequences.faa

Optional:
    --classifier  path to classifier_v6b.pkl   (default: classifier_v6b.pkl)
    --label_enc   path to label_encoder_v6b.pkl (default: label_encoder_v6b.pkl)
    --threshold   confidence cutoff             (default: 0.50)
    --batch_size  ESM-2 batch size              (default: 4, reduce if OOM)
    --verbose     print all class probabilities
"""

import argparse
import numpy as np
import torch

CLASS_DESCRIPTIONS = {
    "host_binding":        "Tail fibers, receptor-binding proteins, depolymerases",
    "membrane_disruption": "Holins, endolysins, spanins — membrane-active peptides",
    "iron_acquisition":    "Iron and heme uptake auxiliary metabolic genes",
    "structural":          "Capsid, portal, tail tube, terminase",
    "replication":         "DNA polymerase, helicase, primase, recombinase",
    "regulatory":          "CI/CII repressors, antiterminators, sigma factors",
    "metabolic_amg":       "Auxiliary metabolic genes (psbA, phoH, sulfur, phosphate)",
    "non_phage":           "Does not match any phage functional class",
    "unknown_dark":        "Confidence below threshold — unresolved dark matter",
}

VALID_AA = set("ACDEFGHIKLMNPQRSTVWY")


def load_fasta(path):
    """Read a FASTA file and return a dict of {header: sequence}."""
    sequences = {}
    header = None
    parts = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if header:
                    sequences[header] = "".join(parts)
                header = line[1:]
                parts = []
            else:
                parts.append(line)
    if header:
        sequences[header] = "".join(parts)
    return sequences


def clean(seq):
    """Strip non-standard amino acids."""
    return "".join(c for c in seq.upper() if c in VALID_AA)


def embed(sequences, batch_size=4):
    """
    Embed sequences with ESM-2 (esm2_t12_35M_UR50D), layer 12,
    mean-pooled over residue positions. Returns (embeddings, headers).
    """
    import esm

    print("Loading ESM-2 (esm2_t12_35M_UR50D)...")
    model, alphabet = esm.pretrained.esm2_t12_35M_UR50D()
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    converter = alphabet.get_batch_converter()
    print(f"  Device: {device}\n")

    valid, headers = [], []
    for h, s in sequences.items():
        s = clean(s)
        if 10 <= len(s) <= 1022:
            valid.append((h, s))
            headers.append(h)
        else:
            print(f"  Skipped {h[:50]} — length {len(s)} outside 10-1022")

    embeddings = []
    print(f"Embedding {len(valid)} sequences...")
    for i in range(0, len(valid), batch_size):
        batch = valid[i: i + batch_size]
        _, _, tokens = converter(batch)
        tokens = tokens.to(device)
        with torch.no_grad():
            out = model(tokens, repr_layers=[12], return_contacts=False)
        for j, (_, s) in enumerate(batch):
            emb = out["representations"][12][j, 1:len(s) + 1].mean(0).cpu().numpy()
            embeddings.append(emb)
        if i % (batch_size * 5) == 0:
            print(f"  {min(i + batch_size, len(valid))}/{len(valid)}")

    print(f"  Done. {len(embeddings)} embeddings (480-dim each).\n")
    return np.array(embeddings), headers


def classify(embeddings, clf, le, threshold):
    """Run the MLP classifier and return results."""
    probs = clf.predict_proba(embeddings)
    results = []
    for i in range(len(embeddings)):
        top_idx = int(np.argmax(probs[i]))
        top_prob = float(probs[i][top_idx])
        top_class = le.classes_[top_idx]
        assigned = top_class if top_prob >= threshold else "unknown_dark"
        all_probs = {le.classes_[j]: round(float(probs[i][j]), 4)
                     for j in range(len(le.classes_))}
        results.append({
            "assigned": assigned,
            "top_class": top_class,
            "confidence": round(top_prob, 4),
            "above_threshold": top_prob >= threshold,
            "description": CLASS_DESCRIPTIONS.get(assigned, ""),
            "all_probs": all_probs,
        })
    return results


def main():
    parser = argparse.ArgumentParser(
        description="PhageAMR-Finder v6b — classify phage proteins by function"
    )
    parser.add_argument("--fasta",      default="example_proteins.faa")
    parser.add_argument("--classifier", default="classifier_v6b.pkl")
    parser.add_argument("--label_enc",  default="label_encoder_v6b.pkl")
    parser.add_argument("--threshold",  type=float, default=0.50)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--verbose",    action="store_true")
    args = parser.parse_args()

    import joblib

    print(f"Reading {args.fasta}...")
    sequences = load_fasta(args.fasta)
    print(f"  {len(sequences)} sequences found.\n")

    embeddings, headers = embed(sequences, batch_size=args.batch_size)
    if len(embeddings) == 0:
        print("Nothing to classify.")
        return

    print("Loading model (v6b)...")
    clf = joblib.load(args.classifier)
    le  = joblib.load(args.label_enc)
    print(f"  Classes: {list(le.classes_)}\n")

    results = classify(embeddings, clf, le, args.threshold)

    print("=" * 68)
    print(f"{'Protein':<32} {'Assigned class':<22} {'Confidence':>10}")
    print("=" * 68)

    for header, r in zip(headers, results):
        name = header[:30] + ".." if len(header) > 32 else header
        flag = "" if r["above_threshold"] else "  ⚠ low"
        print(f"{name:<32} {r['assigned']:<22} {r['confidence']:>10.4f}{flag}")

        if args.verbose:
            for cls, p in sorted(r["all_probs"].items(),
                                  key=lambda x: x[1], reverse=True):
                bar = "█" * int(p * 25)
                print(f"    {cls:<22} {p:.4f}  {bar}")
            print()

    n_above   = sum(r["above_threshold"] for r in results)
    n_nonphage = sum(1 for r in results if r["assigned"] == "non_phage")
    n_unknown  = sum(1 for r in results if r["assigned"] == "unknown_dark")

    print("=" * 68)
    print(f"\nSummary: {len(results)} sequences total")
    print(f"  Classified (≥{args.threshold}): {n_above}")
    print(f"  non_phage: {n_nonphage}")
    print(f"  unknown_dark: {n_unknown}")
    print(f"\nPhageAMR-Finder v6b | CV Macro F1 = 0.9670 ± 0.0174")
    print(f"Cluster-aware (30% id): 0.8663 | GPCR OOD rejection: 100%")
    print(f"Zenodo: https://doi.org/10.5281/zenodo.20935067")


if __name__ == "__main__":
    main()
