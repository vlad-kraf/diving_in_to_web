from bs4 import BeautifulSoup
from decimal import Decimal


def convert(amount, cur_from, cur_to, date, requests):
    response = requests.get("http://www.cbr.ru/scripts/XML_daily.asp?", params={'date_req': date})
    soup = BeautifulSoup(response.content,'lxml')
    rates = { x.charcode.string: (Decimal(x.value.string.replace(',', '.')), int(x.nominal.string)) for x in soup('valute')}
    rates['RUR'] = (Decimal(1), 1)

    result = amount * rates[cur_from][0] * rates[cur_to][1] / rates[cur_from][1] / rates[cur_to][0]
    result = result.quantize(Decimal('.0001'))

    return result  # не забыть про округление до 4х знаков после запятой
