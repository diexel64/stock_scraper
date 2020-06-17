# stock_scraper
A program to scrape financial data from Yahoo Finance.

1. Purpose

This program can be used to gather data on any company listed in Yahoo Finance, mostly from Financials and Statistics tabs. This is what the file Scrape.py does.
This data can then be easily stored in an Excel spreadsheet thanks to the Excel.py file for further analysis.

2. Making it run

The program uses some common libraries that do not come installed by default in Python, namely pandas, bs4, requests, openpyxl
It is possible to install them by using the pip install command.

3. Run Scrape.py

To run the program, just call : Scraper(yahooTicker, 0).get_ratios()
e.g. : Scraper('T', 0).get_ratios()

4. Run Excel.py

