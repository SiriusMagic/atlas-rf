"""Illustrative plots. These are analytical proxies, not EM-solver field maps."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .model import cosine_power_pattern


def make_plots(output_dir: str | Path, frequency_hz: float):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    # Angular cut: broadside +Y is theta=0.
    theta = np.linspace(-np.pi / 2, np.pi / 2, 721)
    field = cosine_power_pattern(np.abs(theta), exponent=8)
    power_db = 10 * np.log10(np.maximum(field**2, 1e-6))
    fig, ax = plt.subplots()
    ax.plot(np.degrees(theta), power_db)
    ax.set(title="Illustrative normalized angular cut (not EM validated)",
           xlabel="Angle from +Y boresight (degrees)", ylabel="Relative power (dB)")
    ax.set_ylim(-60, 1)
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(output / "illustrative_pattern.png", dpi=160)
    plt.close(fig)

    # Simple conceptual heatmap, deliberately labelled as an illustration.
    x = np.linspace(-1, 1, 301)
    z = np.linspace(-1, 1, 301)
    X, Z = np.meshgrid(x, z)
    H = np.exp(-5 * (X**2 + Z**2))
    fig, ax = plt.subplots()
    im = ax.imshow(H, origin="lower", extent=[-1, 1, -1, 1], aspect="equal")
    fig.colorbar(im, ax=ax, label="Normalized illustrative intensity")
    ax.set(title="Conceptual heatmap — not a simulated EM field",
           xlabel="Normalized X coordinate", ylabel="Normalized Z coordinate")
    fig.tight_layout()
    fig.savefig(output / "conceptual_heatmap.png", dpi=160)
    plt.close(fig)
