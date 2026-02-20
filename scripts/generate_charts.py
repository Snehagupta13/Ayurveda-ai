"""
generate_charts.py
Generates training loss charts from actual training run data.
Run once: python generate_charts.py
Output: assets/training_curves.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

os.makedirs("assets", exist_ok=True)

# ── Actual data from your training run ──────────────────────
step_losses = [
    2.9534, 1.2853, 0.6391, 0.4825, 0.4102, 0.4231,
    0.3646, 0.3780, 0.3030, 0.3395, 0.4531,  # epoch 1
    0.3861, 0.3121, 0.3046, 0.3205, 0.3391, 0.2840,
    0.2992, 0.3091, 0.3344, 0.3375, 0.3009,  # epoch 2
    0.2739, 0.2743, 0.2886, 0.2321, 0.2830, 0.3138,
    0.2660, 0.3053, 0.2637, 0.3071, 0.3924,  # epoch 3
]
steps = list(range(0, len(step_losses) * 10, 10))

epoch_data = [
    {"epoch": 1, "train": 0.6211, "eval": 0.3508},
    {"epoch": 2, "train": 0.3087, "eval": 0.3568},
    {"epoch": 3, "train": 0.2705, "eval": 0.3422},
]
epochs      = [d["epoch"]  for d in epoch_data]
train_loss  = [d["train"]  for d in epoch_data]
eval_loss   = [d["eval"]   for d in epoch_data]

# ── Plot ─────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("MedGemma Ayurveda Fine-Tuning Results",
             fontsize=14, fontweight="bold", y=1.02)

# Chart 1: Step-level loss
ax1 = axes[0]
colors = (["#2196F3"] * 11 + ["#4CAF50"] * 11 + ["#FF5722"] * 11)[:len(steps)]
ax1.plot(steps, step_losses, color="#546E7A", linewidth=1.5, alpha=0.4)
ax1.scatter(steps, step_losses, c=colors, s=30, zorder=5)
ax1.axhline(y=step_losses[-1], color="red", linestyle="--", alpha=0.5, linewidth=1)
ax1.set_xlabel("Training Step")
ax1.set_ylabel("Loss")
ax1.set_title("Step-Level Training Loss")
ax1.grid(True, alpha=0.3)
patch1 = mpatches.Patch(color="#2196F3", label="Epoch 1")
patch2 = mpatches.Patch(color="#4CAF50", label="Epoch 2")
patch3 = mpatches.Patch(color="#FF5722", label="Epoch 3")
ax1.legend(handles=[patch1, patch2, patch3], fontsize=8)

# Annotate start and end
ax1.annotate(f"Start: {step_losses[0]:.2f}",
             xy=(steps[0], step_losses[0]),
             xytext=(20, -20), textcoords="offset points",
             fontsize=8, color="#2196F3",
             arrowprops=dict(arrowstyle="->", color="#2196F3"))
ax1.annotate(f"End: {step_losses[-1]:.2f}",
             xy=(steps[-1], step_losses[-1]),
             xytext=(-60, 10), textcoords="offset points",
             fontsize=8, color="#FF5722",
             arrowprops=dict(arrowstyle="->", color="#FF5722"))

# Chart 2: Epoch-level train vs eval
ax2 = axes[1]
ax2.plot(epochs, train_loss, "b-o", linewidth=2, markersize=8, label="Train Loss")
ax2.plot(epochs, eval_loss,  "r-s", linewidth=2, markersize=8, label="Eval Loss")
ax2.fill_between(epochs, train_loss, eval_loss, alpha=0.1, color="purple")
ax2.set_xlabel("Epoch")
ax2.set_ylabel("Loss")
ax2.set_title("Train vs Eval Loss per Epoch")
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xticks([1, 2, 3])
for e, tl, el in zip(epochs, train_loss, eval_loss):
    ax2.annotate(f"{tl:.4f}", (e, tl), textcoords="offset points",
                 xytext=(-15, 8), fontsize=8, color="blue")
    ax2.annotate(f"{el:.4f}", (e, el), textcoords="offset points",
                 xytext=(-15, -14), fontsize=8, color="red")

# Chart 3: Summary bar chart
ax3 = axes[2]
metrics = {
    "Start Loss\n(Step 0)":    2.9534,
    "End Loss\n(Epoch 3)":     0.2705,
    "Eval Loss\n(Epoch 3)":    0.3422,
    "Herb Accuracy\n(×3)":     0.75 * 3,  # scaled for visibility
}
bars = ax3.bar(metrics.keys(), metrics.values(),
               color=["#F44336","#4CAF50","#FF9800","#2196F3"],
               edgecolor="white", linewidth=1.5)
ax3.set_title("Key Metrics Summary")
ax3.set_ylabel("Value")
ax3.grid(True, alpha=0.3, axis="y")
for bar, (k, v) in zip(bars, metrics.items()):
    label = f"{v:.2f}" if "Accuracy" not in k else "75%"
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
             label, ha="center", va="bottom", fontweight="bold", fontsize=9)
ax3.tick_params(axis="x", labelsize=8)

plt.tight_layout()
plt.savefig("assets/training_curves.png", dpi=150, bbox_inches="tight")
print("Chart saved to assets/training_curves.png")

# Also save individual charts
fig2, ax = plt.subplots(figsize=(8, 5))
ax.plot(steps, step_losses, "b-o", markersize=4, linewidth=1.5)
ax.set_xlabel("Training Step")
ax.set_ylabel("Loss")
ax.set_title("MedGemma Ayurveda — Training Loss (2.95 → 0.27)")
ax.grid(True, alpha=0.3)
ax.fill_between(steps, step_losses,
                alpha=0.15, color="blue")
fig2.savefig("assets/loss_curve_simple.png", dpi=150, bbox_inches="tight")
print("Simple loss curve saved to assets/loss_curve_simple.png")
print("Done!")
