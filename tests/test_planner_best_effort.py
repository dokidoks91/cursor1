import pandas as pd

import planner


def test_best_effort_flow_when_user_continues(monkeypatch):
    dummy_products = pd.DataFrame(
        [
            {
                "kisakodrenk": "AAA",
                "KisaKod": "5Y500",
                "Renk": "SİYAH",
                "UrunCinsi": "Elbise",
                "total_stock": 20,
                "season_digit": 5,
                "season_seq": 500,
            }
        ]
    )
    dummy_calendar = [{"day_name": "Pazartesi", "time": "09:00", "day_idx": 0, "is_weekend": False}]

    def fake_load_stock_data(cfg):
        return pd.DataFrame({"dummy": [1]})

    def fake_build_unique_products(df):
        return dummy_products

    def fake_build_post_calendar(cfg):
        return dummy_calendar

    def fake_filter_first_products(unique, cfg):
        return dummy_products

    def fake_filter_back_products(unique, cfg):
        return pd.DataFrame(
            [
                {
                    "kisakodrenk": f"BACK{i}",
                    "KisaKod": f"B{i}",
                    "Renk": "MAVİ",
                    "UrunCinsi": "Elbise",
                    "total_stock": 5,
                }
                for i in range(9)
            ]
        )

    def fake_assign_first_products(calendar, first_candidates, cfg, decide=None):
        cfg["_preferred_assignment_report"] = [
            {"index": 1, "kisakodrenk": "AAA", "status": "assigned", "detail": "Pazartesi 09:00"}
        ]
        post = {
            "day_name": "Pazartesi",
            "time": "09:00",
            "first_product": first_candidates.iloc[0].to_dict(),
            "back_products": [],
        }
        return [post]

    def fake_assign_back_products(posts, back_candidates, cfg):
        for post in posts:
            post["back_products"] = back_candidates.head(9).to_dict("records")
        return posts

    def fake_check_advanced_first_constraints(posts, cfg, decide=None):
        return True

    class DummyAnalyzer:
        def __init__(self, calendar, unique_products, cfg, raw_df):
            self.cfg = cfg

        def analyze_and_suggest_relaxations(self, posts=None):
            return {
                "suggestions": [
                    {
                        "rule_type": "FIRST_stock",
                        "rule_name": "FIRST Minimum Toplam Stok",
                        "original_value": 10,
                        "suggested_value": 5,
                        "estimated_new_candidates": 5,
                        "preselected": True,
                    }
                ],
                "soft_violations": [],
                "hard_violations": [],
                "diagnostics": {
                    "first_pool_size": 1,
                    "required_first": 1,
                    "back_pool_size": 9,
                    "required_back": 9,
                },
                "message": "dummy",
            }

        def apply_relaxations(self, suggestions):
            new_cfg = self.cfg.copy()
            new_cfg["min_total_stock_front"] = suggestions[0]["suggested_value"]
            return new_cfg

    run_calls = {"count": 0}

    def fake_run_planner(**kwargs):
        run_calls["count"] += 1
        if run_calls["count"] == 1:
            return {"success": False, "summary_text": "fail", "error": "fail"}
        return {
            "success": True,
            "summary_text": "ok",
            "output_excel": "out.xlsx",
            "output_md": "out.md",
        }

    def fake_choice(suggestions, message, missing_first, missing_back, preferred_report):
        assert missing_first == 0
        assert preferred_report
        return "continue_best", suggestions

    monkeypatch.setattr(planner, "load_stock_data", fake_load_stock_data)
    monkeypatch.setattr(planner, "build_unique_products", fake_build_unique_products)
    monkeypatch.setattr(planner, "build_post_calendar", fake_build_post_calendar)
    monkeypatch.setattr(planner, "filter_first_products", fake_filter_first_products)
    monkeypatch.setattr(planner, "filter_back_products", fake_filter_back_products)
    monkeypatch.setattr(planner, "assign_first_products", fake_assign_first_products)
    monkeypatch.setattr(planner, "assign_back_products", fake_assign_back_products)
    monkeypatch.setattr(planner, "check_advanced_first_constraints", fake_check_advanced_first_constraints)
    monkeypatch.setattr(planner, "BestEffortAnalyzer", DummyAnalyzer)
    monkeypatch.setattr(planner, "run_planner", fake_run_planner)

    dummy_config = {
        "stock_excel_path": "dummy.xlsx",
        "plan_start_day_name": "Pazartesi",
        "plan_num_days": 1,
        "use_yazlik_front": True,
        "use_kislik_front": True,
        "allowed_cekim_front": ["EVET"],
        "one_atilma_reference_date": None,
        "one_atilma_min_days": None,
        "min_total_stock_front": 10,
        "front_size_stock_rules": [],
        "min_nos_front": 0,
        "min_dvm_front": 0,
        "use_yazlik_back": True,
        "use_kislik_back": True,
        "allowed_cekim_back": ["EVET"],
        "min_total_stock_back": 5,
        "back_size_stock_rules": [],
        "priority_mode_front": "stock_then_newest",
        "priority_mode_back": "stock_then_newest",
        "same_kisakod_min_gap_days": 0,
        "max_black_first_per_day": 0,
        "max_first_uses_per_kisakod": 0,
        "global_min_first_stock_sum": 0,
        "global_min_total_stock_sum": 0,
        "prioritize_by_newness": False,
        "prioritize_by_stock": False,
        "preferred_first_products": [{"kisakodrenk": "AAA", "gun": "Pazartesi", "time": "09:00"}],
        "weekday_times": ["09:00"],
        "weekend_times": ["11:00"],
    }

    result = planner.run_planner_with_best_effort(
        excel_path="dummy.xlsx",
        start_day="Pazartesi",
        num_days=1,
        on_progress=lambda msg: None,
        on_relaxation_choice=fake_choice,
        config_override=dummy_config,
    )

    assert result["success"]
    assert result["preferred_first_report"][0]["kisakodrenk"] == "AAA"
    assert run_calls["count"] == 2

