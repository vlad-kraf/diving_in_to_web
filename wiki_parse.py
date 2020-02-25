from bs4 import BeautifulSoup
#import unittest



def cnt_imgs(body):
    imgs = body.find_all('img')
    count = len([x for x in imgs if x.get('width') and int(x.get('width')) >= 200])
    return count    

def max_linkslen(body):
    max_count = 0
    all_links = body.find_all('a')
    for link in all_links:
        current_count = 1
        siblings = link.find_next_siblings()
        for sibling in siblings:
            if sibling.name == 'a':
                current_count += 1
                max_count = max(current_count, max_count)
            else:
                current_count = 0
    return max_count


def cnt_lists(body):
    count = 0
    all_lists = body.find_all(['ul', 'ol'])
    for tag in all_lists:
        if not tag.find_parents(['ul', 'ol']):
            count += 1
    return count

def cnt_headers(body):
    headers = body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    count = 0
    for header in headers:
        children = header.find_all(recursive=False)
        if children:
            children_content = [x.getText() for x in children if x.getText()]
            try:
                first_letter = children_content[0][0]
                if first_letter in 'ETC':
                    count += 1
            except IndexError:
                pass
        else:
            try:
                first_letter = header.getText()[0]
                if first_letter in 'ETC':
                    count += 1
            except IndexError:
                pass
    return count

def parse(path_to_file):  

    with open(path_to_file, encoding='utf-8') as data:
            soup = BeautifulSoup(data, "html.parser")
    body = soup.find(id="bodyContent")  


    imgs = cnt_imgs(body)
    headers = cnt_headers(body)
    linkslen = max_linkslen(body)
    lists = cnt_lists(body)
    return [imgs, headers, linkslen, lists]


#class TestParse(unittest.TestCase):
#    def test_parse(self):
#        test_cases = (
#            ('wiki/Stone_Age', [13, 10, 12, 40]),
#            ('wiki/Brain', [19, 5, 25, 11]),
#            ('wiki/Artificial_intelligence', [8, 19, 13, 198]),
#            ('wiki/Python_(programming_language)', [2, 5, 17, 41]),
#            ('wiki/Spectrogram', [1, 2, 4, 7]),)
#
#        for path, expected in test_cases:
#            with self.subTest(path=path, expected=expected):
#                self.assertEqual(parse(path), expected)


#if __name__ == '__main__':
#    unittest.main()