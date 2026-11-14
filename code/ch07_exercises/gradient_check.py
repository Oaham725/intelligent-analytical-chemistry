"""Check the gradients in section 7.2 using central differences."""

import numpy as np


def forward(parameters, x, y):
    w1, b1, w2, b2 = parameters
    a = w1 @ x + b1
    h = np.maximum(a, 0)
    z = w2 @ h + b2
    shifted = z - z.max()
    exp = np.exp(shifted)
    loss = np.log(exp.sum()) - y @ shifted
    return loss, a, h, exp / exp.sum() - y


def main():
    parameters = [
        np.array([[0.2, -0.4], [0.3, 0.5], [-0.2, 0.1]]),
        np.array([0.1, 0.2, -0.1]),
        np.array([[0.3, -0.2, 0.5], [-0.1, 0.4, 0.2]]),
        np.zeros(2),
    ]
    x = np.array([0.7, -0.3])
    y = np.array([0, 1])
    _, a, h, g = forward(parameters, x, y)
    delta = (parameters[2].T @ g) * (a > 0)
    gradients = [np.outer(delta, x), delta, np.outer(g, h), g]

    step = 1e-5
    max_error = 0.0
    for values, analytic in zip(parameters, gradients):
        for index in np.ndindex(values.shape):
            original = values[index]
            values[index] = original + step
            plus = forward(parameters, x, y)[0]
            values[index] = original - step
            minus = forward(parameters, x, y)[0]
            values[index] = original
            max_error = max(max_error, abs(analytic[index] - (plus - minus) / (2 * step)))
    assert max_error < 1e-8
    print(f"Max absolute gradient error: {max_error:.3e}")


if __name__ == "__main__":
    main()
