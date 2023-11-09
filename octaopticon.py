#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calculates OctaOpticon construction parameters."""

from solver.solver import Problem, solve


problem = Problem(
    3,  # pizzas
    8,  # slices (per pizza)
    7,  # windows (per slice)
    8,  # possible filter angles
    [
        # image 0 (H)
        [
            #  0    1    2    3    4    5    6
            [ 0,  0,  0,  0,  0,  0,  0], # 0
            [ 0,  0,  0,  0,  0,  0, 50], # 1
            [50, 50,  0, 50, 50, 50,  0], # 2
            [ 0,  0,  0,  0, 50,  0, 50], # 3
            [ 0,  0,  0,  0,  0,  0,  0], # 4
            [ 0,  0,  0,  0,  0,  0, 50], # 5
            [50, 50,  0, 50, 50, 50,  0], # 6
            [ 0,  0,  0,  0, 50,  0, 50], # 7
        ],
        # image 1 (W)
        [
            #  0    1    2    3    4    5    6
            [50,  0,  0,  0,  0,  0,  0], # 0
            [ 0,  0,  0,  0,  0,  0, 50], # 1
            [ 0,  0,  0, 50, 50,  0,  0], # 2
            [50,  0, 50, 50,  0,  0,  0], # 3
            [ 0,  0, 50,  0, 50,  0,  0], # 4
            [50,  0, 50, 50, 50,  0,  0], # 5
            [ 0,  0, 50, 50,  0,  0,  0], # 6
            [ 0,  0,  0,  0, 50,  0, 50], # 7
        ],
        # image 2 (2)
        [
            #  0    1    2    3    4    5    6
            [ 0,  0, 50, 50,  0,  0,  0], # 0
            [50, 50, 50, 50,  0,  0,  0], # 1
            [ 0,  0,  0,  0,  0,  0,  0], # 2
            [ 0,  0,  0,  0,  0,  0,  0], # 3
            [ 0,  0,  0,  0, 50, 50,  0], # 4
            [50, 50,  0, 50, 50, 50, 50], # 5
            [ 0,  0,  0,  0,  0,  0,  0], # 6
            [ 0,  0, 50, 50,  0,  0,  0], # 7
        ],
        # image 3 (3)
        [
            #  0    1    2    3    4    5    6
            [ 0,  0,  0,  0, 50, 50,  0], # 0
            [ 0,  0,  0,  0, 50, 50,  0], # 1
            [50, 50, 50,  0,  0,  0,  0], # 2
            [ 0,  0, 50,  0,  0, 50,  0], # 3
            [ 0,  0,  0,  0, 50, 50,  0], # 4
            [ 0,  0,  0,  0, 50, 50,  0], # 5
            [ 0,  0,  0,  0,  0,  0,  0], # 6
            [ 0,  0,  0,  0,  0, 50,  0], # 7
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
