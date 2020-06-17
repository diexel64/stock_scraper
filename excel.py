from scrape import Scraper
import os
import pandas as pd
from pandas import ExcelWriter


destFolder = os.path.dirname(os.path.abspath(__file__))


class Excel:

    def __init__(self, index):
        self.index = index
        self.dict = Scraper(index).get_ratios()
        self.file = destFolder + '\\AllStocks.xlsx'
        self.df_allstocks = pd.ExcelFile(self.file).parse("Sheet1")
        self.row = {
            'Index': self.index,
            'Sector': self.dict['Sector'],
            'Subsector': self.dict['Subsector'],
            'CEO': self.dict['CEO'],
            'Salario': self.dict['Salario'],
            'Empleados': self.dict['Empleados'],
            'Pais': self.dict['Pais'],
            'Market Cap': self.dict['Market Cap'],
            'P/E ratio': self.dict['P/E ratio'],
            'PEG ratio': self.dict['PEG ratio'],
            'EV/EBITDA': self.dict['EV/EBITDA'],
            'P/B ratio': self.dict['P/B ratio'],
            'P/S ratio': self.dict['P/S ratio'],
            'TA Dividend Yield': self.dict['TA Dividend Yield'],
            '5Y Dividend Yield': self.dict['5Y Dividend Yield'],
            'Dividend payout': self.dict['Dividend payout'],
            'ROA': self.dict['ROA'],
            'EPS': self.dict['EPS'],
            'ROE': self.dict['ROE'],
            'Profit Margin': self.dict['Profit Margin'],
            'Revenue': self.dict['Revenue'],
            'RPS': self.dict['RPS'],
            'Gross Profit': self.dict['Gross Profit'],
            'EBITDA': self.dict['EBITDA'],
            'Current Ratio': self.dict['Current Ratio'],
            'Current Ratio mrq': self.dict['Current Ratio mrq'],
            'Quick Ratio': self.dict['Quick Ratio'],
            'Debt/Equity': self.dict['Debt/Equity'],
            'Total Debt': self.dict['Total Debt'],
            'Enterprise Value': self.dict['Enterprise Value'],
            'Shares Outstanding': self.dict['Shares Outstanding'],
            'Float': self.dict['Float'],
            'Beta': self.dict['Beta'],
            'Total Revenue N-1': self.dict['Total Revenue N-1'],
            'Total Revenue N-2': self.dict['Total Revenue N-2'],
            'Total Revenue N-3': self.dict['Total Revenue N-3'],
            'Gross Profit N-1': self.dict['Gross Profit N-1'],
            'Gross Profit N-2': self.dict['Gross Profit N-2'],
            'Gross Profit N-3': self.dict['Gross Profit N-3'],
            'Operating Income N-1': self.dict['Operating Income N-1'],
            'Operating Income N-2': self.dict['Operating Income N-2'],
            'Operating Income N-3': self.dict['Operating Income N-3'],
            'Income Before Tax N-1': self.dict['Income Before Tax N-1'],
            'Income Before Tax N-2': self.dict['Income Before Tax N-2'],
            'Income Before Tax N-3': self.dict['Income Before Tax N-3'],
            'Net Income N-1': self.dict['Net Income N-1'],
            'Net Income N-2': self.dict['Net Income N-2'],
            'Net Income N-3': self.dict['Net Income N-3'],
            'EBITDA N-1': self.dict['EBITDA N-1'],
            'EBITDA N-2': self.dict['EBITDA N-2'],
            'EBITDA N-3': self.dict['EBITDA N-3'],
            'Total Assets N-1': self.dict['Total Assets N-1'],
            'Total Assets N-2': self.dict['Total Assets N-2'],
            'Total Assets N-3': self.dict['Total Assets N-3'],
            'Total Liabilities N-1': self.dict['Total Liabilities N-1'],
            'Total Liabilities N-2': self.dict['Total Liabilities N-2'],
            'Total Liabilities N-3': self.dict['Total Liabilities N-3'],
            'Operating Cash Flow N-1': self.dict['Operating Cash Flow N-1'],
            'Operating Cash Flow N-2': self.dict['Operating Cash Flow N-2'],
            'Operating Cash Flow N-3': self.dict['Operating Cash Flow N-3'],
            'Capital Expenditure N-1': self.dict['Capital Expenditure N-1'],
            'Capital Expenditure N-2': self.dict['Capital Expenditure N-2'],
            'Capital Expenditure N-3': self.dict['Capital Expenditure N-3'],
            'Free Cash Flow N-1': self.dict['Free Cash Flow N-1'],
            'Free Cash Flow N-2': self.dict['Free Cash Flow N-2'],
            'Free Cash Flow N-3': self.dict['Free Cash Flow N-3']
            }
        self.df_allstocks = self.df_allstocks.append(self.row, ignore_index=True)

    def append_df_to_excel(self):
        writer = ExcelWriter(self.file)
        self.df_allstocks = self.df_allstocks.drop_duplicates(subset='Index', keep='first')
        self.df_allstocks.to_excel(writer, sheet_name='Sheet1', index = False)
        writer.save()


# Run program :

if __name__ == '__main__':
    companies = ['T', 'ORA.PA', 'TSLA', 'IBE.MC']
    for c in companies:
        Excel(c).append_df_to_excel()
