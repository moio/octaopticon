import math
from ortools.sat.python import cp_model


def compute_valid_angles(A: int) -> list[int]:
    """Computes the set of unique integer filter angle offsets assuming the full angle is divided into A equal angles"""
    all = [360.0 / A * i for i in range(A)]

    # polarizing linear filters can be rotated 180 degrees with no change in behavior, reduce all angles to under 180 degrees
    reduced = [a % 180.0 for a in all]
    deduplicated = list(set(reduced))

    # CS-SAT only deals with integer values, round down
    rounded = [math.floor(a) for a in deduplicated]
    return sorted(rounded)


def compute_energy(previous_energy: int, Δ: int) -> int:
    """Computes energy flowing through two linear polarized filters rotated by Δ degrees with respect to one another"""
    return round(previous_energy * math.pow(math.cos(Δ * math.pi / 180.0), 2))


def compute_transitions(A: int, P: int) -> list[(int, int, int)]:
    """
    Returns a list of triplets (previous_energy, Δ, next_energy) representing the change in energy flowing through pairs of
    filters rotated by Δ degrees.
    The list constitutes a graph of all paths starting from energy 100 up to P filters.
    """
    transitions = set([])

    previous_energies = set([100])
    next_energies = set([])
    for _ in range(1, P):
        for previous_energy in previous_energies.copy():
            for Δ in compute_valid_angles(A):
                new_energy = compute_energy(previous_energy, Δ)

                # HACK: avoid duplicate states because off-by-one roundings
                if new_energy + 1 in next_energies:
                    new_energy = new_energy + 1
                if new_energy - 1 in next_energies:
                    new_energy = new_energy - 1

                transitions.add((previous_energy, Δ, new_energy))
                next_energies.add(new_energy)
        previous_energies = next_energies

    return sorted(transitions, reverse=True)


class Problem:
    """Represents all inputs to an Opticon problem (finding combinations of angles and rotations for an Opticon)."""

    def __init__(self, P: int, S: int, W: int, A: int, p: list[list[list[int]]]):
        """
            P is the count of identical and regular polygons in the stack ("pizzas")
                - pizza 0 is at the bottom of the stack, P at the top
            S is the count of triangles in pizzas ("slices")
                - 0 being the top-most, proceeding clockwise
            W is the count of windows per slice
                - 0 being the top left, proceeding by columns then rows
            A is the number of distinct angle offsets of filters in windows
            p is the list of pixels of images
                - p[m][j][k] is image m's pixel value at slice j and window k
                - values are in range 0-100 (rounded percent)
        """
        self.P = P
        self.S = S
        self.W = W
        self.A = A
        self.p = p

    def __str__(self) -> str:
        return f"{self.P} pizzas, {self.S} slices, {self.W} windows per slice, {self.A} possible angles, {len(self.p)} images"


class Solution:
    """Represents outputs of an Opticon problem."""

    def __init__(self, success: bool, wall_time: float, α: list[list[list[int]]], n: list[list[int]], d: list[list[int]], j_corrected: list[list[list[int]]], α_corrected: list[list[list[list[int]]]]):
        """
            α the list of angles for each filter on each window
                - α[i][j][k] is the angle of the filter at window k on slice j on pizza i
            n is the list of offsets, measured in slices, of each pizza in the stack to obtain a certain image
                - n[m][i] is the slice offset of pizza i to get the image m (measured clock-wise)
            d is the list of substitutions of each pizza in the stack to obtain a certain image
                - d[m][s] is the pizza index at stack position s to get the image m (where bottom is 0)

            Other parameters are internal and added for testing/debugging purposes only
        """
        self.success = success
        self.wall_time = wall_time
        self.α = α
        self.n = n
        self.d = d
        self.j_corrected = j_corrected
        self.α_corrected = α_corrected


def solve(problem: Problem) -> Solution:
    """
    Finds combinations of angles and rotations for an Opticon.

        P is the count of identical and regular polygons in the stack ("pizzas")
            - pizza 0 is at the bottom of the stack, P at the top
        S is the count of triangles in pizzas ("slices")
            - 0 being the top-most, proceeding clockwise
        W is the count of windows per slice
            - 0 being the top left, proceeding by columns then rows
        A is the number of distinct angle offsets of filters in windows
        p is the list of pixels of images
            - p[m][j][k] is image m's pixel value at slice j and window k
            - values are in range 0-100 (rounded percent)

    Returns:
        α the list of angles for each filter on each window
            - α[i][j][k] is the angle of the filter at window k on slice j on pizza i
        n is the list of offsets, measured in slices, of each pizza in the stack to obtain a certain image
            - n[m][i] is the slice offset of pizza i to get the image m (measured clock-wise)
            - note that it's not defined for pizza 0 (there's nothing below)
    """
    # Model
    model = cp_model.CpModel()

    # Input Variables
    P = problem.P
    S = problem.S
    W = problem.W
    A = problem.A
    p = problem.p

    # Output Variables
    α_domain = cp_model.Domain.FromValues(compute_valid_angles(A))

    # α[i][j][k] is the angle of the filter at window k on slice j on pizza i
    α = []
    for i in range(P):
        α_i = []
        for j in range(S):
            α_ij = []
            for k in range(W):
                α_ijk = model.NewIntVarFromDomain(α_domain, f"α[{i}][{j}][{k}]")
                α_ij.append(α_ijk)
            α_i.append(α_ij)
        α.append(α_i)

    # n[m][i] is the slice offset (rotation) of pizza i to obtain the image m
    M = len(p)
    n = []
    for m in range(M):
        n_m = [0]
        for i in range(1, P):
            n_mi = model.NewIntVar(0, S - 1, f"n[{m}][{i}]")
            n_m.append(n_mi)
        n.append(n_m)

    # d[m][s] is the index i of the pizza at stack position s to obtain the image m
    d = []
    for m in range(M):
        d_m = []
        for s in range(P):
            d_ms = model.NewIntVar(0, P - 1, f"d[{m}][{s}]")
            d_m.append(d_ms)
        model.AddAllDifferent(d_m)
        d.append(d_m)

    # Intermediate Variables

    # j_corrected[j][m][i] is the index of the slice under slice j
    # corrected by its n[m][i] (how many slices pizza i is rotated)
    j_corrected = []
    for j in range(S):
        j_corrected_j = []
        for m in range(M):
            j_corrected_jm = []
            for i in range(P):
                j_corrected_jmi = model.NewIntVar(0, S - 1, f"j_corrected[{j}][{m}][{i}]")
                model.AddModuloEquality(j_corrected_jmi, j - n[m][i] + S, S)

                j_corrected_jm.append(j_corrected_jmi)
            j_corrected_j.append(j_corrected_jm)
        j_corrected.append(j_corrected_j)

    # α_ikj is α indexed by [i,k,j] instead of [i,j,k]
    α_ikj = []
    for i in range(P):
        α_i = []
        for k in range(W):
            α_ik = []
            for j in range(S):
                α_ik.append(α[i][j][k])
            α_i.append(α_ik)
        α_ikj.append(α_i)

    # α_corrected[j][k][m][i] is the angle of the filter at window k, slice j of pizza i
    # corrected by its n[m][i] (how many slices pizza i is rotated)
    α_corrected = []
    for j in range(S):
        α_corrected_j = []
        for k in range(W):
            α_corrected_jk = []
            for m in range(M):
                α_corrected_jkm = []
                for i in range(P):
                    α_corrected_element_jkmi = model.NewIntVarFromDomain(α_domain, f"α_corrected_element[{j}][{k}][{m}][{i}]")
                    model.AddElement(j_corrected[j][m][i], α_ikj[i][k], α_corrected_element_jkmi)

                    α_corrected_unreduced_jkmi = model.NewIntVar(0, 180 + 360, f"α_corrected[{j}][{k}][{m}][{i}]")
                    model.Add(α_corrected_unreduced_jkmi == α_corrected_element_jkmi + math.floor(360.0 / S) * n[m][i])

                    α_corrected_jkmi = model.NewIntVar(0, 180, f"α_corrected[{j}][{k}][{m}][{i}]")
                    model.AddModuloEquality(α_corrected_jkmi, α_corrected_unreduced_jkmi, 180)

                    α_corrected_jkm.append(α_corrected_jkmi)
                α_corrected_jk.append(α_corrected_jkm)
            α_corrected_j.append(α_corrected_jk)
        α_corrected.append(α_corrected_j)

    # D[j][k][m][s] is the angle delta between filter in window k on slice j of pizza at stack index s
    # and the filter in the same location one pizza below
    # note that it's not defined for pizza 0 (there's nothing below)
    # note it depends on respective pizzas n[m][i]s (how many slices pizzas are rotated)
    D = []
    for j in range(S):
        D_j = []
        for k in range(W):
            D_jk = []
            for m in range(M):
                D_jkm = [None]
                for s in range(1, P):
                    α_corrected_jkms = model.NewIntVar(0, 180, f"α_corrected_jkms[{j}][{k}][{m}][{s}]")
                    model.AddElement(d[m][s], α_corrected[j][k][m], α_corrected_jkms)

                    α_corrected_jkms_ = model.NewIntVar(0, 180, f"α_corrected_jkms_[{j}][{k}][{m}][{s-1}]")
                    model.AddElement(d[m][s - 1], α_corrected[j][k][m], α_corrected_jkms_)

                    D_unreduced_jkms = model.NewIntVar(-180, 180, f"D_unreduced_jkms[{j}][{k}][{m}][{s}]")
                    model.Add(D_unreduced_jkms == α_corrected_jkms - α_corrected_jkms_)

                    D_jkms = model.NewIntVar(0, 180, f"D[{j}][{k}][{m}][{s}]")
                    model.AddModuloEquality(D_jkms, D_unreduced_jkms + 360 * 10, 180)
                    D_jkm.append(D_jkms)
                D_jk.append(D_jkm)
            D_j.append(D_jk)
        D.append(D_j)

    # Constraints
    transitions = compute_transitions(A, P)
    for m in range(M):
        for j in range(S):
            for k in range(W):
                start_state = 100
                end_state = p[m][j][k]
                model.AddAutomaton(D[j][k][m][1:], start_state, [end_state], transitions)

    # Solve
    solver = cp_model.CpSolver()
    solver.parameters.log_search_progress = True
    solver.parameters.max_time_in_seconds = 60

    status = solver.Solve(model)

    success = None
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        success = True
    elif status == cp_model.INFEASIBLE:
        success = False
    elif status == cp_model.UNKNOWN:
        success = None
    elif status == cp_model.MODEL_INVALID:
        raise cp_model.MODEL_INVALID

    return Solution(
        success,
        solver.WallTime(),
        [[[solver.Value(α[i][j][k]) for k in range(W)] for j in range(S)] for i in range(P)] if success else [],
        [[solver.Value(n[m][i]) for i in range(P)] for m in range(M)] if success else [],
        [[solver.Value(d[m][s]) for s in range(P)] for m in range(M)] if success else [],
        [[[solver.Value(j_corrected[j][m][i]) for i in range(P)] for m in range(M)] for j in range(S)] if success else [],
        [[[[solver.Value(α_corrected[j][k][m][i]) for i in range(P)] for m in range(M)] for k in range(W)] for j in range(S)] if success else [],
    )
