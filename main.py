from pathlib import Path
from datetime import datetime, date
import pandas as pd
from bs4 import BeautifulSoup
import requests
import logging
from playwright.sync_api import sync_playwright
import re


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


def read_menus(file):
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
        ]
    }

    for i, daily_menu in enumerate(daily_menus):
        day = datetime.now().strftime("%A")
        date = datetime.now().strftime("%Y-%m-%d")
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
            label_list = item.find("div", class_="label-list")
            if label_list:
                for img in label_list.find_all("img"):
                    alt = img.get("alt", "").lower()
                    title = img.get("title", "").lower()
                    if "vegan" in alt or "vegan" in title:
                        is_vegan = True
                    if "vegetar" in alt or "vegetar" in title:
                        is_vegetarian = True
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


def format_as_markdown(df: pd.DataFrame) -> str:
    # Format the dataframe as markdown table for Mattermost
    df_formatted: pd.DataFrame = df[
        ["restaurant", "price", "vegan", "title", "description"]
    ].copy(deep=True)
    # Put the column names with the first letter capitalized
    df_formatted.columns = [col.capitalize() for col in df_formatted.columns]

    # Put the resturant in bold
    make_bold = lambda col: col.str.replace(r"(\w+)", r"**\1**", regex=True)
    df_formatted["Restaurant"] = make_bold(df_formatted["Restaurant"])
    df_formatted["Title"] = make_bold(df_formatted["Title"])
    # Format price with 2 decimal places (enforce for the markdown transformation)
    df_formatted["Price"] = df_formatted["Price"].apply(parse_price)
    df_formatted["Vegan"] = df_formatted["Vegan"].apply(lambda x: "✔️" if x else "❌")

    df_md = df_formatted.to_markdown(index=False, tablefmt="github")

    return df_md


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    work_dir = Path("/home/coli/Documents/mensabot")

    # Debug option when testing the script, will raise exceptions so that you can see the errors
    # it will not send the message to Mattermost to avoid spamming
    debug = False
    # Whether to redownload the menus
    # useful when debugging the script
    download = True

    uris = {
        "Empa": "https://sv-restaurant.ch/menu/Empa-EAWAG,%20D%C3%BCbendorf/Mittagsmen%C3%BC%20Fire",
        "Eawag": "https://sv-restaurant.ch/menu/Empa-EAWAG,%20D%C3%BCbendorf/Lunch%20Aqa",
        "Amag": "https://sv-restaurant.ch/menu/AMAG,%20D%C3%BCbendorf/Mittagsmen%C3%BC",
    }

    mensa_files = []

    errors = []

    for restaurant, uri in uris.items():
        save_path = work_dir / restaurant

        raw_html = save_path / "raw_html"
        raw_html.mkdir(exist_ok=True, parents=True)
        outputs = save_path / "outputs"
        outputs.mkdir(exist_ok=True, parents=True)

        file = raw_html / f"menu_{date.today()}.html"

        try:
            if download:
                download_html(uri, file)
            df = read_menus(file)
        except Exception as e:
            logger.error(f"Error processing {restaurant} menu: {e}")
            if debug:
                raise e
            errors.append(f"Error processing {restaurant} menu: {e}")
            continue

        logger.info(f"Parsed DataFrame:\n{df}")

        df["restaurant"] = restaurant

        # Save the data
        mensa_file = save_path / f"menu_{date.today()}.csv"
        mensa_files.append(mensa_file)
        df.to_csv(mensa_file, index=False)

    try:
        # Read the dataframes
        df = pd.concat([pd.read_csv(mensa_file) for mensa_file in mensa_files])

        # Select only the vegetarian and vegan options
        df_veg = df[(df["vegetarian"] == True) | (df["vegan"] == True)].copy(deep=True)

        df_md = format_as_markdown(df_veg)

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
    text = f"# Vegi menus today \n\n 🥑🍆🥔🥕🌽🌶️ 🫑 🥒🥬🥦🧄🧅🥜 🫘 🌰🍄  \n\n{df_md}{error_md}"

    if debug:
        logger.info(f"Message: {text}")
    else:
        send_mattermost_message(url_file=work_dir / "mattermost_url.txt", text=text)
