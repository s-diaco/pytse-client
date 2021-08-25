import bs4
import jdatetime
import pandas as pd
from pytse_client import translations, tse_settings, utils


class PriceAdjust:
    def __init__(self, index: str) -> None:
        self._index = index
        self._price_adj_url = tse_settings.TSE_PRICE_ADJUSTMENT_URL.format(
            self._index)
        self._stock_split_url = tse_settings.TSE_STOCK_SPLIT_URL.format(
            self._index)

    def price_adjustments(self) -> pd.DataFrame:
        """
        Returns the adjustment data for the given index.
        """
        session = utils.requests_retry_session()
        page = session.get(self._price_adj_url, timeout=5)
        session.close()
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        table: bs4.PageElement = soup.find_all("table")[0]
        adjustments_df = utils.get_shareholders_html_table_as_csv(table)
        adjustments_df = adjustments_df.rename(
            columns=translations.ADJUSTMENT_FIELD_MAPPINGS
        )
        adjustments_df["date"] = adjustments_df["j_date"].apply(
            lambda x: jdatetime.date(
                int(x.split("/")[0]),
                int(x.split("/")[1]),
                int(x.split("/")[2])).togregorian()
        )
        return adjustments_df

    def stock_spilts(self):
        """
        Returns the stock split data for the given index.
        """
        session = utils.requests_retry_session()
        page = session.get(self._stock_split_url, timeout=5)
        session.close()
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        table: bs4.PageElement = soup.find_all("table")[0]
        stock_split_df = utils.get_shareholders_html_table_as_csv(table)
        stock_split_df = stock_split_df.rename(
            columns=translations.STOCK_SPLIT_FIELD_MAPPINGS
        )
        stock_split_df["split_coef"] = stock_split_df["shares_after_split"] / \
            stock_split_df["shares_before_split"]
        stock_split_df["date"] = stock_split_df["j_date"].apply(
            lambda x: jdatetime.date(
                int(x.split("/")[0]),
                int(x.split("/")[1]),
                int(x.split("/")[2])).togregorian()
        )
        return stock_split_df

    def calculate_adjusted(self, df, dividends=False):
        # we will go from today to the past
        new = df.sort_index(ascending=False)

        split_coef = new['split coefficient'].shift(1
            ).fillna(1).cumprod()

        for col in ['open', 'high', 'low', 'close']:
            new['adj_' + col] = new[col] / split_coef
        new['adj_volume'] = split_coef * new['volume']

        if dividends:
            new['adj_dividends'] = new['dividend amount'] / split_coef

        return new.sort_index(ascending=True)
