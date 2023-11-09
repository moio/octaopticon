#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calculates OctaOpticon construction parameters."""

from solver.solver import Problem, solve


problem = Problem(
    4,  # pizzas
    8,  # slices (per pizza)
    2,  # windows (per slice)
    8,  # possible filter angles
    [
        # image 0 (Y)
        [
            [0, 0], [50, 50], [0, 0], [0, 0], [50, 50], [0, 0], [0, 0], [50, 50],
        ],
        # image 1 (q)
        [
            [50, 0], [50, 0], [50, 0], [50, 50], [50, 0], [50, 0], [50, 0], [50, 0],
        ],
        # image 2 (X)
        [
            [0, 0], [50, 50], [0, 0], [50, 50], [0, 0], [50, 50], [0, 0], [50, 50],
        ],
        # image 3 (o)
        [
            [50, 0], [50, 0], [50, 0], [50, 0], [50, 0], [50, 0], [50, 0], [50, 0],
        ],
        # image 4 (I)
        [
            [50, 50], [0, 0], [0, 0], [0, 0], [50, 50], [0, 0], [0, 0], [0, 0],
        ],
        # image 5 (c)
        [
            [50, 0], [50, 0], [0, 0], [50, 0], [50, 0], [50, 0], [50, 0], [50, 0],
        ],
        # image 6 (K)
        [
            [50, 50], [50, 50], [0, 0], [50, 50], [50, 50], [0, 0], [0, 0], [0, 0],
        ],
    ],
)

if __name__ == "__main__":
    solution = solve(problem)
    if solution.success:
        print("\n\n**DEBUG INFORMATION**\n")
        for m in range(len(problem.p)):
            print(f"offsets to reconstruct image {m}: {solution.n[m]}")
            for i in range(problem.P):
                print(f"    pizza {i}, rotation {solution.n[m][i]}")
                for j in range(problem.S):
                    print(f"        {j} -> {solution.j_corrected[j][m][i]}")
                print("    corrected angles:")
                for j in range(problem.S):
                    for k in range(problem.W):
                        print(f"            {solution.α[i][j][k]} -> {solution.α_corrected[m][i][j][k]}")

        print("\n\n**SOLUTION**\n")
        for i in reversed(range(problem.P)):
            print(f"α for pizza {i}:")
            for j in range(problem.S):
                print(f"    slice {j}: {solution.α[i][j]}")
        for m in range(len(problem.p)):
            print(f"offsets to reconstruct image {m}: {solution.n[m]}")

    else:
        print("no result")
