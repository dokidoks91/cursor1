import pandas as pd

from instagram_auto_post import assign_preferred_first_products


def test_assign_preferred_first_products_reports_statuses():
    calendar = [
        {"day_name": "Pazartesi", "time": "09:00"},
        {"day_name": "Salı", "time": "10:30"},
    ]
    first_candidates = pd.DataFrame(
        [
            {
                "kisakodrenk": "AAA",
                "KisaKod": "5Y500",
                "Renk": "SİYAH",
                "UrunCinsi": "Elbise",
                "total_stock": 10,
            },
            {
                "kisakodrenk": "BBB",
                "KisaKod": "4K400",
                "Renk": "MAVİ",
                "UrunCinsi": "Elbise",
                "total_stock": 8,
            },
        ]
    )
    cfg = {
        "preferred_first_products": [
            {"kisakodrenk": "AAA", "gun": "Pazartesi", "time": "09:00"},
            {"kisakodrenk": "BBB", "gun": "Çarşamba", "time": "09:00"},
            {"kisakodrenk": "CCC", "gun": "Salı", "time": "10:30"},
        ]
    }

    posts, used, report = assign_preferred_first_products(calendar, first_candidates, cfg, set())

    assert len(posts) == 1
    assert used == {"AAA"}

    statuses = {entry["kisakodrenk"]: entry["status"] for entry in report}
    assert statuses["AAA"] == "assigned"
    assert statuses["BBB"] == "day_not_in_plan"
    assert statuses["CCC"] == "not_in_first_pool"






