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

if __name__ == "__main__":
    unittest.main()
