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

## Mattermost webhook url

You need to set the MATTERMOST_WEBHOOK_URL environment variable to your Mattermost incoming webhook url.


## How to run

First install the mensabot package. You can do this via pip:

```
pip install .
```

Then you can run the script via:

```
python -m mensabot
```

You can run this daily via a cron job. 
You can also use the provided app.py script to run it every weekday at 14:00.

## Docker

Alternativatively, you can run it in a Docker container.

Build the Docker image:

```
docker build -t mensabot .
```

Run the Docker container:

```
docker run mensabot
```
