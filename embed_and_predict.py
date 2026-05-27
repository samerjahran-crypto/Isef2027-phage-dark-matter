"""
embed_and_predict.py
--------------------
Demo: predict functional class for phage proteins using ESM-2 + trained MLP.

This is a minimal, self-contained demonstration of the core methodology.
It runs on the 10 example sequences in example_proteins.faa.

Full pipeline (assembly, clustering, batch processing of 184,394 proteins,
statistical tests, figure generation) is available upon request after
competition submission.

Requirements:
    pip install fair-esm scikit-learn torch joblib

Usage:
    python embed_and_predict.py --fasta example_proteins.faa --model mlp_classifier.pkl --encoder label_encoder.pkl
"""

import argparse
import torch
import joblib
import numpy as np
from pathlib import Path


# ── helpers ──────────────────────────────────────────────────────────────────

def load_fasta(path: str) -> dict:
    """Parse a FASTA file into {header: sequence} dict."""
    sequences = {}
    header = None
    seq_parts = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if header:
                    sequences[header] = "".join(seq_parts)
                header = line[1:]
                seq_parts = []
            else:
                seq_parts.append(line)
    if header:
        sequences[header] = "".join(seq_parts)
    return sequences


def embed_sequences(sequences: dict, batch_size: int = 8) -> np.ndarray:
    """
    Generate ESM-2 embeddings for a dict of sequences.

    Model: esm2_t12_35M_UR50D (480-dim, ~35M parameters)
    Pooling: mean over sequence length positions
    Returns: ndarray of shape (n_sequences, 480)
    """
    import esm

    model, alphabet = esm.pretrained.esm2_t12_35M_UR50D()
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    batch_converter = alphabet.get_batch_converter()

    headers = list(sequences.keys())
    seqs = [(h, sequences[h]) for h in headers]
    all_embeddings = []

    for i in range(0, len(seqs), batch_size):
        batch = seqs[i : i + batch_size]
        _, _, tokens = batch_converter(batch)
        tokens = tokens.to(device)
        with torch.no_grad():
            results = model(tokens, repr_layers=[12], return_contacts=False)
        # Mean-pool over sequence positions (exclude BOS/EOS tokens)
        for j, (_, seq) in enumerate(batch):
            token_embeddings = results["representations"][12][j, 1 : len(seq) + 1]
            embedding = token_embeddings.mean(0).cpu().numpy()
            all_embeddings.append(embedding)

        if (i // batch_size) % 5 == 0:
            print(f"  Embedded {min(i + batch_size, len(seqs))}/{len(seqs)} proteins")

    return np.array(all_embeddings), headers


def predict(embeddings: np.ndarray, clf, le, threshold: float = 0.85):
    """
    Predict functional class and confidence score.

    threshold: minimum softmax probability to retain prediction.
               Predictions below threshold are labeled 'low_confidence'.
    """
    probs = clf.predict_proba(embeddings)          # shape (n, 4)
    max_probs = probs.max(axis=1)
    pred_indices = probs.argmax(axis=1)
    pred_labels = le.inverse_transform(pred_indices)

    results = []
    for i, (label, conf) in enumerate(zip(pred_labels, max_probs)):
        results.append({
            "predicted_class": label if conf >= threshold else "low_confidence",
            "confidence": round(float(conf), 4),
            "high_confidence": conf >= threshold,
            "class_probabilities": {
                cls: round(float(probs[i, j]), 4)
                for j, cls in enumerate(le.classes_)
            },
        })
    return results


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Predict phage protein function via ESM-2 + MLP")
    parser.add_argument("--fasta",   default="example_proteins.faa", help="Input FASTA file")
    parser.add_argument("--model",   default="mlp_classifier.pkl",   help="Trained MLP (joblib)")
    parser.add_argument("--encoder", default="label_encoder.pkl",    help="LabelEncoder (joblib)")
    parser.add_argument("--threshold", type=float, default=0.85,     help="Confidence threshold")
    parser.add_argument("--batch-size", type=int, default=8,         help="ESM-2 batch size")
    args = parser.parse_args()

    # ── load ──
    print(f"Loading sequences from {args.fasta} ...")
    sequences = load_fasta(args.fasta)
    print(f"  {len(sequences)} sequences loaded.\n")

    print("Generating ESM-2 embeddings ...")
    embeddings, headers = embed_sequences(sequences, batch_size=args.batch_size)
    print(f"  Embedding matrix: {embeddings.shape}\n")

    print("Loading classifier ...")
    clf = joblib.load(args.model)
    le  = joblib.load(args.encoder)
    print(f"  Classes: {list(le.classes_)}\n")

    print("Predicting functional classes ...")
    results = predict(embeddings, clf, le, threshold=args.threshold)

    # ── report ──
    print("\n" + "=" * 65)
    print(f"{'Protein':<30} {'Class':<20} {'Confidence':>10}")
    print("=" * 65)
    for header, result in zip(headers, results):
        label = result["predicted_class"]
        conf  = result["confidence"]
        flag  = "" if result["high_confidence"] else "  ⚠ low"
        short_header = header[:28] + ".." if len(header) > 30 else header
        print(f"{short_header:<30} {label:<20} {conf:>10.4f}{flag}")

    n_hc = sum(r["high_confidence"] for r in results)
    print("=" * 65)
    print(f"\nHigh-confidence predictions (≥{args.threshold}): {n_hc}/{len(results)}")


if __name__ == "__main__":
    main()
