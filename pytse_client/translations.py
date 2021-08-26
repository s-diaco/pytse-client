HISTORY_FIELD_MAPPINGS = {
    "<DTYYYYMMDD>": "date",
    "<FIRST>": "open",
    "<HIGH>": "high",
    "<LOW>": "low",
    "<LAST>": "close",
    "<VOL>": "volume",
    "<CLOSE>": "adjClose",
    "<OPENINT>": "count",
    "<VALUE>": "value",
    "<OPEN>": "yesterday",
}

SHAREHOLDERS_FIELD_MAPPINGS = {
    "سهامدار/دارنده": "shareholder",
    "سهم": "shares",
    "درصد": "percentage",
    "تغییر": "change",
}

ADJUSTMENT_FIELD_MAPPINGS = {
    "قبل از تعدیل": "price_before_adj",
    "تعدیل شده": "price_after_adj",
    "تاریخ": "jdate"
}

STOCK_SPLIT_FIELD_MAPPINGS = {
    "سهام قبلی": "shares_before_split",
    "سهام جدید": "shares_after_split",
    "تاریخ": "jdate"
}