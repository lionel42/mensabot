import logging
import re
from datetime import date

from bs4 import BeautifulSoup
import pandas as pd

from pathlib import Path


logger = logging.getLogger(__name__)


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


def read_menus(file: Path, date: date) -> pd.DataFrame:

    file = Path(file)

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
        # Read the menu items - try both old and new HTML structures
        menu_items = daily_menu.find_all(class_="product-wrapper")

        # If old structure not found, try new structure (mat-card)
        if not menu_items:
            menu_items = daily_menu.find_all(class_="product-card")
            is_new_format = True
        else:
            is_new_format = False

        logger.info(
            f"Found {len(menu_items)} menu items (format: {'new' if is_new_format else 'old'})"
        )

        # Iterate over each menu item and extract relevant information
        for index, item in enumerate(menu_items):
            logger.debug(f"Processing {item.prettify()}")

            # Extract title - handle both old and new formats
            if is_new_format:
                # New format: div.product-title > button
                title_elem = item.find("div", class_="product-title")
                if title_elem and title_elem.find("button"):
                    title_menu = title_elem.find("button").text.strip()
                else:
                    title_menu = ""
            else:
                # Old format: pre-wrap class
                title_elem = item.find(class_="pre-wrap")
                title_menu = title_elem.text.strip() if title_elem else ""

            # Extract description - handle both formats
            if is_new_format:
                # New format: div.push-bottom-xs
                desc_elem = item.find("div", class_="push-bottom-xs")
                description = desc_elem.text.strip() if desc_elem else ""
            else:
                # Old format: product-teaser class
                desc_elem = item.find(class_="product-teaser")
                description = desc_elem.text.strip() if desc_elem else ""

            # Extract price - handle both formats
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

            # If vegetatrische alternative is possible, mark as vegetarian
            if "vegetarische alternative" in description.lower():
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
            menus["glutenfree"].append(glutenfree)
            menus["co2_footprint"].append(co2_footprint)

    df_menus = pd.DataFrame(menus)

    return df_menus

