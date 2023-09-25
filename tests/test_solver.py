from solver.solver import solve


def test_solve():
    result = solve()
    assert result["x"] == 7
    assert result["y"] == 3
    assert result["z"] == 5
