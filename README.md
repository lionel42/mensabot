# mensabot


This is a script that can be run to parse menus from the SV Mensa. 

It does the following:

* Download the daily menu from html in the SV Mensa website
* Parse the html to extract the menu items
* Saves the menus in csv files
* Select only the vegetarian and vegan options (since we don't want to kill animals)
* Formats the menus as markdown
* Sends the menus to a Mattermost channel

If you want to use this scripts, or parts of it, we can adapt it. 
Maybe we can also do a python package in case you are interested in that.
Just open an issue or a pull request and we can discuss it.

## Output example

### Vegi menus today 

 🥑🍆🥔🥕🌽🌶️ 🫑 🥒🥬🥦🧄🧅🥜 🫘 🌰🍄‍🟫  

| Restaurant   | Price     | Vegan   | Title       | Description                                                                                                                                    |
|:-------------|:----------|:--------|:------------|:-----------------------------------------------------------------------------------------------------------------------------------------------|
| Empa         | 11.50 CHF | True    | Buddha Bowl | mit Quinoa, Randen Falafel, Zucchetti, Sesam  Rettich Pickles, Lattich, Cherrytomaten und Olivenöl-Zitronen Dressing , Tagessalat und 1dl Saft |
| Eawag        | 13.70 CHF | True    | Korma Curry | mit geräucherten Tofu, rotem Jasminreis und   Tagessalat oder Tagessuppe                                                                       |

## How to run

I run this daily via a cron job. 
We might create a CLI in the future, if anyone is interested in that, so that we can 
add options easily and put the configuration in a separate file.