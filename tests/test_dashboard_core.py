"""Automated tests for GameScope core logic and analytics functions."""
from pathlib import Path
import unittest
import pandas as pd
import plotly.graph_objects as go

# We will import the pure functions from app
import app


class TestGameScopeDataPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_path = app.get_dataset_path()
        if cls.data_path and cls.data_path.exists():
            cls.df = app.load_data(str(cls.data_path))
        else:
            cls.df = None

    def test_dataset_found_and_loaded(self):
        """Ensure dataset exists and loads with required schema."""
        self.assertIsNotNone(self.data_path, "Dataset file must exist.")
        self.assertIsNotNone(self.df, "DataFrame must load successfully.")
        self.assertFalse(self.df.empty, "DataFrame must not be empty.")
        
        # Check required columns
        for col in app.REQUIRED_COLUMNS:
            self.assertIn(col, self.df.columns, f"Required column {col} missing.")

    def test_data_types_and_validity(self):
        """Ensure numeric sales columns are strictly non-negative and properly typed."""
        if self.df is None:
            self.skipTest("No dataset")
        for col in app.SALES_COLUMNS:
            self.assertTrue(pd.api.types.is_numeric_dtype(self.df[col]))
            self.assertTrue((self.df[col] >= 0).all(), f"Negative sales detected in {col}")

    def test_filter_processing_normal(self):
        """Test filtering with standard valid criteria."""
        if self.df is None:
            self.skipTest("No dataset")
        
        # Filter for year 2000-2010, Action genre, PS2 platform
        filtered = app.apply_filters(
            self.df,
            year_range=(2000, 2010),
            selected_genres=["Action"],
            selected_platforms=["PS2"]
        )
        self.assertFalse(filtered.empty)
        self.assertTrue((filtered["Genre"] == "Action").all())
        self.assertTrue((filtered["Platform"] == "PS2").all())
        valid_years = filtered["Year"].dropna()
        self.assertTrue(((valid_years >= 2000) & (valid_years <= 2010)).all())

    def test_filter_processing_empty(self):
        """Test filtering when no genres or platforms are selected."""
        if self.df is None:
            self.skipTest("No dataset")
        filtered_no_genre = app.apply_filters(
            self.df,
            year_range=(2000, 2010),
            selected_genres=[],
            selected_platforms=["PS2"]
        )
        self.assertTrue(filtered_no_genre.empty)

        filtered_no_platform = app.apply_filters(
            self.df,
            year_range=(2000, 2010),
            selected_genres=["Action"],
            selected_platforms=[]
        )
        self.assertTrue(filtered_no_platform.empty)

    def test_filter_search_query(self):
        """Ensure game name search query accurately filters records."""
        if self.df is None:
            self.skipTest("No dataset")
        
        # Search for Mario
        mario_filtered = app.apply_filters(
            self.df,
            year_range=(1980, 2020),
            selected_genres=app.GENRE_PALETTE.keys(),
            selected_platforms=self.df["Platform"].unique().tolist(),
            search_query="Mario"
        )
        self.assertFalse(mario_filtered.empty)
        for _, row in mario_filtered.head(10).iterrows():
            name_match = "mario" in str(row["Name"]).lower()
            pub_match = "mario" in str(row["Publisher"]).lower()
            self.assertTrue(name_match or pub_match)

    def test_kpi_calculations_accuracy(self):
        """Test KPI calculation math and top game title identification."""
        if self.df is None:
            self.skipTest("No dataset")
        kpis = app.calculate_kpis(self.df)
        self.assertIn("total_sales", kpis)
        self.assertIn("game_records", kpis)
        self.assertIn("top_genre", kpis)
        self.assertIn("top_genre_sales", kpis)
        self.assertIn("avg_sales", kpis)
        self.assertIn("top_game_name", kpis)
        self.assertIn("top_game_sales", kpis)

        expected_records = len(self.df)
        expected_sales = self.df["Global_Sales"].sum()
        expected_avg = self.df["Global_Sales"].mean()

        self.assertEqual(kpis["game_records"], expected_records)
        self.assertAlmostEqual(kpis["total_sales"], expected_sales, places=2)
        self.assertAlmostEqual(kpis["avg_sales"], expected_avg, places=2)
        self.assertEqual(kpis["top_genre"], "Action")
        self.assertEqual(kpis["top_game_name"], "Wii Sports")
        self.assertAlmostEqual(kpis["top_game_sales"], 82.74, places=2)

    def test_dynamic_insights_generation(self):
        """Test analytical insight calculations."""
        if self.df is None:
            self.skipTest("No dataset")
        insights = app.generate_dynamic_insights(self.df)
        self.assertGreaterEqual(len(insights), 4, "Must generate at least 4 insights.")
        
        # Verify structure
        for ins in insights:
            self.assertIn("title", ins)
            self.assertIn("value", ins)
            self.assertIn("description", ins)
            self.assertIn("badge", ins)

        # Specifically check game, platform, dominant region, peak year
        badges = [i["badge"] for i in insights]
        self.assertTrue(any("Game" in b for b in badges))
        self.assertTrue(any("Platform" in b for b in badges))
        self.assertTrue(any("Wilayah" in b or "Region" in b for b in badges))
        self.assertTrue(any("Tahun" in b or "Peak" in b for b in badges))

    def test_top10_games_chart(self):
        """Ensure Top 10 Best-Selling Video Games bar chart renders properly."""
        if self.df is None:
            self.skipTest("No dataset")
        fig = app.create_top10_games_chart(self.df)
        self.assertIsInstance(fig, (go.Figure, object))
        self.assertTrue(len(fig.data) > 0, "Top 10 chart must contain a trace.")
        # Must contain 10 bars
        self.assertEqual(len(fig.data[0].x), 10)

    def test_game_comparison_chart(self):
        """Ensure Compare Game Sales chart renders regional stacked traces."""
        if self.df is None:
            self.skipTest("No dataset")
        selected = ["Wii Sports (Wii)", "Super Mario Bros. (NES)"]
        fig = app.create_game_comparison_chart(self.df, selected)
        self.assertIsInstance(fig, (go.Figure, object))
        # 4 regional traces (NA, EU, JP, Other)
        self.assertEqual(len(fig.data), 4)

    def test_chart_generation(self):
        """Ensure all standard charts generate valid Plotly figures."""
        if self.df is None:
            self.skipTest("No dataset")

        fig1 = app.create_sales_trend_chart(self.df)
        self.assertIsInstance(fig1, (go.Figure, object))
        self.assertTrue(len(fig1.data) > 0, "Line chart must have at least one trace.")

        fig2 = app.create_genre_bar_chart(self.df)
        self.assertIsInstance(fig2, (go.Figure, object))
        self.assertTrue(len(fig2.data) > 0, "Bar chart must have at least one trace.")

        fig3 = app.create_regional_heatmap(self.df)
        self.assertIsInstance(fig3, (go.Figure, object))
        self.assertTrue(len(fig3.data) > 0, "Heatmap must have at least one trace.")

        fig4 = app.create_na_vs_eu_scatter(self.df)
        self.assertIsInstance(fig4, (go.Figure, object))
        self.assertTrue(len(fig4.data) > 0, "Scatter plot must have traces.")

    def test_edge_case_single_row(self):
        """Ensure single record behaves cleanly without errors in charts, KPIs, insights."""
        if self.df is None:
            self.skipTest("No dataset")
        single_df = self.df.iloc[:1].copy()
        
        kpis = app.calculate_kpis(single_df)
        self.assertEqual(kpis["game_records"], 1)
        self.assertEqual(kpis["top_game_name"], single_df["Name"].iloc[0])
        
        insights = app.generate_dynamic_insights(single_df)
        self.assertEqual(len(insights), 4)

        fig_top10 = app.create_top10_games_chart(single_df)
        fig_comp = app.create_game_comparison_chart(single_df, [single_df["Game_Identifier"].iloc[0]])
        fig1 = app.create_sales_trend_chart(single_df)
        fig2 = app.create_genre_bar_chart(single_df)
        fig3 = app.create_regional_heatmap(single_df)
        fig4 = app.create_na_vs_eu_scatter(single_df)
        self.assertIsNotNone(fig_top10)
        self.assertIsNotNone(fig_comp)
        self.assertIsNotNone(fig1)
        self.assertIsNotNone(fig2)
        self.assertIsNotNone(fig3)
        self.assertIsNotNone(fig4)

    def test_edge_case_no_valid_year(self):
        """Ensure dataframe with only missing years handles trend and insight gracefully."""
        if self.df is None:
            self.skipTest("No dataset")
        no_year_df = self.df.copy()
        no_year_df["Year"] = pd.NA
        
        fig1 = app.create_sales_trend_chart(no_year_df)
        self.assertIsNotNone(fig1)
        
        insights = app.generate_dynamic_insights(no_year_df)
        peak_insight = next(i for i in insights if "Tahun" in i["badge"] or "Peak" in i["badge"])
        self.assertEqual(peak_insight["title"], "N/A")

    def test_all_genres_in_palette(self):
        """Ensure every genre in dataset has a defined harmonious color in palette."""
        if self.df is None:
            self.skipTest("No dataset")
        unique_genres = self.df["Genre"].dropna().unique()
        for g in unique_genres:
            self.assertIn(g, app.GENRE_PALETTE, f"Genre {g} should have a curated color in GENRE_PALETTE.")


if __name__ == "__main__":
    unittest.main()
