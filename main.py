"""
problem description in gurobi.
timeslots, subchannels and things are configurable.
in each timeslot we assign a subchannel to each thing.

please refer to problem statement in
https://github.com/citado/RoadToPhD
"""

import itertools

import gurobipy as gp
from gurobipy import GRB

SUBCHANNELS = 5
SLOTS = 4
THINGS = 10

min_spreading_factor = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
]

assert len(min_spreading_factor) == THINGS

try:
    m = gp.Model("aoi")

    x = m.addVars(THINGS, SLOTS, vtype=GRB.INTEGER, name="x")
    p = m.addVars(THINGS, SUBCHANNELS, SLOTS, vtype=GRB.BINARY, name="p")

    m.setObjective(x.sum(), GRB.MINIMIZE)

    m.addConstrs(
        (
            p.sum("*", c, t) <= 1
            for (c, t) in itertools.product(range(SUBCHANNELS), range(SLOTS))
        ),
        name="subchannel_limit",
    )

    m.addConstrs(
        (
            p.sum(i, "*", t) <= 1
            for (i, t) in itertools.product(range(THINGS), range(SLOTS))
        ),
        name="thing_limit",
    )

    # please consider that models that have large matrix coefficient rang
    # may have numerical issues.
    m.addConstrs(
        (
            (-SLOTS * p.sum(i, "*", t)) + x[i, t] + 1 <= x[i, t + 1]
            for (i, t) in itertools.product(range(THINGS), range(SLOTS - 1))
        ),
        name="aoi_limit",
    )

    m.addConstrs(
        (
            p[i, s, t] == 0
            for (i, t) in itertools.product(range(THINGS), range(SLOTS))
            for s in range(min_spreading_factor[i][t])
        ),
        name="spreading_factor_min",
    )

    m.optimize()

    for t in range(SLOTS):
        print(f"slot {t}:")

        for i in range(THINGS):
            x = m.getVarByName(f"x[{i},{t}]")
            assert x is not None
            print(f"\tage of information for thing {i}: {x.X}")

    for t in range(SLOTS):
        print(f"slot {t}:")

        for i in range(THINGS):
            for c in range(SUBCHANNELS):
                p = m.getVarByName(f"p[{i},{c},{t}]")
                assert p is not None
                if p.X == 1:
                    print(f"\tthing {i} is using subchannel {c}")

    print(f"Obj: {m.ObjVal}")

    m.write("model.lp")

except gp.GurobiError as e:
    print(f"Error code {e.errno}: {e}")

except AttributeError:
    print("Encountered an attribute error")
