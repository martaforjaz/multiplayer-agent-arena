"""Draw the arena layout and measured benchmark results."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

from control_point import HEIGHT, OBSTACLES, RADIUS, TICKS, WIDTH

out = Path("benchmark")
report = json.loads((out / "control-point.json").read_text(encoding="utf-8"))
fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), layout="constrained")
arena, result = axes
arena.add_patch(Rectangle((0, 0), WIDTH, HEIGHT, facecolor="#edf2f7", edgecolor="#142d50"))
for xy in OBSTACLES:
    arena.add_patch(Circle(xy, RADIUS, color="#142d50"))
for y in (100, 210, 320):
    arena.add_patch(Circle((350, y), 45, fill=False, linestyle="--", edgecolor="#975f88"))
arena.scatter((80, WIDTH-80), (HEIGHT/2, HEIGHT/2), marker="D", c="#286783")
arena.set(xlim=(-12, WIDTH+12), ylim=(-12, HEIGHT+12), aspect="equal", title="a  Arena layout")
arena.set_axis_off()
points = report["control_ticks"]
total = report["matches"] * TICKS
contested = report["contested_ticks"]
counts = [points["Direct"], points["Predictive"], contested, total-sum(points.values())-contested]
shares = [n/total*100 for n in counts]
bars = result.barh(["Direct", "Predictive", "Contested", "Unoccupied"], shares,
                   color=["#286783", "#975f88", "#9dadbd", "#ced7df"])
result.bar_label(bars, fmt="%.1f%%", padding=4, fontsize=9)
result.invert_yaxis()
result.spines[["top", "right"]].set_visible(False)
result.set(xlim=(0, 90), xlabel="Share of simulation ticks (%)", title="b  Control-point occupancy")
fig.savefig(out / "control-point.svg")

