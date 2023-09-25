from ortools.sat.python import cp_model


def solve():
    """Minimal CP-SAT example to showcase calling the solver."""
    # Model
    model = cp_model.CpModel()

    # Variables
    var_upper_bound = max(50, 45, 37)
    x = model.NewIntVar(0, var_upper_bound, "x")
    y = model.NewIntVar(0, var_upper_bound, "y")
    z = model.NewIntVar(0, var_upper_bound, "z")

    # Constraints
    model.Add(2 * x + 7 * y + 3 * z <= 50)
    model.Add(3 * x - 5 * y + 7 * z <= 45)
    model.Add(5 * x + 2 * y - 6 * z <= 37)

    # Objective
    model.Maximize(2 * x + 2 * y + 3 * z)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        return {"x": solver.Value(x), "y": solver.Value(y), "z": solver.Value(z)}
    else:
        return None
