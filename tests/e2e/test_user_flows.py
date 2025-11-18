"""
End-to-end tests for user flows using Playwright.

Tests cover:
- User authentication flows
- Navigation flows
- Data collection workflows
- Analysis workflows
- Report generation
"""

import pytest
from playwright.sync_api import Page, expect
import re


@pytest.mark.e2e
class TestAuthenticationFlows:
    """Test user authentication flows."""

    def test_user_login_flow(self, page: Page, base_url: str, test_user_credentials):
        """Test complete user login flow."""
        # Navigate to login page
        page.goto(f"{base_url}/login")

        # Fill in credentials
        page.fill("input[name='username']", test_user_credentials["username"])
        page.fill("input[name='password']", test_user_credentials["password"])

        # Click login button
        page.click("button[type='submit']")

        # Wait for navigation to dashboard
        page.wait_for_url(f"{base_url}/dashboard")

        # Verify login successful
        expect(page.locator("h1")).to_contain_text("Dashboard")

    def test_user_logout_flow(self, page: Page, base_url: str):
        """Test user logout flow."""
        # Assume already logged in
        page.goto(f"{base_url}/dashboard")

        # Click logout button
        page.click("button[data-test='logout']")

        # Verify redirected to login
        page.wait_for_url(f"{base_url}/login")
        expect(page.locator("h1")).to_contain_text("Login")

    def test_invalid_login_attempt(self, page: Page, base_url: str):
        """Test login with invalid credentials."""
        page.goto(f"{base_url}/login")

        page.fill("input[name='username']", "invalid_user")
        page.fill("input[name='password']", "wrong_password")
        page.click("button[type='submit']")

        # Verify error message displayed
        expect(page.locator(".error-message")).to_be_visible()
        expect(page.locator(".error-message")).to_contain_text("Invalid credentials")

    def test_password_reset_flow(self, page: Page, base_url: str):
        """Test password reset flow."""
        page.goto(f"{base_url}/login")

        # Click forgot password link
        page.click("a[href='/forgot-password']")

        # Enter email
        page.fill("input[name='email']", "test@example.com")
        page.click("button[type='submit']")

        # Verify success message
        expect(page.locator(".success-message")).to_contain_text("Reset email sent")


@pytest.mark.e2e
class TestCollectionWorkflows:
    """Test data collection workflows."""

    def test_dns_collection_workflow(self, page: Page, base_url: str):
        """Test DNS collection through UI."""
        # Navigate to collectors page
        page.goto(f"{base_url}/collectors")

        # Select DNS collector
        page.click("button[data-collector='dns']")

        # Enter target domain
        page.fill("input[name='target']", "example.com")

        # Start collection
        page.click("button[data-test='start-collection']")

        # Wait for collection to complete
        page.wait_for_selector(".collection-status[data-status='completed']", timeout=30000)

        # Verify results displayed
        expect(page.locator(".results-container")).to_be_visible()
        expect(page.locator(".results-container")).to_contain_text("A Records")

    def test_whois_collection_workflow(self, page: Page, base_url: str):
        """Test WHOIS collection through UI."""
        page.goto(f"{base_url}/collectors/whois")

        page.fill("input[name='domain']", "example.com")
        page.click("button[type='submit']")

        # Wait for results
        page.wait_for_selector(".whois-results", timeout=30000)

        # Verify WHOIS data displayed
        expect(page.locator(".whois-results")).to_contain_text("Registrar")
        expect(page.locator(".whois-results")).to_contain_text("Creation Date")

    def test_multiple_collector_workflow(self, page: Page, base_url: str):
        """Test running multiple collectors."""
        page.goto(f"{base_url}/collectors/batch")

        # Select multiple collectors
        page.check("input[value='dns']")
        page.check("input[value='whois']")
        page.check("input[value='ssl']")

        # Enter target
        page.fill("input[name='target']", "example.com")

        # Start batch collection
        page.click("button[data-test='start-batch']")

        # Wait for all to complete
        page.wait_for_selector(".batch-status[data-status='completed']", timeout=60000)

        # Verify all results present
        expect(page.locator(".dns-results")).to_be_visible()
        expect(page.locator(".whois-results")).to_be_visible()
        expect(page.locator(".ssl-results")).to_be_visible()

    def test_collection_error_handling(self, page: Page, base_url: str):
        """Test error handling in collection workflow."""
        page.goto(f"{base_url}/collectors/dns")

        # Enter invalid domain
        page.fill("input[name='target']", "invalid..domain")
        page.click("button[type='submit']")

        # Verify error message
        expect(page.locator(".error-message")).to_be_visible()
        expect(page.locator(".error-message")).to_contain_text("Invalid domain")


@pytest.mark.e2e
class TestAnalysisWorkflows:
    """Test analysis workflows."""

    def test_graph_analysis_workflow(self, page: Page, base_url: str):
        """Test graph analysis visualization."""
        page.goto(f"{base_url}/analysis/graph")

        # Enter entity to analyze
        page.fill("input[name='entity']", "8.8.8.8")
        page.click("button[data-test='analyze']")

        # Wait for graph to render
        page.wait_for_selector(".graph-container svg", timeout=30000)

        # Verify graph elements
        expect(page.locator(".graph-container svg")).to_be_visible()
        expect(page.locator(".node")).to_have_count_greater_than(0)
        expect(page.locator(".edge")).to_have_count_greater_than(0)

    def test_relationship_explorer(self, page: Page, base_url: str):
        """Test relationship explorer UI."""
        page.goto(f"{base_url}/analysis/relationships")

        # Select entity
        page.fill("input[name='entity']", "example.com")
        page.click("button[data-test='explore']")

        # Wait for relationships to load
        page.wait_for_selector(".relationships-list", timeout=30000)

        # Verify relationships displayed
        expect(page.locator(".relationship-item")).to_have_count_greater_than(0)

        # Click on relationship to see details
        page.click(".relationship-item:first-child")

        # Verify detail panel opens
        expect(page.locator(".relationship-details")).to_be_visible()

    def test_pattern_detection_workflow(self, page: Page, base_url: str):
        """Test pattern detection workflow."""
        page.goto(f"{base_url}/analysis/patterns")

        # Select pattern type
        page.select_option("select[name='pattern-type']", "infrastructure")

        # Set parameters
        page.fill("input[name='entity-count']", "5")
        page.click("button[data-test='detect-patterns']")

        # Wait for results
        page.wait_for_selector(".patterns-results", timeout=30000)

        # Verify patterns found
        expect(page.locator(".pattern-item")).to_have_count_greater_than(0)


@pytest.mark.e2e
class TestRiskScoringWorkflows:
    """Test risk scoring workflows."""

    def test_risk_score_calculation(self, page: Page, base_url: str):
        """Test risk score calculation workflow."""
        page.goto(f"{base_url}/scoring")

        # Enter entity to score
        page.fill("input[name='entity']", "8.8.8.8")
        page.click("button[data-test='calculate-score']")

        # Wait for score calculation
        page.wait_for_selector(".risk-score-display", timeout=30000)

        # Verify score displayed
        expect(page.locator(".risk-score-display")).to_be_visible()
        expect(page.locator(".score-value")).to_have_text(re.compile(r"\d+"))
        expect(page.locator(".severity-level")).to_be_visible()

    def test_score_factors_breakdown(self, page: Page, base_url: str):
        """Test viewing score factors breakdown."""
        page.goto(f"{base_url}/scoring/8.8.8.8")

        # Expand factors breakdown
        page.click("button[data-test='show-factors']")

        # Verify factors displayed
        expect(page.locator(".factor-item")).to_have_count_greater_than(0)
        expect(page.locator(".factor-weight")).to_be_visible()
        expect(page.locator(".factor-score")).to_be_visible()

    def test_score_history_view(self, page: Page, base_url: str):
        """Test viewing score history."""
        page.goto(f"{base_url}/scoring/8.8.8.8/history")

        # Verify history chart displayed
        expect(page.locator(".score-history-chart")).to_be_visible()

        # Verify history table
        expect(page.locator(".history-table tbody tr")).to_have_count_greater_than(0)

        # Test date range filtering
        page.fill("input[name='start-date']", "2024-01-01")
        page.fill("input[name='end-date']", "2024-01-31")
        page.click("button[data-test='filter-history']")

        # Verify filtered results
        page.wait_for_selector(".history-table.filtered", timeout=5000)


@pytest.mark.e2e
class TestWorkflowExecution:
    """Test workflow execution through UI."""

    def test_create_workflow(self, page: Page, base_url: str):
        """Test creating a new workflow."""
        page.goto(f"{base_url}/workflows/new")

        # Fill workflow details
        page.fill("input[name='name']", "Test Investigation")
        page.fill("textarea[name='description']", "Test workflow description")

        # Add tasks
        page.click("button[data-test='add-task']")
        page.select_option("select[name='task-type']", "dns_collector")
        page.fill("input[name='task-param']", "example.com")

        # Save workflow
        page.click("button[data-test='save-workflow']")

        # Verify workflow created
        expect(page.locator(".success-message")).to_contain_text("Workflow created")

    def test_execute_workflow(self, page: Page, base_url: str):
        """Test executing a workflow."""
        page.goto(f"{base_url}/workflows")

        # Select workflow
        page.click(".workflow-item:first-child")

        # Execute workflow
        page.click("button[data-test='execute-workflow']")

        # Monitor progress
        page.wait_for_selector(".execution-progress", timeout=5000)

        # Wait for completion
        page.wait_for_selector(".execution-status[data-status='completed']", timeout=60000)

        # Verify results available
        expect(page.locator(".workflow-results")).to_be_visible()

    def test_workflow_pause_resume(self, page: Page, base_url: str):
        """Test pausing and resuming workflow execution."""
        page.goto(f"{base_url}/workflows/execute/test-workflow")

        # Start execution
        page.click("button[data-test='start-execution']")

        # Wait a moment then pause
        page.wait_for_timeout(2000)
        page.click("button[data-test='pause-execution']")

        # Verify paused state
        expect(page.locator(".execution-status")).to_contain_text("Paused")

        # Resume execution
        page.click("button[data-test='resume-execution']")

        # Verify resumed
        expect(page.locator(".execution-status")).to_contain_text("Running")


@pytest.mark.e2e
class TestReportGeneration:
    """Test report generation workflows."""

    def test_generate_investigation_report(self, page: Page, base_url: str):
        """Test generating investigation report."""
        page.goto(f"{base_url}/reports/new")

        # Select report type
        page.select_option("select[name='report-type']", "investigation")

        # Select entities to include
        page.fill("input[name='entity']", "example.com")
        page.click("button[data-test='add-entity']")

        # Select sections
        page.check("input[value='collection-results']")
        page.check("input[value='risk-scores']")
        page.check("input[value='relationships']")

        # Generate report
        page.click("button[data-test='generate-report']")

        # Wait for report generation
        page.wait_for_selector(".report-preview", timeout=30000)

        # Verify report sections
        expect(page.locator(".report-section")).to_have_count(3)

    def test_export_report_pdf(self, page: Page, base_url: str):
        """Test exporting report as PDF."""
        page.goto(f"{base_url}/reports/123")

        # Click export button
        with page.expect_download() as download_info:
            page.click("button[data-test='export-pdf']")

        download = download_info.value

        # Verify download
        assert download.suggested_filename.endswith(".pdf")

    def test_export_report_json(self, page: Page, base_url: str):
        """Test exporting report as JSON."""
        page.goto(f"{base_url}/reports/123")

        with page.expect_download() as download_info:
            page.click("button[data-test='export-json']")

        download = download_info.value

        # Verify download
        assert download.suggested_filename.endswith(".json")


@pytest.mark.e2e
class TestNavigationFlows:
    """Test navigation flows."""

    def test_main_navigation(self, page: Page, base_url: str):
        """Test main navigation menu."""
        page.goto(f"{base_url}/dashboard")

        # Test navigation links
        page.click("a[href='/collectors']")
        expect(page).to_have_url(f"{base_url}/collectors")

        page.click("a[href='/analysis']")
        expect(page).to_have_url(f"{base_url}/analysis")

        page.click("a[href='/scoring']")
        expect(page).to_have_url(f"{base_url}/scoring")

        page.click("a[href='/workflows']")
        expect(page).to_have_url(f"{base_url}/workflows")

    def test_breadcrumb_navigation(self, page: Page, base_url: str):
        """Test breadcrumb navigation."""
        page.goto(f"{base_url}/analysis/graph/entity-123")

        # Verify breadcrumbs present
        expect(page.locator(".breadcrumb")).to_be_visible()

        # Click breadcrumb to navigate back
        page.click(".breadcrumb a:has-text('Analysis')")
        expect(page).to_have_url(f"{base_url}/analysis")

    def test_search_functionality(self, page: Page, base_url: str):
        """Test global search functionality."""
        page.goto(f"{base_url}/dashboard")

        # Open search
        page.click("button[data-test='open-search']")

        # Enter search query
        page.fill("input[name='search']", "8.8.8.8")
        page.press("input[name='search']", "Enter")

        # Verify search results
        expect(page.locator(".search-results")).to_be_visible()
        expect(page.locator(".search-result-item")).to_have_count_greater_than(0)


@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteUserJourneys:
    """Test complete user journeys."""

    def test_complete_investigation_journey(self, page: Page, base_url: str):
        """Test complete investigation from start to finish."""
        # 1. Login
        page.goto(f"{base_url}/login")
        page.fill("input[name='username']", "test_user")
        page.fill("input[name='password']", "test_password")
        page.click("button[type='submit']")

        # 2. Navigate to collectors
        page.click("a[href='/collectors']")

        # 3. Run DNS collection
        page.click("button[data-collector='dns']")
        page.fill("input[name='target']", "example.com")
        page.click("button[data-test='start-collection']")
        page.wait_for_selector(".collection-status[data-status='completed']", timeout=30000)

        # 4. View analysis
        page.click("a[href='/analysis']")
        page.fill("input[name='entity']", "example.com")
        page.click("button[data-test='analyze']")
        page.wait_for_selector(".graph-container svg", timeout=30000)

        # 5. Check risk score
        page.click("a[href='/scoring']")
        page.fill("input[name='entity']", "example.com")
        page.click("button[data-test='calculate-score']")
        page.wait_for_selector(".risk-score-display", timeout=30000)

        # 6. Generate report
        page.click("a[href='/reports/new']")
        page.fill("input[name='entity']", "example.com")
        page.click("button[data-test='add-entity']")
        page.check("input[value='all-sections']")
        page.click("button[data-test='generate-report']")
        page.wait_for_selector(".report-preview", timeout=30000)

        # 7. Export report
        with page.expect_download():
            page.click("button[data-test='export-pdf']")

        # Verify complete journey
        expect(page.locator(".report-preview")).to_be_visible()
