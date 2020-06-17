import os, requests
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request as ur


destFolder = os.path.dirname(os.path.abspath(__file__))
dict = {}


def convert_float(text):
    zeros = 0
    if text == "N/A":
        floated = text
    else:
        unit = text[-1]
        if "." in text:
            number = text.split('.')
            minus = len(number[1]) - 1
        else:
            minus = 0
        if unit == 'T':
            zeros = '0' * (12 - minus)
        if unit == 'B':
            zeros = '0' * (9 - minus)
        if unit == 'M':
            zeros = '0' * (6 - minus)
        if unit == 'k':
            zeros = '0' * (3 - minus)
        else:
            pass
        floated = float(
            text.replace('T', zeros).replace('B', zeros).replace('M', zeros).replace('k', zeros).replace('.', ''))
    return (floated)


class Scraper:

    # Initializing the scraper with the urls that will be used in the different methods
    def __init__(self, index):
        self.index = index
        self.url_is = 'https://finance.yahoo.com/quote/' + self.index + '/financials?p=' + self.index
        self.url_bs = 'https://finance.yahoo.com/quote/' + self.index + '/balance-sheet?p=' + self.index
        self.url_cf = 'https://finance.yahoo.com/quote/' + self.index + '/cash-flow?p=' + self.index
        self.url_stats = 'https://finance.yahoo.com/quote/' + self.index + '/key-statistics?p=' + self.index
        self.url_pr = 'https://finance.yahoo.com/quote/' + self.index + '/profile?p=' + self.index
        print(self.index)

    # Finding the number of columns in the table
    def nb_cols(self, ls):
        columns = ['ttm', '12/31/2019', '12/31/2018', '12/31/2017', '12/31/2016']
        cols = 1
        for x in columns:
            if x in ls:
                cols += 1
        return cols

    # Getting the soup as a Dataframe
    def get_dataframe(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        soup = soup.find('div', class_="W(100%) Whs(nw) Ovx(a) BdT Bdtc($seperatorColor)")
        ls = ['Label']
        for element in soup.find_all('div'):
            ls.append(element.get('title'))
            ls.append(element.string)
        ls = list(filter(None, ls))
        new_ls = []
        for x in ls:
            try:
                x = float(x.replace(',', ''))
            except Exception as e:
                pass
            finally:
                if x != '-' and x in new_ls and isinstance(x, str):
                    pass
                else:
                    new_ls.append(x)
        print(new_ls)
        cols = self.nb_cols(new_ls)
        data = list(zip(*[iter(new_ls)] * cols))
        result = pd.DataFrame(data[0:])
        result.columns = result.iloc[0]  # Set first row as column names
        result = result.set_index('Label')  # Change 0 index column to Labels
        result.columns = result.iloc[0]  # Name columns to first row of dataframe
        result.drop(result.index[0], inplace=True)  # Drop first index row
        result.index.name = ''  # Remove the index name
        print(result)
        return result

    # Getting the statistics as a Dataframe
    def get_nb(self):
        ls_main = []
        ls_stats = []
        ls_fins = []
        ls_trads = []
        read_data = ur.urlopen(self.url_stats).read()
        soup_stats = BeautifulSoup(read_data, 'html.parser')
        soup_financials = soup_stats.find('div', class_="Fl(start) W(50%) smartphone_W(100%)").find_all('tr')
        soup_trading = soup_stats.find('div', class_="Fl(end) W(50%) smartphone_W(100%)").find_all('tr')

        soup_stats = soup_stats.find('table')
        for stats in soup_stats:
            stats = stats.find_all('td')
            for stat in stats:
                ls_stats.append(stat.text)
                ls_main.append(stat.text)
        # print(ls_stats)

        for fins in soup_financials:
            fins = fins.find_all('td')
            for fin in fins:
                ls_fins.append(fin.text)
                ls_main.append(fin.text)
        # print(ls_fins)

        for trads in soup_trading:
            trads = trads.find_all('td')
            for trad in trads:
                ls_trads.append(trad.text)
                ls_main.append(trad.text)
        # print(ls_trads)

        # print(ls_main)
        stats_data = list(zip(*[iter(ls_main)] * 2))
        all_stats = pd.DataFrame(stats_data[0:])
        all_stats = all_stats.set_index(0)
        all_stats.index.name = ''
        print(all_stats)
        return all_stats

    # Getting profile information as a list
    def get_sect(self):
        countries = ['Spain', 'France', 'United States', 'Germany', 'Belgium']
        ls_sect = []
        read_data = ur.urlopen(self.url_pr).read()
        soup_prof = BeautifulSoup(read_data, 'html.parser')
        soup_prof1 = soup_prof.find('div', class_="asset-profile-container").find_all('span', class_="Fw(600)")
        soup_prof2 = soup_prof.find('div', class_="asset-profile-container").find('p')
        for x in soup_prof1:
            ls_sect.append(x.text)
        for country in countries:
            if country in soup_prof2:
                ls_sect.append(country)
        if len(ls_sect) == 3:
            ls_sect.append('Undefined')
        # print(ls_sect)
        return ls_sect

    # Getting more profile information as a list
    def get_pro(self):
        ls_pro = []
        read_data = ur.urlopen(self.url_pr).read()
        soup_prof = BeautifulSoup(read_data, 'html.parser')
        soup_prof2 = soup_prof.find('table').find_all('tr')
        soup_prof2 = soup_prof2[1].find_all('td')
        for y in soup_prof2:
            ls_pro.append(y.text)
        print(ls_pro)
        return ls_pro

    # Getting all the information into a dictionary
    def get_ratios(self):
        # get datatables
        dtis = self.get_dataframe(self.url_is)
        dtbs = self.get_dataframe(self.url_bs)
        dtcf = self.get_dataframe(self.url_cf)
        dtnb = Scraper(self.index).get_nb()
        dtpro = Scraper(self.index).get_pro()
        dtsect = Scraper(self.index).get_sect()

        # standardize column names (to avoid different dates which are dependent on the company)
        if len(dtis.columns) == 4:
            dtis.columns = ['TTM', 'N-1', 'N-2', 'N-3']
            dtbs.columns = ['N-1', 'N-2', 'N-3']
            dtcf.columns = ['TTM', 'N-1', 'N-2', 'N-3']
        else:
            dtis.columns = ['TTM', 'N-1', 'N-2', 'N-3', 'N-4']
            dtbs.columns = ['N-1', 'N-2', 'N-3', 'N-4']
            dtcf.columns = ['TTM', 'N-1', 'N-2', 'N-3', 'N-4']

        dtnb.columns = ['data']

        ### Valuation Ratios in progress ###

        ## Market Cap: ##
        try:
            Market_Cap = dtnb.at['Market Cap (intraday) 5', 'data']
            dict['Market Cap'] = convert_float(Market_Cap)

            print('Market Cap : ' + str(dict['Market Cap']))
        except KeyError as e:
            dict['Market Cap'] = "NA"
            print('Market Cap : ' + 'KeyError - reason "%s"' % str(e))

        ## Entreprise Value: ##
        try:
            EV = dtnb.at['Enterprise Value 3', 'data']
            dict['Enterprise Value'] = convert_float(EV)
            print('Enterprise Value : ' + str(EV))
        except KeyError as e:
            dict['Enterprise Value'] = "NA"
            print('Enterprise Value : ' + 'KeyError - reason "%s"' % str(e))

        ## P/E ratio: ##
        try:
            PE_ratio = dtnb.at['Trailing P/E ', 'data']
            dict['P/E ratio'] = PE_ratio.replace('.', ',')
            print('P/E ratio : ' + str(PE_ratio))
        except KeyError as e:
            dict['P/E ratio'] = "NA"
            print('P/E ratio : ' + 'KeyError - reason "%s"' % str(e))

        ## PEG ratio: ##
        try:
            PEG_ratio = dtnb.at['PEG Ratio (5 yr expected) 1', 'data']
            dict['PEG ratio'] = PEG_ratio.replace('.', ',')
            print('PEG ratio : ' + str(PEG_ratio))
        except KeyError as e:
            dict['PEG ratio'] = "NA"
            print('PEG ratio : ' + 'KeyError - reason "%s"' % str(e))

        ## P/B ratio: ##
        try:
            PB_ratio = dtnb.at['Price/Book (mrq)', 'data']
            dict['P/B ratio'] = PB_ratio.replace('.', ',')
            print('P/B ratio : ' + str(PB_ratio))
        except KeyError as e:
            dict['P/B ratio'] = "NA"
            print('P/B ratio : ' + 'KeyError - reason "%s"' % str(e))

        ## P/S ratio: ##
        try:
            PS_ratio = dtnb.at['Price/Sales (ttm)', 'data']
            dict['P/S ratio'] = PS_ratio.replace('.', ',')
            print('P/S ratio : ' + str(PS_ratio))
        except KeyError as e:
            dict['P/S ratio'] = "NA"
            print('P/S ratio : ' + 'KeyError - reason "%s"' % str(e))

        ## EV_EBITDA ratio: ##
        try:
            EV_EBITDA = dtnb.at['Enterprise Value/EBITDA 6', 'data']
            dict['EV/EBITDA'] = EV_EBITDA.replace('.', ',')
            print('EV/EBITDA : ' + str(EV_EBITDA))
        except KeyError as e:
            dict['EV/EBITDA'] = "NA"
            print('EV/EBITDA : ' + 'KeyError - reason "%s"' % str(e))

        ## Dividend Yield trailing ratio: ##
        try:
            TA_Dividend_Yield = dtnb.at['Trailing Annual Dividend Yield 3', 'data']
            dict['TA Dividend Yield'] = TA_Dividend_Yield.replace('.', ',')
            print('Trailing Annual Dividend Yield : ' + str(TA_Dividend_Yield))
        except KeyError as e:
            dict['TA Dividend Yield'] = "NA"
            print('Trailing Annual Dividend Yield : ' + 'KeyError - reason "%s"' % str(e))

        ## Dividend Yield over 5 Years: ##
        try:
            _5Y_Dividend_Yield = dtnb.at['5 Year Average Dividend Yield 4', 'data']
            dict['5Y Dividend Yield'] = _5Y_Dividend_Yield.replace('.', ',')
            print('5 Year Average Dividend Yield : ' + str(_5Y_Dividend_Yield))
        except KeyError as e:
            dict['5Y Dividend Yield'] = "NA"
            print('5 Year Average Dividend Yield : ' + 'KeyError - reason "%s"' % str(e))

        ## Dividends Payout : ##

        try:
            Dividend_payout = dtnb.at['Payout Ratio 4', 'data']
            dict['Dividend payout'] = Dividend_payout.replace('.', ',')
            print('Dividend payout : ' + str(Dividend_payout))
        except KeyError as e:
            dict['Dividend payout'] = "NA"
            print('Dividend payout : ' + 'KeyError - reason "%s"' % str(e))
        except ValueError as ve:
            dict['Dividend payout'] = "NA"
            print('Dividend payout : ' + 'ValueError - reason "%s"' % str(ve))

        ### Profitability ratio in progress ###

        ## ROA N-1: ##
        try:
            dict['ROA'] = dtnb.at['Return on Assets (ttm)', 'data']
            print('ROA : ' + str(dict['ROA']) + '%')
        except KeyError as e:
            print('ROA : ' + 'KeyError - reason "%s"' % str(e))

        ## ROE N-1: ##
        try:
            dict['ROE'] = dtnb.at['Return on Equity (ttm)', 'data']
            print('ROE : ' + str(dict['ROE']) + '%')
        except KeyError as e:
            dict['ROE'] = "NA"
            print('ROE : ' + 'KeyError - reason "%s"' % str(e))

        ## Profit Margin: ##
        try:
            Profit_Margin = dtnb.at['Profit Margin ', 'data']
            dict['Profit Margin'] = Profit_Margin.replace('.', ',')
            print('Profit Margin : ' + str(Profit_Margin))
        except KeyError as e:
            dict['Profit Margin'] = "NA"
            print('Profit Margin : ' + 'KeyError - reason "%s"' % str(e))

        ## EPS: ##
        try:
            EPS = dtnb.at['Diluted EPS (ttm)', 'data']
            dict['EPS'] = EPS.replace('.', ',')
            print('EPS : ' + str(EPS))
        except KeyError as e:
            dict['EPS'] = "NA"
            print('EPS : ' + 'KeyError - reason "%s"' % str(e))

        ### Liquidity ratio  OK ###

        # Current Ratio N-1:
        try:
            Current_Ratio = float(dtbs.at['Total Current Assets', 'N-1']) / float(
                dtbs.at['Total Current Liabilities', 'N-1'])
            dict['Current Ratio'] = round(Current_Ratio, 2)
            print('Current Ratio : ' + str(dict['Current Ratio']) + '%')
        except KeyError as e:
            dict['Current Ratio'] = "NA"
            print('Current Ratio : ' + 'KeyError - reason "%s"' % str(e))

        # Current Ratio #
        try:
            Current_Ratio = dtnb.at['Current Ratio (mrq)', 'data']
            dict['Current Ratio mrq'] = Current_Ratio.replace('.', ',')
            print('Current Ratio mrq: ' + str(dict['Current Ratio mrq']))
        except KeyError as e:
            dict['Current Ratio mrq'] = ""
            print('Current Ratio mrq: ' + 'KeyError - reason "%s"' % str(e))

            # Quick Ratio N-1:
        try:
            Quick_Ratio = (float(dtbs.at['Total Current Assets', 'N-1']) - float(dtcf.at['Inventory', 'N-1'])) / float(
                dtbs.at['Total Current Liabilities', 'N-1'])
            dict['Quick Ratio'] = round(Quick_Ratio, 2)
            print('Quick Ratio : ' + str(dict['Quick Ratio']) + '%')
        except ValueError as ve:
            dict['Quick Ratio'] = "NA"
            print('Quick Ratio : ' + 'ValueError - reason "%s"' % str(ve))
        except KeyError as e:
            dict['Quick Ratio'] = "NA"
            print('Quick Ratio : ' + 'KeyError - reason "%s"' % str(e))

        ### Efficiency  ratio  NO ###

        ### Debt Ratio ###

        ## Total Debt: ##
        try:
            Total_Debt = dtnb.at['Total Debt (mrq)', 'data']
            dict['Total Debt'] = convert_float(Total_Debt)
            print('Total Debt : ' + str(Total_Debt))
        except KeyError as e:
            dict['Total Debt'] = "NA"
            print('Total Debt : ' + 'KeyError - reason "%s"' % str(e))
        except ValueError as ve:
            dict['Total Debt'] = "NA"
            print('Total Debt : ' + 'ValueError - reason "%s"' % str(ve))

        ## Debt/Equity: ##
        try:
            Debt_Equity = dtnb.at['Total Debt/Equity (mrq)', 'data']
            dict['Debt/Equity'] = Debt_Equity.replace('.', ',')
            print('Debt/Equity : ' + str(Debt_Equity))
        except KeyError as e:
            dict['Debt/Equity'] = "NA"
            print('Debt/Equity : ' + 'KeyError - reason "%s"' % str(e))

        ### OTHER ###

        ## Revenue ttm : ##
        try:
            Revenue = dtnb.at['Revenue (ttm)', 'data']
            dict['Revenue'] = convert_float(Revenue)
            print('Revenue : ' + str(Revenue))
        except KeyError as e:
            dict['Revenue'] = "NA"
            print('Revenue : ' + 'KeyError - reason "%s"' % str(e))

            ## Revenue per share : ##
        try:
            RPS = dtnb.at['Revenue Per Share (ttm)', 'data']
            dict['RPS'] = RPS.replace('.', ',')
            print('RPS : ' + str(RPS))
        except KeyError as e:
            dict['RPS'] = "NA"
            print('RPS : ' + 'KeyError - reason "%s"' % str(e))

            ## Gross Profit (ttm) : ##
        try:
            Gross_Profit = dtnb.at['Gross Profit (ttm)', 'data']
            dict['Gross Profit'] = convert_float(Gross_Profit)
            print('Gross Profit : ' + str(Gross_Profit))
        except KeyError as e:
            dict['Gross Profit'] = "NA"
            print('Gross Profit : ' + 'KeyError - reason "%s"' % str(e))

            ## EBITDA : ##
        try:
            EBITDAttm = dtnb.at['EBITDA ', 'data']
            dict['EBITDA'] = convert_float(EBITDAttm)
            print('EBITDA : ' + str(EBITDAttm))
        except KeyError as e:
            dict['EBITDA'] = "NA"
            print('EBITDA : ' + 'KeyError - reason "%s"' % str(e))

            ## Beta : ##
        try:
            Beta = dtnb.at['Beta (5Y Monthly) ', 'data']
            dict['Beta'] = Beta.replace('.', ',')
            print('Beta : ' + str(Beta))
        except KeyError as e:
            dict['Beta'] = "NA"
            print('Beta : ' + 'KeyError - reason "%s"' % str(e))

            ## Shares Outstanding : ##
        try:
            Shares_Outstanding = dtnb.at['Shares Outstanding 5', 'data']
            dict['Shares Outstanding'] = convert_float(Shares_Outstanding)
            print('Shares Outstanding : ' + str(Shares_Outstanding))
        except KeyError as e:
            dict['Shares Outstanding'] = "NA"
            print('Shares Outstanding : ' + 'KeyError - reason "%s"' % str(e))

            ## Float : ##
        try:
            Float = dtnb.at['Float ', 'data']
            dict['Float'] = convert_float(Float)
            print('Float : ' + str(Float))
        except KeyError as e:
            dict['Float'] = "NA"
            print('Float : ' + 'KeyError - reason "%s"' % str(e))

        for x in dtis.columns:
            try:
                Net_Income = dtis.at['Normalized Income', x]
                dict['Net Income {}'.format(x)] = Net_Income
                print('Net Income {}'.format(x) + ': ' + str(Net_Income))
            except KeyError as e:
                dict['Net Income {}'.format(x)] = "NA"
                print('Net Income {}'.format(x) + ': ' + 'KeyError - reason "%s"' % str(e))

        for z in dtis.columns:
            try:
                Total_Revenue = dtis.at['Total Revenue', z]
                dict['Total Revenue {}'.format(z)] = Total_Revenue
                print('Total Revenue {}'.format(z) + ': ' + str(Total_Revenue))
            except KeyError as e:
                dict['Total Revenue {}'.format(z)] = "NA"
                print('Total Revenue {}'.format(z) + ': ' + 'KeyError - reason "%s"' % str(e))

        for w in dtis.columns:
            try:
                Gross_Profit = dtis.at['Gross Profit', w]
                dict['Gross Profit {}'.format(w)] = Gross_Profit
                print('Gross Profit {}'.format(w) + ': ' + str(Gross_Profit))
            except KeyError as e:
                dict['Gross Profit {}'.format(w)] = "NA"
                print('Gross Profit {}'.format(w) + ': ' + 'KeyError - reason "%s"' % str(e))

        for v in dtis.columns:
            try:
                Operating_Income = dtis.at['Operating Income', v]
                dict['Operating Income {}'.format(v)] = Operating_Income
                print('Operating Income {}'.format(v) + ': ' + str(Operating_Income))
            except KeyError as e:
                dict['Operating Income {}'.format(v)] = "NA"
                print('Operating Income {}'.format(v) + ': ' + 'KeyError - reason "%s"' % str(e))

        for u in dtis.columns:
            try:
                Income_BefTax = dtis.at['Pretax Income', u]
                dict['Income Before Tax {}'.format(u)] = Income_BefTax
                print('Income Before Tax {}'.format(u) + ': ' + str(Income_BefTax))
            except KeyError as e:
                dict['Income Before Tax {}'.format(u)] = "NA"
                print('Income Before Tax {}'.format(u) + ': ' + 'KeyError - reason "%s"' % str(e))

        for t in dtis.columns:
            try:
                EBITDA = dtis.at['EBITDA', t]
                dict['EBITDA {}'.format(t)] = EBITDA
                print('EBITDA {}'.format(t) + ': ' + str(EBITDA))
            except KeyError as e:
                dict['EBITDA {}'.format(t)] = "NA"
                print('EBITDA {}'.format(t) + ': ' + 'KeyError - reason "%s"' % str(e))

        for y in dtbs.columns:
            try:
                Total_Assets = dtbs.at['Total Assets', y]
                dict['Total Assets {}'.format(y)] = Total_Assets
                print('Total Assets {}'.format(y) + ': ' + str(Total_Assets))
            except KeyError as e:
                dict['Total Assets {}'.format(y)] = "NA"
                print('Total Assets {}'.format(y) + ': ' + 'KeyError - reason "%s"' % str(e))

        for s in dtbs.columns:
            try:
                Total_Liabilities = dtbs.at['Total Liabilities', s]
                dict['Total Liabilities {}'.format(s)] = Total_Liabilities
                print('Total Liabilities {}'.format(s) + ': ' + str(Total_Liabilities))
            except KeyError as e:
                dict['Total Liabilities {}'.format(s)] = "NA"
                print('Total Liabilities {}'.format(s) + ': ' + 'KeyError - reason "%s"' % str(e))

        for r in dtcf.columns:
            try:
                OpCashFlow = dtcf.at['Operating Cash Flow', r]
                dict['Operating Cash Flow {}'.format(r)] = OpCashFlow
                print('Operating Cash Flow {}'.format(r) + ': ' + str(OpCashFlow))
            except KeyError as e:
                dict['Operating Cash Flow {}'.format(r)] = "NA"
                print('Operating Cash Flow {}'.format(r) + ': ' + 'KeyError - reason "%s"' % str(e))

        for q in dtcf.columns:
            try:
                CapEx = dtcf.at['Capital Expenditure', q]
                dict['Capital Expenditure {}'.format(q)] = CapEx
                print('Capital Expenditure {}'.format(q) + ': ' + str(CapEx))
            except KeyError as e:
                dict['Capital Expenditure {}'.format(q)] = "NA"
                print('Capital Expenditure {}'.format(q) + ': ' + 'KeyError - reason "%s"' % str(e))

        for p in dtcf.columns:
            try:
                FreeCashFlow = dtcf.at['Free Cash Flow', p]
                dict['Free Cash Flow {}'.format(p)] = FreeCashFlow
                print('Free Cash Flow {}'.format(p) + ': ' + str(FreeCashFlow))
            except KeyError as e:
                dict['Free Cash Flow {}'.format(p)] = "NA"
                print('Free Cash Flow {}'.format(p) + ': ' + 'KeyError - reason "%s"' % str(e))

        dict['Sector'] = dtsect[0]
        dict['Subsector'] = dtsect[1]
        dict['Empleados'] = dtsect[2].replace(',', '')
        dict['Pais'] = dtsect[3]

        dict['CEO'] = dtpro[0]
        dict['Salario'] = dtpro[2]

        print(dict)
        return dict


# RUN :
Scraper('T').get_ratios()
