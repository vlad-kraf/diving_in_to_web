import requests
import json
from datetime import date
from collections import Counter, OrderedDict

YEAR = date.today().year
ACCESS_TOKEN = '17da724517da724517da72458517b8abce117da17da72454d235c274f1a2be5f45ee711'
V = '5.71'


def get_usr_id(uid):

    if type(uid) == str:
        user = requests.get("https://api.vk.com/method/users.get", params={
        'access_token': ACCESS_TOKEN,
        'user_ids': uid,
        'v': V
        })
        user_id = json.loads(user.text)['response'][0]['id']
    elif type(uid) == int:
        user_id = uid
    return user_id

def get_friends (uid):

    user_id = get_usr_id(uid)
    friends = requests.get("https://api.vk.com/method/friends.get", params= {
        'access_token': ACCESS_TOKEN,
        'user_id': user_id,
        'v': V,
        'fields': 'bdate'
    })
    return friends

def calc_age(uid):

    friends = get_friends(uid)
    friends = json.loads(friends.text)['response']['items']

    friends_age = dict()
    for friend in friends:
        if "bdate" in friend and len(friend["bdate"].split(".")) == 3:
            friends_age[friend["id"]] = YEAR - int(friend["bdate"].split(".")[2])

   # count same age entries 
    counts = Counter(v for k, v in friends_age.items())
    result = [(k, v) for k, v in counts.items()]
    sorted_result = sorted(result, key=lambda v: (v[1], -v[0]), reverse=True)

    return sorted_result



if __name__ == '__main__':
    res = calc_age('reigning')
    print(res)