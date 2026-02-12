
import pytest
from pathlib import Path
from datetime import date
from mensabot.parser import read_menus


# Get the test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"

# Fixture that provides test data: (html_file_path, expected_menu_count)
@pytest.fixture(
    params=[
        # Test files from data folder with expected menu counts
        (TEST_DATA_DIR / "menu_default.html", 4),  # Old HTML format (product-wrapper)
        (TEST_DATA_DIR / "menu_holiday.html", 1),  # Was a holiday menu with only one item
        (TEST_DATA_DIR / "menu_format_matcard.html", 4),  # New HTML format (product-card)
    ],
    ids=[
        "default_format",
        "holiday_menu",
        "matcard_format",
    ],
)
def html_test_files(request):
    """
    Fixture providing HTML test files and expected menu counts.
    
    Each test file has a corresponding expected number of menu items.
    You can adjust the expected_count if your test files have different number of items.
    """
    file_path = request.param[0]
    expected_menu_count = request.param[1]
    
    return {
        "path": file_path,
        "expected_count": expected_menu_count,
        "file_name": file_path.name,
    }


class TestReadMenus:
    """Test suite for the read_menus function."""
    
    def test_read_menus_file_exists(self, html_test_files):
        """Test that the HTML file exists before trying to parse it."""
        assert html_test_files["path"].exists(), f"Test file not found: {html_test_files['path']}"
    
    def test_read_menus_returns_dataframe(self, html_test_files):
        """Test that read_menus returns a pandas DataFrame."""
        import pandas as pd
        
        df = read_menus(html_test_files["path"], date=date(2025, 8, 1))
        assert isinstance(df, pd.DataFrame), "read_menus should return a DataFrame"
    
    def test_read_menus_has_expected_count(self, html_test_files):
        """Test that read_menus finds the expected number of menu items."""
        df = read_menus(html_test_files["path"], date=date(2025, 8, 1))
        
        actual_count = len(df)
        expected_count = html_test_files["expected_count"]
        
        print(f"\nFound {actual_count} items in {html_test_files['file_name']}")
        if actual_count > 0:
            print(f"  Sample titles: {df['title'].head(3).tolist()}")
        
        assert actual_count == expected_count, (
            f"Expected {expected_count} menu items in {html_test_files['file_name']}, "
            f"but got {actual_count}"
        )
    
    def test_read_menus_has_required_columns(self, html_test_files):
        """Test that the returned DataFrame has all required columns."""
        df = read_menus(html_test_files["path"], date=date(2025, 8, 1))
        
        required_columns = {
            "day", "date", "title", "description", "price", 
            "provenance", "vegan", "vegetarian", "glutenfree", "co2_footprint"
        }
        
        actual_columns = set(df.columns)
        assert required_columns.issubset(actual_columns), (
            f"Missing columns: {required_columns - actual_columns}"
        )
    
    def test_read_menus_date_column_format(self, html_test_files):
        """Test that date column is in correct format."""
        df = read_menus(html_test_files["path"], date=date(2025, 8, 1))
        
        # All dates should be '2025-08-01'
        assert (df["date"] == "2025-08-01").all(), "All dates should be 2025-08-01"
    
    def test_read_menus_no_empty_titles(self, html_test_files):
        """Test that all menu items have titles."""
        df = read_menus(html_test_files["path"], date=date(2025, 8, 1))
        
        # Skip this test if no items found
        if len(df) == 0:
            pytest.skip("No menu items found in test file")
        
        assert not df["title"].isnull().any(), "Menu items should not have null titles"
        assert (df["title"] != "").all(), "Menu items should not have empty titles"
    
    def test_read_menus_prices_are_valid(self, html_test_files):
        """Test that prices are valid numbers or None."""
        import pandas as pd
        
        df = read_menus(html_test_files["path"], date=date(2025, 8, 1))
        
        # Skip this test if no items found
        if len(df) == 0:
            pytest.skip("No menu items found in test file")
        
        for price in df["price"]:
            if price is not None:
                # Try to convert to float to ensure it's a valid number
                try:
                    float(price)
                except ValueError:
                    pytest.fail(f"Invalid price format: {price}")
    
    def test_read_menus_boolean_columns(self, html_test_files):
        """Test that vegan, vegetarian, and glutenfree columns contain booleans."""
        df = read_menus(html_test_files["path"], date=date(2025, 8, 1))
        
        # Skip this test if no items found
        if len(df) == 0:
            pytest.skip("No menu items found in test file")
        
        boolean_columns = ["vegan", "vegetarian", "glutenfree"]
        for col in boolean_columns:
            assert df[col].dtype == bool, f"Column '{col}' should contain booleans"




