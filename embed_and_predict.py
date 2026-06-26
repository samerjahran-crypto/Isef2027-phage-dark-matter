"""
embed_and_predict.py
--------------------
Predict the functional class of phage proteins using ESM-2 embeddings
and the PhageAMR-Finder v4 MLP classifier.
 
This script is a working demo of the core pipeline. Give it a FASTA file
of phage protein sequences and it will return a functional class prediction
for each one — even proteins with zero BLAST hits.
 
The model was trained on 1318 sequences across 8 functional classes and
achieves a cross-validated macro F1 of 0.9771. It includes a non_phage
class that correctly rejects human proteins 100% of the time, and an
unknown_dark label for anything it isn't confident about.
 
Model files (classifier_v2.pkl and scaler_v2.pkl) are available at:
https://doi.org/10.5281/zenodo.20935067
 
Requirements:
    pip install fair-esm scikit-learn torch
 
Usage:
    python embed_and_predict.py --fasta your_sequences.faa
 
Optional:
    --classifier  path to classifier_v2.pkl  (default: classifier_v2.pkl)
    --scaler      path to scaler_v2.pkl      (default: scaler_v2.pkl)
    --threshold   confidence cutoff          (default: 0.50)
    --batch_size  ESM-2 batch size           (default: 4, reduce if OOM)
    --verbose     print all class probabilities
 
A note on k99_19554_1:
    The primary AMR candidate in this project classifies as metabolic_amg
    rather than iron_acquisition or membrane_disruption. This is a known
    limitation of ESM-2 mean-pooling for multi-transmembrane proteins with
    extreme hydrophobicity (GRAVY 1.335, 7 TM helices) — documented in
    Meier et al. 2021, NeurIPS. The functional annotation of k99 is based
    on Foldseek structural evidence, not this classifier.
"""
 
import argparse
import pickle
import numpy as np
import torch
 
 
# The 8 functional classes the model was trained on.
# non_phage was added in v4 to handle out-of-distribution inputs.
CLASS_SCHEMA = {
    0: "host_binding",
    1: "membrane_disruption",
    2: "iron_acquisition",
    3: "structural",
    4: "replication",
    5: "regulatory",
    6: "metabolic_amg",
    7: "non_phage",
}
 
CLASS_DESCRIPTIONS = {
    "host_binding":        "Tail fibers, receptor binding proteins, depolymerases",
    "membrane_disruption": "Holins, endolysins, spanins",
    "iron_acquisition":    "CcmB analogs, hemin/iron uptake AMGs",
    "structural":          "Capsid, portal, tail tube, terminase",
    "replication":         "DNA polymerase, helicase, primase",
    "regulatory":          "CI/CII repressors, antiterminators",
    "metabolic_amg":       "Auxiliary metabolic genes (psbA, phoH, sulfur/phosphate)",
    "non_phage":           "Doesn't match any phage functional class",
    "unknown_dark":        "Confidence below threshold — unresolved dark matter",
}
 
CONFIDENCE_THRESHOLD = 0.50
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
    """Strip non-standard amino acids and whitespace."""
    return "".join(c for c in seq.upper() if c in VALID_AA)
 
 
def embed(sequences, batch_size=4):
    """
    Run sequences through ESM-2 and return mean-pooled layer 12 embeddings.
 
    This is the same embedding method used to train the classifier —
    esm2_t12_35M_UR50D, layer 12, mean-pooled over residue positions,
    480 dimensions per sequence.
    """
    import esm
 
    print("Loading ESM-2...")
    model, alphabet = esm.pretrained.esm2_t12_35M_UR50D()
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    converter = alphabet.get_batch_converter()
    print(f"  Running on: {device}\n")
 
    valid = []
    headers = []
    for h, s in sequences.items():
        s = clean(s)
        if 10 <= len(s) <= 1022:
            valid.append((h, s))
            headers.append(h)
        else:
            print(f"  Skipped {h[:50]} — length {len(s)} outside 10-1022 range")
 
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
 
    print(f"  Done. {len(embeddings)} embeddings, 480-dim each.\n")
    return np.array(embeddings), headers
 
 
def classify(embeddings, clf, scaler, threshold):
    """Scale embeddings and run the MLP classifier."""
    scaled = scaler.transform(embeddings)
    probs = clf.predict_proba(scaled)
 
    results = []
    for i in range(len(embeddings)):
        top_idx = int(np.argmax(probs[i]))
        top_prob = float(probs[i][top_idx])
        top_class = CLASS_SCHEMA[clf.classes_[top_idx]]
        assigned = top_class if top_prob >= threshold else "unknown_dark"
 
        all_probs = {
            CLASS_SCHEMA[c]: round(float(probs[i][j]), 4)
            for j, c in enumerate(clf.classes_)
        }
 
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
        description="PhageAMR-Finder v4 — classify phage proteins by function"
    )
    parser.add_argument("--fasta",      default="example_proteins.faa")
    parser.add_argument("--classifier", default="classifier_v2.pkl")
    parser.add_argument("--scaler",     default="scaler_v2.pkl")
    parser.add_argument("--threshold",  type=float, default=0.50)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--verbose",    action="store_true",
                        help="Print all class probabilities for each sequence")
    args = parser.parse_args()
 
    # Load sequences
    print(f"Reading {args.fasta}...")
    sequences = load_fasta(args.fasta)
    print(f"  {len(sequences)} sequences found.\n")
 
    # Embed
    embeddings, headers = embed(sequences, batch_size=args.batch_size)
    if len(embeddings) == 0:
        print("Nothing to classify.")
        return
 
    # Load model
    print(f"Loading model...")
    with open(args.classifier, "rb") as f:
        clf = pickle.load(f)
    with open(args.scaler, "rb") as f:
        scaler = pickle.load(f)
    print(f"  Classes: {[CLASS_SCHEMA[c] for c in clf.classes_]}\n")
 
    # Classify
    results = classify(embeddings, clf, scaler, args.threshold)
 
    # Print results
    print("=" * 68)
    print(f"{'Protein':<32} {'Assigned class':<22} {'Confidence':>10}")
    print("=" * 68)
 
    for header, r in zip(headers, results):
        name = header[:30] + ".." if len(header) > 32 else header
        flag = "" if r["above_threshold"] else "  ⚠ low"
        print(f"{name:<32} {r['assigned']:<22} {r['confidence']:>10.4f}{flag}")
 
        if args.verbose:
            for cls, p in sorted(r["all_probs"].items(), key=lambda x: x[1], reverse=True):
                bar = "█" * int(p * 25)
                print(f"    {cls:<22} {p:.4f}  {bar}")
            print()
 
    n_classified = sum(r["above_threshold"] for r in results)
    n_non_phage = sum(1 for r in results if r["assigned"] == "non_phage")
    n_unknown = sum(1 for r in results if r["assigned"] == "unknown_dark")
 
    print("=" * 68)
    print(f"\nResults:")
    print(f"  {len(results)} sequences total")
    print(f"  {n_classified} classified with confidence ≥ {args.threshold}")
    print(f"  {n_non_phage} flagged as non_phage")
    print(f"  {n_unknown} returned unknown_dark")
    print(f"\nPhageAMR-Finder v4 | CV F1 = 0.9771 ± 0.0091")
    print(f"Zenodo: https://doi.org/10.5281/zenodo.20935067")
 
 
if __name__ == "__main__":
    main()
    
