#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Outputs an SVG for an octaopticon"""

import math
import os
import webbrowser


def generate_octagon_star_points(max_size_mm, x_offset, y_offset):
    radius_outer_mm = max_size_mm / 2
    radius_inner_mm = radius_outer_mm * math.sqrt(2 - math.sqrt(2))

    polygon_points = []

    for i in range(8):
        angle_outer = 2 * math.pi * i / 8
        x_outer = x_offset + radius_outer_mm * math.cos(angle_outer)
        y_outer = y_offset + radius_outer_mm * math.sin(angle_outer)
        polygon_points.append(f"{x_outer},{y_outer}")

        angle_inner = angle_outer + math.pi / 8
        x_inner = x_offset + radius_inner_mm * math.cos(angle_inner)
        y_inner = y_offset + radius_inner_mm * math.sin(angle_inner)
        polygon_points.append(f"{x_inner},{y_inner}")

    return " ".join(polygon_points)


def generate_square_points(max_size_mm, x_offset, y_offset, angle_offset):
    radius = max_size_mm / 2

    polygon_points = []

    for i in range(4):
        angle_outer = 2 * math.pi * i / 4 + angle_offset
        x_outer = x_offset + radius * math.cos(angle_outer)
        y_outer = y_offset + radius * math.sin(angle_outer)
        polygon_points.append(f"{x_outer},{y_outer}")

    return " ".join(polygon_points)


def generate_circle_centers(n, max_size_mm, x_offset, y_offset):
    radius_outer_mm = max_size_mm / 2

    centers = []

    for i in range(n):
        angle_outer = 2 * math.pi * i / n
        x_outer = x_offset + radius_outer_mm * math.cos(angle_outer)
        y_outer = y_offset + radius_outer_mm * math.sin(angle_outer)
        centers.append([x_outer, y_outer])

    return centers


def generate_elements(max_size_mm, circle_radius_mm, radii, x_offset, y_offset):
    polygon_points_str = generate_octagon_star_points(max_size_mm, x_offset, y_offset)

    result = [f"""<polygon points="{polygon_points_str}" fill="none" stroke="black" stroke-width="1" stroke-linejoin="round" />"""]

    for radius in radii:
        for coords in generate_circle_centers(radius[0], max_size_mm * radius[1], x_offset, y_offset):
            result.append(f'<polygon points="{generate_square_points(circle_radius_mm * 2 * 1.5 * math.sqrt(2), coords[0], coords[1], 0)}" fill="none" stroke="black" stroke-width="0.2" />')
            result.append(f'<polygon points="{generate_square_points(circle_radius_mm * 2 * 1.5 * math.sqrt(2), coords[0], coords[1], math.pi / 4)}" fill="none" stroke="black" stroke-width="0.2" />')
            result.append(f'<circle cx="{coords[0]}" cy="{coords[1]}" r="{circle_radius_mm}" fill="none" stroke="black" stroke-width="1.5" />')

    return result


def generate_svg(document_size_x_mm, document_size_y_mm, elements):
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{document_size_x_mm}mm" height="{document_size_y_mm}mm" viewBox="0 0 {document_size_x_mm} {document_size_y_mm}">
        {' '.join(elements)}
    </svg>"""

    return svg_content


if __name__ == "__main__":
    # small
    elements = []
    elements.extend(generate_elements(95, 5, [[1, 0], [8, 13 / 32], [8, 23 / 32]], 210 / 4, 297 / 4))
    elements.extend(generate_elements(95, 5, [[1, 0], [8, 13 / 32], [8, 23 / 32]], 210 / 4 * 3, 297 / 4))
    elements.extend(generate_elements(95, 5, [[1, 0], [8, 13 / 32], [8, 23 / 32]], 210 / 4, 297 / 4 * 3))
    elements.extend(generate_elements(95, 5, [[1, 0], [8, 13 / 32], [8, 23 / 32]], 210 / 4 * 3, 297 / 4 * 3))
    svg_content = generate_svg(210, 297, elements)
    with open("small.svg", 'w') as svg_file:
        svg_file.write(svg_content)
    webbrowser.open("file://" + os.path.abspath("small.svg"), new=2)  # "new=2" opens the file in a new tab if possible

    # big
    svg_content = generate_svg(210, 297, generate_elements(200, 5, [[1, 0], [8, 7 / 32], [8, 12 / 32], [16, 17 / 32], [16, 22 / 32], [8, 27 / 32],], 210 / 2, 297 / 2))
    with open("big.svg", 'w') as svg_file:
        svg_file.write(svg_content)
    webbrowser.open("file://" + os.path.abspath("big.svg"), new=2)  # "new=2" opens the file in a new tab if possible
