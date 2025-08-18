from pathlib import Path
from datetime import datetime, date
import logging
import re
import argparse

import requests
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


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


def find_labels(img: BeautifulSoup) -> str | None:
    """Find all vegan/vegetarian in the labels-list div."""
    alt = img.get("alt", "").lower()
    title = img.get("title", "").lower()
    if "vegan" in alt or "vegan" in title:
        return "vegan"
    elif "vegetar" in alt or "vegetar" in title:
        return "vegetarian"
    elif "glutenfrei" in alt or "glutenfrei" in title:
        return "glutenfree"
    elif "gluten-free" in alt or "gluten-free" in title:
        return "glutenfree"
    elif alt.startswith("co2"):
        # The title is something like this: 
        # Your ecological footprint represents 0.7 g CO2e
        # Get the number
        match = re.search(r"([\d.]+)\s*g\s*co2e", title, re.IGNORECASE)
        if match:
            return f"co2_{match.group(1)}"
    else:
        return None


def read_menus(file, date: date):
    with open(file, "r") as f:
        html_content = f.read()

    logger.debug(f"HTML content from {file}")

    # <div class="category-grid ng-star-inserted"><app-category _nghost-ng-c4143720142="" class="grid-row ng-star-inserted"><!----><h3 _ngcontent-ng-c4143720142="" class="h3 category-header ng-star-inserted"> Local to Global </h3><!----><app-product-list _ngcontent-ng-c4143720142="" _nghost-ng-c1967480023="" class="ng-star-inserted"><div _ngcontent-ng-c1967480023="" appclickablearea="" class="product-wrapper ng-star-inserted"><div _ngcontent-ng-c1967480023="" layout="row"><div _ngcontent-ng-c1967480023="" flex=""><div _ngcontent-ng-c1967480023="" layout-gt-sm="row"><div _ngcontent-ng-c1967480023="" class="name-column pad-right-sm pad-bottom-sm"><button _ngcontent-ng-c1967480023="" appclickableareatarget="" class="button-reset link-reset"><span _ngcontent-ng-c1967480023="" class="pre-wrap legacy-text-xxl">Buddha Bowl</span></button><div _ngcontent-ng-c1967480023="" class="product-teaser push-top-xs ng-star-inserted"> mit Quinoa, Randen Falafel, Zucchetti, Sesam  Rettich Pickles, Lattich, Cherrytomaten und Olivenöl-Zitronen Dressing | Tagessalat und 1dl Saft </div><!----><!----></div><div _ngcontent-ng-c1967480023="" class="allergen-column ng-star-inserted"><app-product-label-list _ngcontent-ng-c1967480023=""><!----><!----><div class="label-list customtag-list ng-star-inserted"><app-product-custom-tag _nghost-ng-c1604586910="" class="ng-star-inserted"><img _ngcontent-ng-c1604586910="" src="https://files.qnips.com/releaseicons/20230405sviconsvegan_2024.07.02_09.01.13.png" title="Vegan" alt="Vegan" class="ng-star-inserted"><!----><!----></app-product-custom-tag><app-product-custom-tag _nghost-ng-c1604586910="" class="ng-star-inserted"><img _ngcontent-ng-c1604586910="" src="https://files.qnips.com/releaseicons/20230405sviconsglutenfrei_2024.07.02_09.01.40.png" title="Glutenfrei" alt="Glutenfrei" class="ng-star-inserted"><!----><!----></app-product-custom-tag><app-product-custom-tag _nghost-ng-c1604586910="" class="ng-star-inserted"><img _ngcontent-ng-c1604586910="" src="https://files.qnips.com/releaseicons/20230405sviconslaktosefrei_2024.07.02_09.01.51.png" title="Laktosefrei" alt="Laktosefrei" class="ng-star-inserted"><!----><!----></app-product-custom-tag><!----><!----></div><!----></app-product-label-list></div><!----><div _ngcontent-ng-c1967480023="" class="price-column legacy-text-lg text-right pad-left-sm ng-star-inserted"><div _ngcontent-ng-c1967480023="" class="price ng-star-inserted">   <!----> &nbsp;CHF&nbsp;11.50 <!----></div><!----></div><!----><div _ngcontent-ng-c1967480023="" layout="row" layout-gt-sm="column" layout-align="start end"><!----><!----></div></div></div></div><!----></div><!----></app-product-list><!----><!----><!----><!----><!----></app-category><app-category _nghost-ng-c4143720142="" class="grid-row ng-star-inserted"><!----><h3 _ngcontent-ng-c4143720142="" class="h3 category-header ng-star-inserted"> Twist and Trend </h3><!----><app-product-list _ngcontent-ng-c4143720142="" _nghost-ng-c1967480023="" class="ng-star-inserted"><div _ngcontent-ng-c1967480023="" appclickablearea="" class="product-wrapper ng-star-inserted"><div _ngcontent-ng-c1967480023="" layout="row"><div _ngcontent-ng-c1967480023="" flex=""><div _ngcontent-ng-c1967480023="" layout-gt-sm="row"><div _ngcontent-ng-c1967480023="" class="name-column pad-right-sm pad-bottom-sm"><button _ngcontent-ng-c1967480023="" appclickableareatarget="" class="button-reset link-reset"><span _ngcontent-ng-c1967480023="" class="pre-wrap legacy-text-xxl">Berliner Currywurst</span></button><div _ngcontent-ng-c1967480023="" class="product-teaser push-top-xs ng-star-inserted"> mit Pommes Frites | Tagessalat und 1 dl Saft </div><!----><!----></div><div _ngcontent-ng-c1967480023="" class="allergen-column ng-star-inserted"><app-product-label-list _ngcontent-ng-c1967480023=""><!----><!----><div class="label-list customtag-list ng-star-inserted"><app-product-custom-tag _nghost-ng-c1604586910="" class="ng-star-inserted"><img _ngcontent-ng-c1604586910="" src="https://files.qnips.com/releaseicons/20230405sviconsglutenfrei_2024.07.02_09.01.40.png" title="Glutenfrei" alt="Glutenfrei" class="ng-star-inserted"><!----><!----></app-product-custom-tag><app-product-custom-tag _nghost-ng-c1604586910="" class="ng-star-inserted"><img _ngcontent-ng-c1604586910="" src="https://files.qnips.com/releaseicons/20230405sviconslaktosefrei_2024.07.02_09.01.51.png" title="Laktosefrei" alt="Laktosefrei" class="ng-star-inserted"><!----><!----></app-product-custom-tag><!----><!----></div><!----></app-product-label-list></div><!----><div _ngcontent-ng-c1967480023="" class="price-column legacy-text-lg text-right pad-left-sm ng-star-inserted"><div _ngcontent-ng-c1967480023="" class="price ng-star-inserted">   <!----> &nbsp;CHF&nbsp;13.50 <!----></div><!----></div><!----><div _ngcontent-ng-c1967480023="" layout="row" layout-gt-sm="column" layout-align="start end"><!----><!----></div></div></div></div><!----></div><!----></app-product-list><!----><!----><!----><!----><!----></app-category><app-category _nghost-ng-c4143720142="" class="grid-row ng-star-inserted"><!----><h3 _ngcontent-ng-c4143720142="" class="h3 category-header ng-star-inserted"> Grill n’ Bun </h3><!----><app-product-list _ngcontent-ng-c4143720142="" _nghost-ng-c1967480023="" class="ng-star-inserted"><div _ngcontent-ng-c1967480023="" appclickablearea="" class="product-wrapper ng-star-inserted"><div _ngcontent-ng-c1967480023="" layout="row"><div _ngcontent-ng-c1967480023="" flex=""><div _ngcontent-ng-c1967480023="" layout-gt-sm="row"><div _ngcontent-ng-c1967480023="" class="name-column pad-right-sm pad-bottom-sm"><button _ngcontent-ng-c1967480023="" appclickableareatarget="" class="button-reset link-reset"><span _ngcontent-ng-c1967480023="" class="pre-wrap legacy-text-xxl">Empa Fitnessteller</span></button><div _ngcontent-ng-c1967480023="" class="product-teaser push-top-xs ng-star-inserted"> mit Schweins Pfefferspies, Ayvar und Salat nach Wahl vom Buffet | Tagessuppe oder 1dl Saft </div><!----><!----></div><div _ngcontent-ng-c1967480023="" class="allergen-column ng-star-inserted"><app-product-label-list _ngcontent-ng-c1967480023=""><!----><!----><div class="label-list customtag-list ng-star-inserted"><app-product-custom-tag _nghost-ng-c1604586910="" class="ng-star-inserted"><img _ngcontent-ng-c1604586910="" src="https://files.qnips.com/releaseicons/20230405sviconsglutenfrei_2024.07.02_09.01.40.png" title="Glutenfrei" alt="Glutenfrei" class="ng-star-inserted"><!----><!----></app-product-custom-tag><!----><!----></div><!----></app-product-label-list></div><!----><div _ngcontent-ng-c1967480023="" class="price-column legacy-text-lg text-right pad-left-sm ng-star-inserted"><div _ngcontent-ng-c1967480023="" class="price ng-star-inserted">   <!----> &nbsp;CHF&nbsp;16.80 <!----></div><!----></div><!----><div _ngcontent-ng-c1967480023="" layout="row" layout-gt-sm="column" layout-align="start end"><!----><!----></div></div></div></div><!----></div><!----></app-product-list><!----><!----><!----><!----><!----></app-category><app-category _nghost-ng-c4143720142="" class="grid-row ng-star-inserted"><!----><h3 _ngcontent-ng-c4143720142="" class="h3 category-header ng-star-inserted"> Hot &amp; Cold </h3><!----><app-product-list _ngcontent-ng-c4143720142="" _nghost-ng-c1967480023="" class="ng-star-inserted"><div _ngcontent-ng-c1967480023="" appclickablearea="" class="product-wrapper ng-star-inserted"><div _ngcontent-ng-c1967480023="" layout="row"><div _ngcontent-ng-c1967480023="" flex=""><div _ngcontent-ng-c1967480023="" layout-gt-sm="row"><div _ngcontent-ng-c1967480023="" class="name-column pad-right-sm pad-bottom-sm"><button _ngcontent-ng-c1967480023="" appclickableareatarget="" class="button-reset link-reset"><span _ngcontent-ng-c1967480023="" class="pre-wrap legacy-text-xxl">Öffnungszeiten Sommerferien</span></button><div _ngcontent-ng-c1967480023="" class="product-teaser push-top-xs ng-star-inserted"> Das Restaurant Fire ist von  06.30 - 13.30 Uhr geöffnet Mittagsservice ist von 11.15 - 13.00 Uhr </div><!----><!----></div><div _ngcontent-ng-c1967480023="" class="allergen-column ng-star-inserted"><app-product-label-list _ngcontent-ng-c1967480023=""><!----><!----><!----></app-product-label-list></div><!----><div _ngcontent-ng-c1967480023="" class="price-column legacy-text-lg text-right pad-left-sm ng-star-inserted"><!----></div><!----><div _ngcontent-ng-c1967480023="" layout="row" layout-gt-sm="column" layout-align="start end"><!----><!----></div></div></div></div><!----></div><!----></app-product-list><!----><!----><!----><!----><!----></app-category><!----></div>
    # Parse the HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all menu items
    daily_menus = soup.find_all(class_="category-grid")

    logger.debug(f"Found {len(daily_menus)} daily menus")

    logger.debug(
        f"Daily menu: {daily_menus[0].prettify() if daily_menus else 'No daily menus found'}"
    )

    menus = {
        field: []
        for field in [
            "day",
            "date",
            "title",
            "description",
            "price",
            "provenance",
            "vegan",
            "vegetarian",
            "glutenfree",
            "co2_footprint",
        ]
    }

    day = date.strftime("%A")
    date = date.strftime("%Y-%m-%d")
    for i, daily_menu in enumerate(daily_menus):
        # Read the menu items

        menu_items = daily_menu.find_all(class_="product-wrapper")
        logger.info(f"Found {len(menu_items)} menu items")

        # Iterate over each menu item and extract relevant information
        for index, item in enumerate(menu_items):
            logger.debug(f"Processing {item.prettify()}")

            title_menu = item.find(class_="pre-wrap").text.strip()
            description = item.find(class_="product-teaser").text.strip()
            # Find all price elements
            price_elems = item.find_all(class_="price")
            price = None
            for pe in price_elems:
                text = pe.get_text(separator=" ", strip=True)
                if text.startswith("EXT"):
                    # Extract the price after 'CHF'
                    match = re.search(r"CHF\s*([\d.,]+)", text)
                    if match:
                        price = match.group(1).replace(",", ".")
                    break
            # Fallback: if no EXT price found, use the first price if available
            if price is None and price_elems:
                text = price_elems[0].get_text(separator=" ", strip=True)
                match = re.search(r"CHF\s*([\d.,]+)", text)
                if match:
                    price = match.group(1).replace(",", ".")

            provenance = item.find(class_="menu-provenance")
            provenance = provenance.text.strip() if provenance else None

            # Detect vegan/vegetarian by <img> alt or title attributes in label-list
            is_vegan = False
            is_vegetarian = False
            co2_footprint = None
            glutenfree = False
            label_lists = item.find_all("div", class_="label-list")

            if label_lists:
                # Put all the ResultSet together
                for label_list in label_lists:
                    logger.debug(f"Processing label list: {label_list.prettify()}")
                    for img in label_list.find_all("img"):
                        label = find_labels(img)
                        if label is None:
                            continue
                        elif label == "vegan":
                            is_vegan = True
                        elif label == "vegetarian":
                            is_vegetarian = True
                        elif label == "glutenfree":
                            glutenfree = True
                        elif label.startswith("co2_"):
                            co2_footprint = label[4:]
                        else:
                            logger.warning(f"Unknown label: {label}")
            # If vegan, also mark as vegetarian
            if is_vegan:
                is_vegetarian = True

            menus["day"].append(day)
            menus["date"].append(date)
            menus["title"].append(title_menu)
            menus["description"].append(
                description.replace("\n", " ").replace("|", ",")
            )
            menus["price"].append(price)
            menus["provenance"].append(provenance)
            menus["vegan"].append(is_vegan)
            menus["vegetarian"].append(is_vegetarian)
            menus["glutenfree"].append(glutenfree)
            menus["co2_footprint"].append(co2_footprint)

    df_menus = pd.DataFrame(menus)

    return df_menus


def send_mattermost_message(url_file, text: str):

    # Send a messag to Mattermost
    with open(url_file, "r") as f:
        url = f.read().strip()  # Read the URL from a text file

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
    df_formatted["Glutenfree"] = df_formatted["Glutenfree"].apply(lambda x: "✔️" if x else "❌")

    df_md = df_formatted.to_markdown(index=False, tablefmt="github")

    return df_md


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Mensabot - Fetch vegetarian/vegan menu items from SV restaurants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run with default settings
  %(prog)s --debug                  # Run in debug mode (no Mattermost message)
  %(prog)s --no-download            # Use existing HTML files
  %(prog)s --today                  # Get today's menu instead of next workday
  %(prog)s --debug --no-download    # Debug mode with existing files
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
    next_day = not args.today  # Invert because arg is --today

    # Print configuration in debug mode
    if debug:
        logger.info("=== Mensabot Configuration ===")
        logger.info(f"Work directory: {work_dir}")
        logger.info(f"Debug mode: {debug}")
        logger.info(f"Download new files: {download}")
        logger.info(f"Next workday menu: {next_day}")
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

    today = date.today()
    day_to_download = (
        today
        + pd.DateOffset(
            # In case it is friday , we want to download the menu for monday
            days=1 if today.weekday() != 4 else 3
        )
        if next_day
        else today
    )

    for restaurant, uri in uris.items():
        save_path = work_dir / restaurant

        raw_html = save_path / "raw_html"
        raw_html.mkdir(exist_ok=True, parents=True)
        cleaned_csv_dir = save_path / "menus"
        cleaned_csv_dir.mkdir(exist_ok=True, parents=True)

        file = raw_html / f"menu_{day_to_download.strftime('%Y-%m-%d')}.html"

        try:
            if download:
                if next_day:
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
        send_mattermost_message(url_file=work_dir / "mattermost_url.txt", text=text)
