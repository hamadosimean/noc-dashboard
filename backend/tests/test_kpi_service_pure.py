from app.services.kpi_service import month_label, prev_month, shift_months


def test_prev_month_regular():
    assert prev_month(4, 2026) == (3, 2026)


def test_prev_month_january_wraps_year():
    assert prev_month(1, 2026) == (12, 2025)


def test_shift_months_within_year():
    assert shift_months(7, 2026, 3) == (4, 2026)


def test_shift_months_across_year():
    assert shift_months(2, 2026, 3) == (11, 2025)
    assert shift_months(1, 2026, 12) == (1, 2025)


def test_shift_months_zero_offset():
    assert shift_months(7, 2026, 0) == (7, 2026)


def test_month_label_french():
    assert month_label(4, 2026) == "Avril 2026"
    assert month_label(12, 2025) == "Décembre 2025"
