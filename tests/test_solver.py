import math
import random
import pytest
from solver.solver import Problem, compute_valid_angles, compute_energy, compute_transitions, solve


# Test valid input values

@pytest.mark.parametrize(
    "A,expected",
    [
        (1, [0]),
        (2, [0]),
        (3, [0, 60, 120]),
        (4, [0, 90]),
        (5, [0, 36, 72, 108, 144]),
        (6, [0, 60, 120]),
        (7, [0, 25, 51, 77, 102, 128, 154]),
        (8, [0, 45, 90, 135]),
        (9, [0, 20, 40, 60, 80, 100, 120, 140, 160]),
        (10, [0, 36, 72, 108, 144]),
        (11, [0, 16, 32, 49, 65, 81, 98, 114, 130, 147, 163]),
        (12, [0, 30, 60, 90, 120, 150]),
        (13, [0, 13, 27, 41, 55, 69, 83, 96, 110, 124, 138, 152, 166]),
        (14, [0, 25, 25, 51, 51, 77, 77, 102, 102, 128, 128, 154]),
        (15, [0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144, 156, 168]),
        (16, [0, 22, 45, 67, 90, 112, 135, 157]),
        (17, [0, 10, 21, 31, 42, 52, 63, 74, 84, 95, 105, 116, 127, 137, 148, 158, 169]),
        (18, [0, 20, 40, 60, 80, 100, 120, 140, 160]),
        (19, [0, 9, 18, 28, 37, 47, 56, 66, 75, 85, 94, 104, 113, 123, 132, 142, 151, 161, 170]),
        (20, [0, 18, 36, 54, 72, 90, 108, 126, 144, 162]),
    ]
)
def test_compute_valid_angles(A, expected):
    actual = compute_valid_angles(A)
    assert expected == actual


@pytest.mark.parametrize(
    "previous_energy,Δ,expected",
    [
        (100, 0, 100),
        (100, 45, 50),
        (100, 90, 0),
        (50, 0, 50),
        (50, 45, 25),
        (50, 90, 0),
        (25, 0, 25),
        (25, 45, 13),
        (25, 90, 0),
        (13, 0, 13),
        (13, 45, 7),
        (13, 90, 0),
        (0, 0, 0),
        (0, 45, 0),
        (0, 90, 0),
    ]
)
def test_compute_energy(previous_energy, Δ, expected):
    actual = compute_energy(previous_energy, Δ)
    assert expected == actual


@pytest.mark.parametrize(
    "A,P,expected",
    [
        (4, 1, []),
        (4, 2, [
            (100, 90, 0),
            (100, 0, 100),
        ]),
        (4, 3, [
            (100, 90, 0),
            (100, 0, 100),
            (0, 90, 0),
            (0, 0, 0),
        ]),
        (4, 4, [
            (100, 90, 0),
            (100, 0, 100),
            (0, 90, 0),
            (0, 0, 0),
        ]),
        (8, 4, [
            (100, 135, 50),
            (100, 90, 0),
            (100, 45, 50),
            (100, 0, 100),

            (50, 135, 25),
            (50, 90, 0),
            (50, 45, 25),
            (50, 0, 50),

            (25, 135, 13),
            (25, 90, 0),
            (25, 45, 13),
            (25, 0, 25),

            (0, 135, 0),
            (0, 90, 0),
            (0, 45, 0),
            (0, 0, 0),
        ]),
    ]
)
def test_compute_transitions(A, P, expected):
    actual = compute_transitions(A, P)
    assert expected == actual


@pytest.fixture(scope='module')
def global_data():
    return {'wall_time_success': [], 'wall_time_failure': [], 'wall_time_unknown': []}


@pytest.mark.parametrize(
    "problem",
    [
        Problem(
            2,  # pizzas
            4,  # slices (per pizza)
            1,  # windows (per slice)
            4,  # possible filter angles
            [
                # image 0
                [
                    [0], [0],
                    [0], [0],
                ],
                # image 1
                [
                    [100], [100],
                    [100], [100],
                ]
            ],
        ),
        Problem(
            3,  # pizzas
            4,  # slices (per pizza)
            1,  # windows (per slice)
            4,  # possible filter angles
            [
                # image 0
                [
                    [100], [0],
                    [0], [0],
                ],
                # image 1
                [
                    [100], [100],
                    [100], [100],
                ],
                # image 2
                [
                    [100], [0],
                    [0], [100],
                ],
            ],
        ),
    ]
)
def test_solve(global_data, problem):
    solution = solve(problem)

    if solution.success is False:
        global_data['wall_time_failure'].append(solution.wall_time)
        print(f" *********************** FAILURE {problem}")
        return
    if solution.success is None:
        global_data['wall_time_unknown'].append(solution.wall_time)
        print(f" *********************** UNKNOWN {problem}")
        return
    global_data['wall_time_success'].append(solution.wall_time)
    print(f"*********************** RESOLVED {problem}")

    p = problem.p
    S = problem.S
    W = problem.W
    P = problem.P
    n = solution.n
    α = solution.α

    # internal consistency checks
    j_corrected = solution.j_corrected
    for m in range(len(p)):
        for i in range(P):
            for j in range(S):
                assert j_corrected[j][m][i] == (j - n[m][i]) % S

    α_corrected = solution.α_corrected
    for m in range(len(p)):
        for i in range(P):
            for j in range(S):
                for k in range(W):
                    assert α_corrected[m][i][j][k] == (α[i][j_corrected[j][m][i]][k] + math.floor(360.0 / S) * n[m][i]) % 180

    # consistency of actual results
    for m in range(len(p)):
        for j in range(S):
            for k in range(W):
                energy = 100
                for i in range(1, P):
                    n_under = n[m][i - 1]
                    α_under = α[i - 1][(j - n_under) % S][k]
                    n_over = n[m][i]
                    α_over = α[i][(j - n_over) % S][k]
                    energy = round(compute_energy(energy, α_over + 360.0 / S * (n_over) - (α_under + 360.0 / S * n_under)))
                print(f"p[{m}][{j}][{k}] EXPECTED: {p[m][j][k]} ACTUAL: {energy}")
                assert abs(p[m][j][k] - energy) < 2


def test_solve_randomized(global_data):
    random.seed(0)
    for W in range(1, 6):
        for P in range(2, 4):
            for S in [3, 4, 6, 8]:
                for A in [2, 3, 4]:
                    if S % A != 0:
                        continue
                    for M in range(2, 6):

                        transitions = compute_transitions(A, P)

                        p = [[[random.choice(transitions)[2] for k in range(W)] for j in range(S)] for _ in range(M)]
                        problem = Problem(
                            P,  # pizzas
                            S,  # slices (per pizza)
                            W,  # windows (per slice)
                            A,  # possible filter angles
                            p,
                        )

                        test_solve(global_data, problem)


def test_report_results(global_data):
    wts = global_data['wall_time_success']
    wtf = global_data['wall_time_failure']
    wtu = global_data['wall_time_unknown']
    print("\n\n")
    print(f"******************* TOTAL SUCCEEDED {len(wts)}\n")
    print("hist")
    print(auto_bin_histogram(wts))
    print(f"******************* TOTAL FAILED {len(wtf)}\n")
    print("hist")
    print(auto_bin_histogram(wtf))
    print(f"******************* TOTAL UNKNOWN {len(wtu)}\n")
    print("hist")
    print(auto_bin_histogram(wtu))


def auto_bin_histogram(data, num_bins=10):
    if not data:
        return {}
    min_val = min(data)
    max_val = max(data)
    bin_width = (max_val - min_val) / num_bins
    bins = [min_val + i * bin_width for i in range(num_bins)]
    bins.append(max_val)  # Include the upper bound in the last bin
    histogram = {bin: 0 for bin in bins}
    for value in data:
        bin_index = int((value - min_val) / bin_width)
        if bin_index == num_bins:
            bin_index -= 1  # Handle the case where the value is equal to the max_val
        histogram[bins[bin_index]] += 1
    return histogram
