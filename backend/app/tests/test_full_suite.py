import os
import io
import unittest
import json
import pandas as pd
from app.services.session_service import session_manager
from app.services.dataset_service import dataset_service
from app.services.dashboard_service import dashboard_service
from app.services.export_service import export_service
from app.services.language_service import language_service
from app.services.intent_service import intent_service
from app.services.validation_service import validation_service
from app.services.context_service import context_service
from app.services.ambiguity_service import ambiguity_service
from app.services.speech_service import speech_service

class ComprehensiveDashboardTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.csv_path = "sample_datasets/superstore_sales.csv"
        cls.xlsx_path = "sample_datasets/retail_sales_multisheet.xlsx"
        
        with open(cls.csv_path, "rb") as f:
            cls.csv_bytes = f.read()

        with open(cls.xlsx_path, "rb") as f:
            cls.xlsx_bytes = f.read()

    def setUp(self):
        # Fresh session for each test
        self.session = session_manager.create_session("Test Analytics Session")

    def tearDown(self):
        session_manager.clear_session(self.session.session_id)

    # 1. Upload CSV
    def test_01_upload_csv(self):
        meta = dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        self.assertEqual(meta.total_rows, 500)
        self.assertGreaterEqual(meta.total_columns, 10)
        self.assertIn("Sales", [c.name for c in meta.columns])
        self.assertIn("Region", [c.name for c in meta.columns])
        self.assertEqual(len(meta.preview_rows), 15)

    # 2. Upload Excel
    def test_02_upload_excel(self):
        meta = dataset_service.process_file_bytes(self.xlsx_bytes, "retail_sales_multisheet.xlsx", self.session)
        self.assertEqual(meta.file_type, "xlsx")
        self.assertGreaterEqual(len(meta.sheet_names), 3)
        self.assertIn("Sales_2023", meta.sheet_names)
        self.assertIn("Category_Summary", meta.sheet_names)

    # 3. Select Excel Worksheet
    def test_03_switch_worksheet(self):
        dataset_service.process_file_bytes(self.xlsx_bytes, "retail_sales_multisheet.xlsx", self.session)
        self.assertEqual(self.session.active_sheet, "Sales_2023")
        
        # Switch to Category_Summary sheet
        new_meta = dataset_service.switch_sheet(self.session, "Category_Summary")
        self.assertEqual(self.session.active_sheet, "Category_Summary")
        self.assertIn("Category", [c.name for c in new_meta.columns])

    # 4. Create Bar Chart using Text
    def test_04_create_bar_chart(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        res = dashboard_service.process_command(self.session, "Create a bar chart of sales by region")
        self.assertTrue(res.success)
        self.assertEqual(len(self.session.charts), 1)
        chart = self.session.charts[0]
        self.assertEqual(chart.chart_type, "bar")
        self.assertEqual(chart.x_col, "Region")
        self.assertEqual(chart.y_col, "Sales")
        self.assertIn("data", chart.plotly_spec)

    # 5. Create Chart using Voice / Transcribe
    def test_05_speech_service_status(self):
        status = speech_service.get_status()
        self.assertIn("engine", status)
        self.assertIn("available", status)

    # 6. Create Multiple Charts without removing previous charts
    def test_06_create_multiple_charts(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        # Chart 1
        res1 = dashboard_service.process_command(self.session, "Create a bar chart of monthly sales")
        self.assertTrue(res1.success)
        self.assertEqual(len(self.session.charts), 1)

        # Chart 2
        res2 = dashboard_service.process_command(self.session, "Create a line chart of monthly profit")
        self.assertTrue(res2.success)
        self.assertEqual(len(self.session.charts), 2)
        
        # Both charts must exist with unique IDs
        self.assertNotEqual(self.session.charts[0].id, self.session.charts[1].id)
        self.assertEqual(self.session.charts[0].y_col, "Sales")
        self.assertEqual(self.session.charts[1].y_col, "Profit")

    # 7. Generate KPI Cards
    def test_07_generate_kpi_cards(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        res1 = dashboard_service.process_command(self.session, "Show total revenue")
        self.assertTrue(res1.success)
        self.assertEqual(len(self.session.kpis), 1)
        self.assertGreater(self.session.kpis[0].value, 0)

        res2 = dashboard_service.process_command(self.session, "Calculate average profit")
        self.assertTrue(res2.success)
        self.assertEqual(len(self.session.kpis), 2)
        self.assertEqual(self.session.kpis[1].agg, "avg")

    # 8 & 9. Modify Existing Chart and Identify using Conversation Context ("it")
    def test_08_09_context_resolution_and_modification(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        # Create Sales Bar Chart
        dashboard_service.process_command(self.session, "Create a bar chart of sales by region")
        # Create Profit Line Chart
        dashboard_service.process_command(self.session, "Create a line chart of monthly profit")
        self.assertEqual(len(self.session.charts), 2)
        
        # "Change it to a pie chart" should resolve "it" to the most recently created profit chart
        res3 = dashboard_service.process_command(self.session, "Change it to a pie chart")
        self.assertTrue(res3.success)
        self.assertEqual(len(self.session.charts), 2)  # Still 2 charts
        self.assertEqual(self.session.charts[1].chart_type, "pie")
        self.assertEqual(self.session.charts[0].chart_type, "bar")  # First chart untouched

    # 10 & 11. Ambiguity Detection & Clarification Questions
    def test_10_11_ambiguity_detection_and_clarification(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        dashboard_service.process_command(self.session, "Create a bar chart of sales by region")
        
        # Ambiguous command: "Show the top five" (metric is missing!)
        res = dashboard_service.process_command(self.session, "Show the top five")
        self.assertTrue(res.requires_clarification)
        self.assertIsNotNone(res.clarification)
        self.assertEqual(res.clarification.parameter_needed, "metric_col")
        self.assertIn("Sales", res.clarification.options)

        # Answer the clarification with "Sales"
        resume_res = dashboard_service.process_command(self.session, "Sales")
        self.assertTrue(resume_res.success)
        self.assertFalse(resume_res.requires_clarification)
        self.assertEqual(len(self.session.charts), 2)

    # 12. English Command
    def test_12_english_commands(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        res = dashboard_service.process_command(self.session, "Compare sales by region")
        self.assertTrue(res.success)
        self.assertEqual(res.detected_language, "English")

    # 13. Hindi Commands
    def test_13_hindi_commands(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        # Devanagari Hindi
        res = dashboard_service.process_command(self.session, "Monthly sales ka bar chart banao")
        self.assertTrue(res.success)
        self.assertEqual(res.detected_language, "Hinglish")
        
        res2 = dashboard_service.process_command(self.session, "कुल बिक्री दिखाओ")
        self.assertTrue(res2.success)
        self.assertEqual(res2.detected_language, "Hindi")

    # 14. Marathi Commands
    def test_14_marathi_commands(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        res1 = dashboard_service.process_command(self.session, "Monthly sales cha bar chart tayar kara")
        self.assertTrue(res1.success)
        self.assertEqual(res1.detected_language, "Marathi-English")
        
        res2 = dashboard_service.process_command(self.session, "एकूण विक्री दाखवा")
        self.assertTrue(res2.success)
        self.assertEqual(res2.detected_language, "Marathi")

    # 15. Code-mixed Commands (Hinglish & Marathi-English)
    def test_15_code_mixed_commands(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        res = dashboard_service.process_command(self.session, "Top 5 products by profit dikhao")
        self.assertTrue(res.success)
        self.assertEqual(self.session.charts[-1].top_n, 5)

    # 16. Validate Incorrect Column Names
    def test_16_validate_incorrect_column(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        valid, err = validation_service.validate_chart_request(
            x_col="NonExistentCol", y_col="Sales", chart_type="bar", agg="sum",
            available_columns=self.session.dataset_meta.columns
        )
        self.assertFalse(valid)
        self.assertIn("does not exist", err)

        # Non-numeric aggregation check
        valid_agg, err_agg = validation_service.validate_chart_request(
            x_col="Region", y_col="Category", chart_type="bar", agg="sum",
            available_columns=self.session.dataset_meta.columns
        )
        self.assertFalse(valid_agg)
        self.assertIn("not a numeric column", err_agg)

    # 17 & 18. Dashboard Filters and KPI Updates
    def test_17_18_filtering_and_kpi_update(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        # Create KPI
        dashboard_service.create_kpi(self.session, "Sales", "sum")
        initial_val = self.session.kpis[0].value
        self.assertGreater(initial_val, 0)

        # Apply Filter on Region == "West"
        dashboard_service.apply_filter(self.session, "Region", "West")
        filtered_val = self.session.kpis[0].value
        
        # Filtered sales must be strictly less than total sales across all regions
        self.assertLess(filtered_val, initial_val)
        self.assertGreater(filtered_val, 0)

        # Reset Filter
        dashboard_service.clear_filter(self.session)
        reset_val = self.session.kpis[0].value
        self.assertEqual(reset_val, initial_val)

    # 19 & 20. ZIP Export and Restoration
    def test_19_20_zip_export_and_restore(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        dashboard_service.create_chart(self.session, "bar", "Region", "Sales", title="Sales by Region")
        dashboard_service.create_kpi(self.session, "Sales", "sum")

        # Export ZIP
        zip_bytes = export_service.generate_zip_export(self.session)
        self.assertGreater(len(zip_bytes), 1000)

        # Restore into a brand new clean session
        new_session = session_manager.create_session("Restored Session")
        success, msg = export_service.restore_from_zip(zip_bytes, new_session)
        self.assertTrue(success)
        self.assertEqual(len(new_session.charts), 1)
        self.assertEqual(len(new_session.kpis), 1)
        self.assertEqual(new_session.charts[0].title, "Sales by Region")
        session_manager.clear_session(new_session.session_id)

    # 21 & 22. Standalone HTML Export and Offline Filter Verifications
    def test_21_22_standalone_html_export(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        dashboard_service.create_chart(self.session, "bar", "Region", "Sales")
        dashboard_service.create_kpi(self.session, "Sales", "sum")

        html = export_service.generate_standalone_html(self.session)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("rawData", html)
        self.assertIn("chartConfigs", html)
        self.assertIn("kpiConfigs", html)
        self.assertIn("function getFilteredData()", html)
        self.assertIn("Plotly.react", html)

    # 23. PDF Export
    def test_23_pdf_export(self):
        dataset_service.process_file_bytes(self.csv_bytes, "superstore_sales.csv", self.session)
        dashboard_service.create_chart(self.session, "bar", "Region", "Sales")
        dashboard_service.create_kpi(self.session, "Sales", "sum")

        pdf_bytes = export_service.generate_pdf_report(self.session)
        self.assertGreater(len(pdf_bytes), 2000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    # 24. Clear Workspace Data
    def test_24_clear_workspace(self):
        sid = self.session.session_id
        self.assertIsNotNone(session_manager.get_session(sid))
        session_manager.clear_session(sid)
        self.assertIsNone(session_manager.get_session(sid))

    # 25. Complete Dataset Table & Acceptance Test (5,332 rows, 12 columns)
    def test_25_view_complete_dataset_table_acceptance(self):
        # Create dataset with exactly 5,332 rows and 12 columns
        n_rows = 5332
        data = {
            "Order_ID": [f"ORD-{i:06d}" for i in range(1, n_rows + 1)],
            "Order_Date": ["2023-01-01"] * n_rows,
            "Region": ["North", "South", "East", "West"] * (n_rows // 4) + ["North"] * (n_rows % 4),
            "State": ["Maharashtra" if i % 2 == 0 else "Karnataka" for i in range(n_rows)],
            "City": ["Mumbai" if i % 3 == 0 else "Bengaluru" for i in range(n_rows)],
            "Category": ["Electronics" if i % 2 == 0 else "Furniture" for i in range(n_rows)],
            "Sub_Category": ["Phones" if i % 4 == 0 else "Chairs" for i in range(n_rows)],
            "Product_Name": [f"Product Item {i}" for i in range(1, n_rows + 1)],
            "Sales": [float(i * 1.5) for i in range(1, n_rows + 1)],  # 1.5 to 7998.0
            "Quantity": [(i % 10) + 1 for i in range(n_rows)],
            "Discount": [0.05 if i % 5 == 0 else 0.1 for i in range(n_rows)],
            "Profit": [float(i * 0.25) for i in range(1, n_rows + 1)]
        }
        df_5332 = pd.DataFrame(data)
        self.assertEqual(len(df_5332), 5332)
        self.assertEqual(len(df_5332.columns), 12)

        csv_bytes = df_5332.to_csv(index=False).encode("utf-8")
        dataset_service.process_file_bytes(csv_bytes, "acceptance_5332.csv", self.session)

        # 1. Check Page 1 with page_size=100
        p1 = dataset_service.get_paginated_table(self.session, page=1, page_size=100)
        self.assertTrue(p1["success"])
        self.assertEqual(p1["total_rows"], 5332)
        self.assertEqual(p1["total_columns"], 12)
        self.assertEqual(p1["filtered_rows"], 5332)
        self.assertEqual(p1["total_pages"], 54)  # ceil(5332 / 100) = 54
        self.assertEqual(p1["current_page"], 1)
        self.assertEqual(p1["page_size"], 100)
        self.assertEqual(p1["start_row"], 1)
        self.assertEqual(p1["end_row"], 100)
        self.assertEqual(len(p1["rows"]), 100)
        self.assertEqual(p1["rows"][0]["Order_ID"], "ORD-000001")

        # 2. Check Final Page 54 (must be accessible and have remaining 32 rows)
        p54 = dataset_service.get_paginated_table(self.session, page=54, page_size=100)
        self.assertEqual(p54["current_page"], 54)
        self.assertEqual(p54["start_row"], 5301)
        self.assertEqual(p54["end_row"], 5332)
        self.assertEqual(len(p54["rows"]), 32)
        self.assertEqual(p54["rows"][-1]["Order_ID"], "ORD-005332")

        # 3. Check Page Sizes: 25, 50, 100, 250
        p_25 = dataset_service.get_paginated_table(self.session, page=1, page_size=25)
        self.assertEqual(len(p_25["rows"]), 25)
        self.assertEqual(p_25["total_pages"], (5332 + 24) // 25)

        p_250 = dataset_service.get_paginated_table(self.session, page=1, page_size=250)
        self.assertEqual(len(p_250["rows"]), 250)
        self.assertEqual(p_250["total_pages"], (5332 + 249) // 250)

        # 4. Search across the COMPLETE dataset (not just the current page)
        # Search for unique row "Product Item 4500"
        search_res = dataset_service.get_paginated_table(self.session, page=1, page_size=100, search="Item 4500")
        self.assertEqual(search_res["filtered_rows"], 1)
        self.assertEqual(search_res["rows"][0]["Order_ID"], "ORD-004500")

        # 5. Sorting across the COMPLETE dataset
        # Sort by Sales descending across all 5332 rows
        sort_res = dataset_service.get_paginated_table(self.session, page=1, page_size=100, sort_by="Sales", sort_order="desc")
        self.assertEqual(sort_res["rows"][0]["Order_ID"], "ORD-005332")
        self.assertEqual(sort_res["rows"][0]["Sales"], 5332 * 1.5)
        self.assertEqual(sort_res["rows"][1]["Order_ID"], "ORD-005331")

        # 6. Column Filter (e.g., Region = "West")
        filter_res = dataset_service.get_paginated_table(
            self.session, page=1, page_size=100, column_filters={"Region": "West"}
        )
        self.assertEqual(filter_res["filtered_rows"], 5332 // 4)
        for row in filter_res["rows"]:
            self.assertEqual(row["Region"], "West")

        # Original dataset remains unchanged
        self.assertEqual(len(self.session.df_working), 5332)


class TestRegionAndStateSlicers(unittest.TestCase):
    """
    Test suite for dynamic, dependent Region and State slicers.
    Dataset: exactly 237 rows and 11 columns including Region and State.
    Command: "Add the slicer of Region and State"
    """
    def setUp(self):
        self.session = session_manager.create_session("Slicer Acceptance Test Session")
        
        # Build 237 rows x 11 columns dataset
        # Region -> State mapping:
        # West -> Maharashtra, Gujarat, Goa, Rajasthan
        # South -> Karnataka, Tamil Nadu, Kerala
        # North -> Delhi, Punjab, Haryana
        # East -> West Bengal, Odisha, Bihar
        regions_states = [
            ("West", "Maharashtra"),
            ("West", "Gujarat"),
            ("West", "Goa"),
            ("West", "Rajasthan"),
            ("South", "Karnataka"),
            ("South", "Tamil Nadu"),
            ("South", "Kerala"),
            ("North", "Delhi"),
            ("North", "Punjab"),
            ("North", "Haryana"),
            ("East", "West Bengal"),
            ("East", "Odisha"),
            ("East", "Bihar"),
        ]

        data = []
        for i in range(237):
            reg, st = regions_states[i % len(regions_states)]
            data.append({
                "Order_ID": f"ORD-{i+1:04d}",
                "Order_Date": f"2023-{(i%12)+1:02d}-{(i%28)+1:02d}",
                "Region": reg,
                "State": st,
                "City": f"City_{i%20}",
                "Category": "Technology" if i % 2 == 0 else "Furniture",
                "Sub_Category": "Phones" if i % 3 == 0 else "Chairs",
                "Sales": float(100 + (i * 5)),
                "Profit": float(20 + (i * 2)),
                "Quantity": int(1 + (i % 10)),
                "Discount": float((i % 5) * 0.05)
            })

        df = pd.DataFrame(data)
        # Ensure exactly 237 rows and 11 columns
        self.assertEqual(df.shape, (237, 11))

        csv_buf = io.BytesIO()
        df.to_csv(csv_buf, index=False)
        csv_bytes = csv_buf.getvalue()

        # Process into session
        meta = dataset_service.process_file_bytes(csv_bytes, "slicer_test_237.csv", self.session)
        self.assertEqual(meta.total_rows, 237)
        self.assertEqual(meta.total_columns, 11)

    def tearDown(self):
        session_manager.clear_session(self.session.session_id)

    def test_region_and_state_slicers_full_lifecycle(self):
        # Initial: create a KPI and a chart to monitor dashboard-wide reactive updates
        kpi_ok, _, kpi = dashboard_service.create_kpi(self.session, "Sales", "sum", "Total Sales")
        self.assertTrue(kpi_ok)
        chart_ok, _, chart = dashboard_service.create_chart(
            self.session, "bar", "Category", "Sales", agg="sum", title="Sales by Category"
        )
        self.assertTrue(chart_ok)

        initial_total_sales = kpi.value
        self.assertGreater(initial_total_sales, 0)
        initial_chart_id = chart.id

        # Case 1 & 2: Natural language command to add Region and State slicers
        cmd_res = dashboard_service.process_command(self.session, "Add the slicer of Region and State")
        self.assertTrue(cmd_res.success)
        self.assertEqual(cmd_res.intent, "ADD_SLICER")
        self.assertIn("Region", cmd_res.message)
        self.assertIn("State", cmd_res.message)

        # Confirm 2 slicers were created in dashboard state
        filter_cols = [f.column for f in self.session.filters]
        self.assertIn("Region", filter_cols)
        self.assertIn("State", filter_cols)

        region_slicer = next(f for f in self.session.filters if f.column == "Region")
        state_slicer = next(f for f in self.session.filters if f.column == "State")

        # Distinct non-null options dynamically extracted
        self.assertEqual(set(region_slicer.options), {"East", "North", "South", "West"})
        # When no region is selected, state slicer displays all available states (13 states)
        self.assertEqual(len(state_slicer.options), 13)
        self.assertIn("Maharashtra", state_slicer.options)
        self.assertIn("Karnataka", state_slicer.options)
        self.assertIn("Delhi", state_slicer.options)

        # Case 3: Select one region ('West')
        apply_ok, _ = dashboard_service.apply_filter(self.session, "Region", ["West"])
        self.assertTrue(apply_ok)

        # Case 4: Confirm State options update dependent on selected region
        state_slicer = next(f for f in self.session.filters if f.column == "State")
        # Western states only: Goa, Gujarat, Maharashtra, Rajasthan
        expected_west_states = {"Goa", "Gujarat", "Maharashtra", "Rajasthan"}
        self.assertEqual(set(state_slicer.options), expected_west_states)
        self.assertNotIn("Karnataka", state_slicer.options)
        self.assertNotIn("Delhi", state_slicer.options)
        self.assertNotIn("Bihar", state_slicer.options)

        # Verify active dataset filtered to West only
        filtered_df = self.session.get_filtered_df()
        self.assertTrue(all(filtered_df["Region"] == "West"))
        west_rows = len(filtered_df)
        self.assertGreater(west_rows, 0)
        self.assertLess(west_rows, 237)

        # Case 5: Select multiple regions ('West', 'South')
        apply_ok, _ = dashboard_service.apply_filter(self.session, "Region", ["West", "South"])
        self.assertTrue(apply_ok)

        state_slicer = next(f for f in self.session.filters if f.column == "State")
        expected_west_south_states = {
            "Goa", "Gujarat", "Maharashtra", "Rajasthan",  # West
            "Karnataka", "Tamil Nadu", "Kerala"           # South
        }
        self.assertEqual(set(state_slicer.options), expected_west_south_states)
        self.assertNotIn("Delhi", state_slicer.options)
        self.assertNotIn("Bihar", state_slicer.options)

        filtered_df = self.session.get_filtered_df()
        self.assertTrue(all(filtered_df["Region"].isin(["West", "South"])))
        self.assertEqual(len(filtered_df[filtered_df["Region"] == "North"]), 0)

        # Case 6 & 7: Select one state ('Maharashtra') while Region has ['West', 'South']
        apply_ok, _ = dashboard_service.apply_filter(self.session, "State", ["Maharashtra"])
        self.assertTrue(apply_ok)

        # Case 8: Confirm AND logic: Region in ['West', 'South'] AND State == 'Maharashtra'
        filtered_df = self.session.get_filtered_df()
        self.assertTrue(all(filtered_df["State"] == "Maharashtra"))
        self.assertTrue(all(filtered_df["Region"] == "West"))
        mh_rows = len(filtered_df)
        self.assertGreater(mh_rows, 0)
        self.assertLess(mh_rows, west_rows)

        # Confirm every chart and KPI updates reactively
        updated_kpi = next(k for k in self.session.kpis if k.metric_col == "Sales")
        expected_sales_sum = float(filtered_df["Sales"].sum())
        self.assertAlmostEqual(updated_kpi.value, expected_sales_sum, places=2)
        self.assertNotEqual(updated_kpi.value, initial_total_sales)

        # Check paginated data table reflects filtered rows
        table_page = dataset_service.get_paginated_table(self.session, page=1, page_size=100)
        self.assertEqual(table_page["total_rows"], 237)
        self.assertEqual(table_page["filtered_rows"], mh_rows)
        self.assertTrue(all(r["State"] == "Maharashtra" for r in table_page["rows"]))

        # Remove individual selection: deselect State (or clear State filter)
        dashboard_service.clear_filter(self.session, "State")
        filtered_df = self.session.get_filtered_df()
        self.assertTrue(all(filtered_df["Region"].isin(["West", "South"])))
        self.assertEqual(len(filtered_df), len(self.session.df_working[self.session.df_working["Region"].isin(["West", "South"])]))

        # Case 9: Clear all filters and verify original dataset view returns
        dashboard_service.clear_filter(self.session)
        self.assertEqual(len(self.session.active_filters), 0)
        filtered_df = self.session.get_filtered_df()
        self.assertEqual(len(filtered_df), 237)

        # Verify state options expand back to all 13 states
        state_slicer = next(f for f in self.session.filters if f.column == "State")
        self.assertEqual(len(state_slicer.options), 13)

        # KPI returns to original total sales
        restored_kpi = next(k for k in self.session.kpis if k.metric_col == "Sales")
        self.assertAlmostEqual(restored_kpi.value, initial_total_sales, places=2)

        # Case 10: Verify existing charts and dashboard components remain intact
        self.assertEqual(len(self.session.charts), 1)
        self.assertEqual(self.session.charts[0].id, initial_chart_id)
        self.assertEqual(len(self.session.kpis), 1)

        # Verify original dataset was preserved without modification
        self.assertEqual(len(self.session.df_original), 237)
        self.assertEqual(self.session.df_original.shape, (237, 11))

        # Test remove slicer function
        dashboard_service.remove_slicer(self.session, "State")
        remaining_filter_cols = [f.column for f in self.session.filters]
        self.assertNotIn("State", remaining_filter_cols)
        self.assertIn("Region", remaining_filter_cols)

    def test_multilingual_slicer_commands(self):
        # 1. Hindi command
        res_hi = dashboard_service.process_command(self.session, "Region aur State ka slicer lagao")
        self.assertTrue(res_hi.success)
        self.assertEqual(res_hi.intent, "ADD_SLICER")
        self.assertIn("Region", [f.column for f in self.session.filters])
        self.assertIn("State", [f.column for f in self.session.filters])

        # Reset slicers
        self.session.filters = []

        # 2. Marathi command
        res_mr = dashboard_service.process_command(self.session, "Region aani State cha slicer tayar kara")
        self.assertTrue(res_mr.success)
        self.assertEqual(res_mr.intent, "ADD_SLICER")
        self.assertIn("Region", [f.column for f in self.session.filters])
        self.assertIn("State", [f.column for f in self.session.filters])

        # Reset slicers
        self.session.filters = []

        # 3. Hinglish code-mixed command
        res_cm = dashboard_service.process_command(self.session, "Region and State slicer banao")
        self.assertTrue(res_cm.success)
        self.assertEqual(res_cm.intent, "ADD_SLICER")
        self.assertIn("Region", [f.column for f in self.session.filters])
        self.assertIn("State", [f.column for f in self.session.filters])


if __name__ == "__main__":
    unittest.main()
