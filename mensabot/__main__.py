import argparse
import logging
import os
import re
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from .parser import read_menus

logger = logging.getLogger(__name__)


def download_html(uri, file):

    with sync_playwright() as p:
        logger.info(f"Acessing {uri}")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(uri)

        # Wait for content to load (e.g., an element that appears after JS finishes)
        try:
            page.wait_for_selector(
                ".category-grid"
            )  # Change selector based on the site
        except Exception as e:
            page.screenshot(path=raw_html / "debug.png", full_page=True)
            pass
        content = page.content()

        browser.close()

    # Save the content to a file

    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Downloaded content from {uri} to {file}")
    return file


def get_mattermost_webhook_url(url_file: Path) -> str:
    """Get the Mattermost webhook URL from environment variable or file."""
    url = os.environ.get("MATTERMOST_WEBHOOK_URL")
    if url is not None:
        return url
    if not url_file.is_file():
        raise ValueError(
            f"Mattermost webhook URL not found in environment variable "
            f"MATTERMOST_WEBHOOK_URL or file {url_file}"
        )
    with open(url_file, "r") as f:
        url = f.read().strip()  # Read the URL from a text file
    return url


def send_mattermost_message(url: str, text: str):

    # Send a message to Mattermost

    headers = {"Content-Type": "application/json"}

    payload = {"text": text}

    response = requests.post(url, json=payload, headers=headers)

    assert (
        response.status_code == 200
    ), f"Expected status code 200, got {response.status_code}"


def parse_price(price_str: str) -> str:
    """Depending on the price, return a formatted string."""
    try:
        price_str = str(price_str).strip()
    except Exception as e:
        logger.error(f"Error parsing price: {e}")
        return "N/A"

    try:
        price_float = float(price_str)
    except ValueError:
        logger.error(f"Error converting price to float: {price_str}")
        return "N/A"

    # Format the price string
    return f"*{price_float:.2f}*"


def format_as_markdown(df: pd.DataFrame, uris: dict[str, str] = {}) -> str:
    # Format the dataframe as markdown table for Mattermost
    df_formatted: pd.DataFrame = df[
        ["restaurant", "price", "vegan", "glutenfree", "title", "description"]
    ].copy(deep=True)
    # Put the column names with the first letter capitalized
    df_formatted.columns = [col.capitalize() for col in df_formatted.columns]

    # Put the resturant in bold
    make_bold = lambda col: col.str.replace(r"(\w+)", r"**\1**", regex=True)
    make_link = lambda col: f"[{col}]({uris[col]})" if col in uris else col
    df_formatted["Restaurant"] = df_formatted["Restaurant"].apply(make_link)
    df_formatted["Title"] = make_bold(df_formatted["Title"])
    # Format price with 2 decimal places (enforce for the markdown transformation)
    df_formatted["Price"] = df_formatted["Price"].apply(parse_price)
    df_formatted["Vegan"] = df_formatted["Vegan"].apply(lambda x: "✔️" if x else "❌")
    df_formatted["Glutenfree"] = df_formatted["Glutenfree"].apply(
        lambda x: "✔️" if x else "❌"
    )

    df_md = df_formatted.to_markdown(index=False, tablefmt="github")

    return df_md


def determine_target_date(custom_date_str: str = None, use_today: bool = False) -> date:
    """
    Determine the target date for fetching the menu.

    Args:
        custom_date_str: Custom date in YYYY-MM-DD format. Takes precedence over use_today.
        use_today: If True, use today's date. Otherwise, use next workday.

    Returns:
        The date to fetch the menu for.

    Raises:
        ValueError: If custom_date_str is provided but invalid format.
    """
    if custom_date_str:
        # Custom date provided
        try:
            return datetime.strptime(custom_date_str, "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"Invalid date format: {custom_date_str}. Expected YYYY-MM-DD")
            raise ValueError(
                f"Invalid date format: {custom_date_str}. Expected YYYY-MM-DD"
            )

    # Use --today flag or default to next workday
    today = date.today()
    if use_today:
        return today

    # Calculate next workday (skip to Monday if Friday)
    return today + pd.DateOffset(days=1 if today.weekday() != 4 else 3)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Mensabot - Fetch vegetarian/vegan menu items from SV restaurants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                # Run with default settings
  %(prog)s --debug                        # Run in debug mode (no Mattermost message)
  %(prog)s --no-download                  # Use existing HTML files
  %(prog)s --today                        # Get today's menu instead of next workday
  %(prog)s --date 2026-02-15              # Get menu for a specific date
  %(prog)s --debug --no-download          # Debug mode with existing files
  %(prog)s --date 2026-02-12 --debug      # Get menu for specific date in debug mode
        """,
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (don't send to Mattermost, show message content)",
    )

    parser.add_argument(
        "--no-download",
        dest="no_download",
        action="store_true",
        help="Don't download new HTML files, use existing ones",
    )

    parser.add_argument(
        "--today",
        action="store_true",
        help="Get today's menu instead of next workday's menu",
    )

    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Specify a custom date (YYYY-MM-DD format). Overrides --today if provided",
    )

    parser.add_argument(
        "--work-dir",
        type=str,
        default=Path.home() / ".mensabot",
        help="Working directory for storing menu data (default: %(default)s)",
    )

    parser.add_argument(
        "--log-level",
        "--log",
        dest="log_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: %(default)s)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()

    # Configure logging based on arguments
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Configuration from arguments
    work_dir = Path(args.work_dir)
    debug = args.debug
    download = not args.no_download  # Invert because arg is --no-download

    # Determine the date to download and whether to append it to the URI
    day_to_download = determine_target_date(
        custom_date_str=args.date, use_today=args.today
    )

    # Append date to URI only if we're not using today's date (i.e., for next workday or custom date)
    append_date_to_uri = not args.today

    # Print configuration in debug mode
    if debug:
        logger.info("=== Mensabot Configuration ===")
        logger.info(f"Work directory: {work_dir}")
        logger.info(f"Debug mode: {debug}")
        logger.info(f"Download new files: {download}")
        logger.info(f"Date to process: {day_to_download.strftime('%Y-%m-%d')}")
        logger.info(f"Append date to URI: {append_date_to_uri}")
        logger.info(f"Log level: {args.log_level}")
        logger.info("===============================")

    uris = {
        "Empa": "https://sv-restaurant.ch/menu/Empa-EAWAG,%20D%C3%BCbendorf/Mittagsmen%C3%BC%20Fire",
        "Eawag": "https://sv-restaurant.ch/menu/Empa-EAWAG,%20D%C3%BCbendorf/Lunch%20Aqa",
        "Amag": "https://sv-restaurant.ch/menu/AMAG,%20D%C3%BCbendorf/Mittagsmen%C3%BC",
        "Memphis": "https://sv-restaurant.ch/menu/Memphis,%20D%C3%BCbendorf/Lunch",
    }

    mensa_files = []

    errors = []

    for restaurant, uri in uris.items():
        save_path = work_dir / restaurant

        raw_html = save_path / "raw_html"
        raw_html.mkdir(exist_ok=True, parents=True)
        cleaned_csv_dir = save_path / "menus"
        cleaned_csv_dir.mkdir(exist_ok=True, parents=True)

        file = raw_html / f"menu_{day_to_download.strftime('%Y-%m-%d')}.html"

        try:
            if download:
                if append_date_to_uri:
                    uri = uri + "/date/" + day_to_download.strftime("%Y-%m-%d")
                download_html(uri, file)
            df = read_menus(file, date=day_to_download)
        except Exception as e:
            logger.error(f"Error processing {restaurant} menu: {e}")
            if debug:
                raise e
            errors.append(f"Error processing {restaurant} menu: {e}")
            continue

        logger.info(f"Parsed DataFrame:\n{df}")

        df["restaurant"] = restaurant

        # Save the data
        mensa_file = (
            cleaned_csv_dir / f"menu_{day_to_download.strftime('%Y-%m-%d')}.csv"
        )
        mensa_files.append(mensa_file)
        df.to_csv(mensa_file, index=False)

    try:
        # Read the dataframes
        df = pd.concat([pd.read_csv(mensa_file) for mensa_file in mensa_files])

        # Select only the vegetarian and vegan options
        df_veg = df[(df["vegetarian"] == True) | (df["vegan"] == True)].copy(deep=True)

        df_md = format_as_markdown(df_veg, uris=uris)

        logger.info(f"Formatted DataFrame for Mattermost:\n{df_md}")
    except Exception as e:
        logger.error(f"Error processing the dataframes: {e}")

        if debug:
            raise e
        errors.append(f"Error processing the dataframes: {e}")
        df_md = "No data available"

    error_md = (
        "\n\n ## Errors when processing data" + "\n".join(errors) if errors else ""
    )
    text = f"# {day_to_download.strftime('%A %d %B')} \n\n{df_md}{error_md}"

    if debug:
        logger.info(f"Debug mode - Message content:\n{text}")
        logger.info("=== Debug Mode ===")
        logger.info("Message was not sent to Mattermost (debug mode enabled)")
        logger.info("To send the actual message, run without --debug flag")
    else:
        url = get_mattermost_webhook_url(work_dir / "mattermost_url.txt")
        send_mattermost_message(url=url, text=text)
