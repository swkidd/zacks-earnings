import pandas as pd
from dateutil import parser
import requests
import io

class ZacksEarnings:
    @staticmethod
    def get_next_earnings_estimate(symbol):
        _ZACKS_URL = 'https://www.zacks.com/stock/quote/%s/detailed-estimates'
        _ZACKS_ERROR_MSG = 'Unable to get next earnings date for %s from Zacks.'
        _ZACKS_HEADER = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'}
        try:
            r = requests.get(_ZACKS_URL % symbol, headers=_ZACKS_HEADER)
            next_earnings_table = pd.read_html(r.content, match="Next Report Date", index_col=0, parse_dates=True)
            if len(next_earnings_table) == 0:
                raise Exception(_ZACKS_ERROR_MSG % symbol)
            return [parser.parse(next_earnings_table[0].loc['Next Report Date'].values[0], fuzzy=True)]
        except:
            print('error %s' % symbol)
        return []

    @staticmethod
    def earnings_by_date(date):
        site = 'https://www.zacks.com/research/earnings/earning_export.php?timestamp=%d&tab_id=1'
        header = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        raw_bytes = requests.get(site % int(date.timestamp()), headers=header).content
        dfs = pd.read_csv(io.StringIO(raw_bytes.decode('utf-8')), sep='\t')
        return dfs

if __name__ == "__main__":
    earnings = ZacksEarnings.earnings_by_date(parser.parse('Aug 12, 2017')) 
    print('Aug 12, 2017 Earnings')
    print(earnings)

    aapl_next_earnings_date = ZacksEarnings.get_next_earnings_estimate('aapl')
    if len(aapl_next_earnings_date) > 0:
        print('Apple (AAPL) Estimated Earnings Date: ', aapl_next_earnings_date[0].strftime("%Y-%m-%d"))