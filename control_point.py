"""Run paired, seeded control-point matches without opening a Pygame window."""
import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

import pymunk

POLICIES = ("Direct", "Predictive")
WIDTH, HEIGHT = 700, 420
DT = 1 / 60
TICKS = 60 * 30
OBSTACLES = ((245, 210), (455, 210))
RADIUS = 38


def match(seed, swapped=False):
    rng = random.Random(seed)
    space = pymunk.Space()
    space.damping = 0.65
    for x, y in OBSTACLES:
        obstacle = pymunk.Circle(space.static_body, RADIUS, (x, y))
        obstacle.elasticity = .5
        space.add(obstacle)
    names = POLICIES[::-1] if swapped else POLICIES
    agents = {}
    for name, x in zip(names, (80, WIDTH - 80)):
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 13))
        body.position = x, HEIGHT / 2
        shape = pymunk.Circle(body, 13)
        space.add(body, shape)
        agents[name] = body
    zones = [pymunk.Vec2d(350, rng.choice((100, 210, 320))) for _ in range(6)]
    # Both policies see the same state before the world advances.
    points = Counter(dict.fromkeys(POLICIES, 0))
    contested = 0
    for tick in range(TICKS):
        goal = zones[tick // 300]
        for name, body in agents.items():
            target = goal
            if name == "Predictive":
                for x, y in OBSTACLES:
                    obstacle = pymunk.Vec2d(x, y)
                    route = goal - body.position
                    if route.length < 1:
                        continue
                    along = (obstacle - body.position).dot(route.normalized())
                    if 0 < along < min(route.length, 120):
                        closest = body.position + route.normalized() * along
                        if (closest - obstacle).length < RADIUS + 18:
                            target = obstacle + (0, (RADIUS + 40) * (-1 if goal.y <= y else 1))
                            break
            desired = (target - body.position) * 4
            if desired.length > 145:
                desired = desired.normalized() * 145
            body.force = (desired - body.velocity) * 7
        space.step(DT)
        inside = [name for name, body in agents.items() if (goal - body.position).length <= 45]
        if len(inside) == 1:
            points[inside[0]] += 1
        elif len(inside) == 2:
            contested += 1
    assert sum(points.values()) + contested <= TICKS
    return {"seed": seed, "swapped": swapped, **points, "contested": contested}


def tournament(seeds):
    return [match(seed, swapped) for seed in seeds for swapped in (False, True)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=12, choices=range(1, 101), metavar="1–100")
    parser.add_argument("--output", type=Path, default=Path("benchmark"))
    args = parser.parse_args()
    rows = tournament(range(args.seeds))
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "control-point.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    totals = {name: sum(row[name] for row in rows) for name in POLICIES}
    report = {"matches": len(rows), "tick_rate": 60, "control_ticks": totals,
              "contested_ticks": sum(row["contested"] for row in rows)}
    (args.output / "control-point.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

