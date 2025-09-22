from datetime import datetime
import re


def parse_date(date_str):
    if not date_str:
        return datetime.now().date()

    date_str = date_str.strip().lower()
    current_year = datetime.now().year

    months = {
        'янв': 1, 'jan': 1, '01': 1, '1': 1,
        'фев': 2, 'feb': 2, '02': 2, '2': 2,
        'мар': 3, 'mar': 3, '03': 3, '3': 3,
        'апр': 4, 'apr': 4, '04': 4, '4': 4,
        'май': 5, 'may': 5, '05': 5, '5': 5,
        'июн': 6, 'jun': 6, '06': 6, '6': 6,
        'июл': 7, 'jul': 7, '07': 7, '7': 7,
        'авг': 8, 'aug': 8, '08': 8, '8': 8,
        'сен': 9, 'sep': 9, '09': 9, '9': 9,
        'окт': 10, 'oct': 10, '10': 10,
        'ноя': 11, 'nov': 11, '11': 11,
        'дек': 12, 'dec': 12, '12': 12
    }

    match = re.match(r'(\d{1,2})[\.\-\s]+(.+)', date_str)
    if match:
        day = int(match.group(1))
        month_part = match.group(2)

        for month_key, month_num in months.items():
            if month_part.startswith(month_key):
                year_match = re.search(r'(\d{2,4})$', month_part)
                year = int(year_match.group(1)) if year_match else current_year

                if year_match and year < 100:
                    year += 2000 if year < 50 else 1900

                try:
                    return datetime(year, month_num, day).date()
                except:
                    pass

    match = re.match(r'([а-яa-z]+)[\.\-\s]+(\d{1,2})', date_str)
    if match:
        month_part = match.group(1)
        day = int(match.group(2))

        for month_key, month_num in months.items():
            if month_part.startswith(month_key):
                try:
                    return datetime(current_year, month_num, day).date()
                except:
                    pass

    return datetime.now().date()
