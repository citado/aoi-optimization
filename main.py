"""
problem description in gurobi
here we only consider 10 time slots and 20 things to reduce problem size.
to have a very minimal problem, we only cosider that we have 5 different subchannels.
"""

import itertools

import gurobipy as gp
from gurobipy import GRB

try:
    m = gp.Model("aoi")

    subchannels = 5
    slots = 4
    things = 10

    x = m.addVars(things, slots, vtype=GRB.INTEGER, name="x")
    p = m.addVars(things, subchannels, slots, vtype=GRB.BINARY, name="p")

    m.setObjective(x.sum(), GRB.MINIMIZE)

    m.addConstrs(
        (
            p.sum("*", c, t) <= 1
            for (c, t) in itertools.product(range(subchannels), range(slots))
        ),
        name="subchannel_limit",
    )

    m.addConstrs(
        (
            p.sum(i, "*", t) <= 1
            for (i, t) in itertools.product(range(things), range(slots))
        ),
        name="thing_limit",
    )

    # please consider that models that have large matrix coefficient rang
    # may have numerical issues.
    m.addConstrs(
        (
            (-slots * p.sum(i, "*", t)) + x[i, t] + 1 <= x[i, t + 1]
            for (i, t) in itertools.product(range(things), range(slots - 1))
        ),
        name="aoi_limit",
    )

    m.optimize()

    for t in range(slots):
        print(f"slot {t}:")

        for i in range(things):
            x = m.getVarByName(f"x[{i},{t}]")
            print(f"\tage of information for thing {i}: {x.X}")

    for t in range(slots):
        print(f"slot {t}:")

        for i in range(things):
            for c in range(subchannels):
                p = m.getVarByName(f"p[{i},{c},{t}]")
                if p.X == 1:
                    print(f"\tthing {i} is using subchannel {c}")

    print(f"Obj: {m.ObjVal}")

    m.write("model.lp")

except gp.GurobiError as e:
    print(f"Error code {e.errno}: {e}")

except AttributeError:
    print("Encountered an attribute error")
