#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Calculates OctaOpticon construction parameters."""

from solver.solver import solve

if __name__ == "__main__":
    results = solve()
    if results:
        print(f"x: {results['x']}")
        print(f"y: {results['y']}")
        print(f"z: {results['z']}")
    else:
        print("no result")
