import requests
from  base64 import b64encode
import json

#В этом задании вам требуется отправить POST запрос на 
# следующий https://datasend.webpython.graders.eldf.ru/submissions/1/
#В запросе должен содержаться заголовок Authorization со способом аутентификации 
# Basic логином alladin и паролем opensesame закодированными в base64.
#Authorization: Basic YWxsYWRpbjpvcGVuc2VzYW1l
base_url = 'https://datasend.webpython.graders.eldf.ru/'

param1 = 'submissions/1/'
headers1 = {'Authorization': 'Basic YWxsYWRpbjpvcGVuc2VzYW1l'}
response_1 = json.loads(requests.post(base_url+param1, headers=headers1).text)

# {'password': 'ktotama', 
#  'path': 'submissions/super/duper/secret/', 
#  'login': 'galchonok', 
#  'instructions': 'Сделайте PUT запрос на тот же хост, но на path указанный 
#                   в этом документе c логином и паролем из этого документа. 
#                   Логин и пароль также передайте в заголовке Authorization.'}


auth2 = '{}:{}'.format(response_1['login'], response_1['password']).encode('utf-8')
headers2 = {'Authorization': 'Basic {}'.format(b64encode(auth2).decode())}
response_2 = requests.put(base_url+response_1['path'], headers=headers2)

print(json.loads(response_2.text)['answer'])
# result: 'w3lc0m370ch4p73r4.2'