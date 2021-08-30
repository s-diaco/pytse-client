import bs4
import jdatetime
import pandas as pd
import numpy as np
from pytse_client import translations, tse_settings, utils


class PriceAdjust:
    def __init__(self, index: str) -> None:
        self._index = index
        self._price_adj_url = tse_settings.TSE_PRICE_ADJUSTMENT_URL.format(
            self._index)
        self._stock_split_url = tse_settings.TSE_STOCK_SPLIT_URL.format(
            self._index)

    def adj_prices(
        self, df, adj_by_dividend, adj_by_split) -> pd.DataFrame:
        if adj_by_split:
            split_df = self.stock_spilts()
            split_df.index = split_df.date
            df.index = df.date
            df = df.merge(
                split_df[['split_coef']],
                left_index=True,
                right_index=True, how='outer')
            df = df.drop(columns=['date'])
            df['split_coef'] = df['split_coef'].fillna(1)
            df = self.adjust_splits(df)
            df = df.reset_index()
        if adj_by_dividend:
            divid_df = self.price_adjustments()
            divid_df.index = divid_df.date
            df.index = df.date
            df = df.merge(
                divid_df[['adj_diff']],
                left_index=True,
                right_index=True, how='outer')
            df = df.drop(columns=['date'])
            df['adj_diff'] = df['adj_diff'].fillna(0)
            df = self.calculate_adjusted(df)
            df = df.reset_index()
        return df

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
        adjustments_df["adj_diff"] = adjustments_df["price_before_adj"] - \
            adjustments_df["price_after_adj"]
        adjustments_df["date"] = adjustments_df["jdate"].apply(
            lambda x: np.datetime64(jdatetime.date(
                int(x.split("/")[0]),
                int(x.split("/")[1]),
                int(x.split("/")[2])).togregorian())
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
        stock_split_df["date"] = stock_split_df["jdate"].apply(
            lambda x: np.datetime64(jdatetime.date(
                int(x.split("/")[0]),
                int(x.split("/")[1]),
                int(x.split("/")[2])).togregorian())
        )
        return stock_split_df

    def adjust_splits(self, df):
        # we will go from today to the past
        new = df.sort_index(ascending=False)

        split_coef = new['split_coef'].shift(1
            ).fillna(1).cumprod()

        for col in ['open', 'high', 'low', 'close']:
            new['adj_' + col] = new[col] / split_coef
        new['adj_volume'] = split_coef * new['volume']

        return new.sort_index(ascending=True)

    def calculate_adjusted(self, df):
        new = df.sort_index(ascending=False)

        split_coef = new['adj_diff'].shift(1
            ).fillna(0).cumsum()

        for col in ['open', 'high', 'low', 'close']:
            new['adj_2_' + col] = new[col] - split_coef
        new['adj_volume'] = split_coef * new['volume']

        return new.sort_index(ascending=True)
