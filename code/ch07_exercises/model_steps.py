"""Numerically check the CNN, GNN and attention figures in chapter 7.

Run from the repository root: python code/ch07_exercises/model_steps.py
Dependency: NumPy. Inputs are fixed teaching examples; no random seed is needed.
These are forward computations, not trained models or performance evaluations.
The GNN omits self-loops and learnable transforms; the attention example shows
one query and one head, not a complete Transformer encoder.
"""

import sys

import numpy as np


def cnn_step():
    """Apply the same kernel at both positions, with no kernel reversal."""
    signal = np.array([1.0, 2.0, 4.0, 3.0])
    kernel = np.array([-1.0, 0.0, 1.0])
    # Deep-learning convolution uses cross-correlation: stride=1, padding=0.
    windows = np.lib.stride_tricks.sliding_window_view(signal, len(kernel))
    response = windows @ kernel
    np.testing.assert_allclose(response, [3.0, 1.0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(
        response, np.correlate(signal, kernel, mode="valid"), rtol=0, atol=1e-12
    )
    print("CNN windows:", windows.tolist())
    print("CNN shared kernel:", kernel.tolist(), "->", response.tolist())


def gnn_step():
    """Aggregate neighbors synchronously, then check a relabeling of nodes."""
    adjacency = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]], dtype=float)
    features = np.array([[1.0], [2.0], [4.0]])
    # All messages use the old features. There is no in-place node update.
    updated = adjacency @ features
    np.testing.assert_allclose(updated[:, 0], [2.0, 5.0, 2.0], rtol=0, atol=1e-12)
    graph_sum = updated.sum(axis=0)
    np.testing.assert_allclose(graph_sum, [9.0], rtol=0, atol=1e-12)

    # Swap the first and second node labels in both A and H.
    permutation = np.eye(3)[[1, 0, 2]]
    relabeled_adjacency = permutation @ adjacency @ permutation.T
    relabeled_features = permutation @ features
    relabeled_updated = relabeled_adjacency @ relabeled_features
    np.testing.assert_allclose(relabeled_updated, permutation @ updated, rtol=0, atol=1e-12)
    np.testing.assert_allclose(relabeled_updated[:, 0], [5.0, 2.0, 2.0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(relabeled_updated.sum(axis=0), graph_sum, rtol=0, atol=1e-12)
    print("GNN neighbor sums:", updated[:, 0].tolist(), "graph sum:", graph_sum.item())
    print("GNN after relabeling:", relabeled_updated[:, 0].tolist())


def row_softmax(scores):
    """Normalize each query row; each row must have an allowed, finite key."""
    if not np.all(np.any(np.isfinite(scores), axis=-1)):
        raise ValueError("Each query must have at least one finite score.")
    weights = np.exp(scores - scores.max(axis=-1, keepdims=True))
    return weights / weights.sum(axis=-1, keepdims=True)


def attention_step():
    """Compute QK^T / sqrt(d_k), row softmax, then a weighted sum of V."""
    query = np.array([[1.0]])  # one query, d_k=1
    keys = np.array([[0.0], [np.log(3.0)]])  # two keys, d_k=1
    values = np.array([[2.0], [6.0]])  # two values, d_v=1
    scores = query @ keys.T / np.sqrt(query.shape[-1])
    weights = row_softmax(scores)
    output = weights @ values
    np.testing.assert_allclose(weights, [[0.25, 0.75]], rtol=0, atol=1e-12)
    np.testing.assert_allclose(weights.sum(axis=-1), [1.0], rtol=0, atol=1e-12)
    np.testing.assert_allclose(output, [[5.0]], rtol=0, atol=1e-12)

    mask = np.array([[0.0, -np.inf]])  # the query cannot read the second key
    masked_weights = row_softmax(scores + mask)
    masked_output = masked_weights @ values
    np.testing.assert_allclose(masked_weights, [[1.0, 0.0]], rtol=0, atol=1e-12)
    np.testing.assert_allclose(masked_output, [[2.0]], rtol=0, atol=1e-12)
    print("Attention weights:", np.round(weights, 12).tolist(), "output:", output.item())
    print("Masked weights:", masked_weights.tolist(), "output:", masked_output.item())


def main():
    print(f"Python {sys.version.split()[0]}; NumPy {np.__version__}")
    cnn_step()
    gnn_step()
    attention_step()
    print("All forward-example checks passed (atol=1e-12). No model training performed.")


if __name__ == "__main__":
    main()
