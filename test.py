from bs4 import BeautifulSoup
from decimal import Decimal
import requests


def convert(amount, cur_from, cur_to, date):
    response = requests.get("http://www.cbr.ru/scripts/XML_daily.asp?", params={'date_req': date})
    soup = BeautifulSoup(response.content,'lxml')
    rates = { x.charcode.string: (Decimal(x.value.string.replace(',', '.')), int(x.nominal.string)) for x in soup('valute')}
 #   rates['RUR'] = (Decimal(1), 1)

    result = amount * rates[cur_from][1] * rates[cur_to][0] / rates[cur_from][0] / rates[cur_to][1]
    result = result.quantize(Decimal('.0001'))

    return result

if __name__ == "__main__":
    print(convert(50,'KRW','USD','21/02/2020'))
