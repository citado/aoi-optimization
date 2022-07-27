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
    slots = 10
    things = 20

    x = m.addVars(things, slots, vtype=GRB.INTEGER, name="x")
    p = m.addVars(things, subchannels, slots, vtype=GRB.BINARY, name="p")

    m.addConstrs(
        (
            p.sum("*", c, t) <= 1
            for (c, t) in itertools.product(range(subchannels), range(slots))
        ),
        name="subchannel_limit",
    )

    m.addConstrs(
        p.sum(i, "*", t) <= 1
        for (i, t) in itertools.product(range(things), range(slots))
    )

    m.addConstrs(
        -GRB.INFINITY * sum(p[i, "*", t]) + x[i, t] + 1 <= x[i, t + 1]
        for (i, t) in itertools.product(range(things), range(slots - 1))
    )

    m.setObjective(x.sum(), GRB.MINIMIZE)

    m.optimize()

    for v in m.getVars():
        print(f"{v.VarName}, {v.X}")

    print(f"Obj: {m.ObjVal}")

except gp.GurobiError as e:
    print(f"Error code {e.errno}: {e}")

except AttributeError:
    print("Encountered an attribute error")
