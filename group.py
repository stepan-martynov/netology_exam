from pprint import pprint
import time
import json
from urllib.parse import urlencode
import requests

AOUTH_URL = 'https://oauth.vk.com/authorize'
APP_ID = 6052865
V = '5.64'
access_token = '7f0229d55a7a58558d9157d39ee26dbce714364b00d2d01564e287729baa1583f33d6c86b6cb685bcd64d'
params = dict()

auth_data = {
    'client_id': APP_ID,
    'display': 'mobile',
    'response_type': 'token',
    'scope': 'friends,groups',
    'v': V
}


# print('?'.join((AOUTH_URL, urlencode(auth_data))))

def get_friend_list(user_id='4058867'):
    user_id = input('Введите id пользователя, за которым будем следить: ')

    params = {
        'user_id': user_id,
        'access_token': access_token
    }
    response = requests.get('https://api.vk.com/method/friends.get', params)
    user_friend_list = response.json()['response']
    return user_friend_list


def get_user_group_list(user_id='4058867'):
    user_id = input('Введите id пользователя, список групп которого хотите посмотреть: ')

    params = {
        'user_id': user_id,
        # 'extended': 1,
        # 'fields': 'name, gid, members_count',
        'access_token': access_token
    }

    response = requests.get('https://api.vk.com/method/groups.get', params)
    user_group_list = response.json()['response']
    return set(user_group_list)


# pprint(get_user_group_list())
friends_list = get_friend_list()
pprint(len(friends_list))


def get_list_friends_groups(friends_list):
    req_link = 'https://api.vk.com/method/execute'
    friends_groups = set()

    req_code = ' '.join(
        ['return', ',\n'.join(['"%d": API.groups.get({"user_id": %d})' % (i, i) for i in friends_list])])

    req_data = {
        'code': req_code,
        'acess_token': access_token
    }

    response = requests.get('?'.join((req_link, urlencode(req_data))))
    pprint(response.json())
    return response.json()['response']

pprint(get_list_friends_groups(friends_list[0:24]))



    # def get_friends_list_execute(user_friend_list, count=3):
    #     req_url = 'https://api.vk.com/method/execute'
    #     inner_code = ',\n'.join(
    #         ['"%d": API.friends.get({"user_id": %d, "count": %d})' % (i, i, count) for i in user_friend_list])
    #     req_code = 'return {%s};' % inner_code
    #     req_data = {
    #         'code': req_code,
    #         'access_token': access_token
    #     }
    #     response = requests.get('?'.join((req_url, urlencode(req_data))))
    #     return response.json()['response']
    #
    #
    # def spt_lst_by_25_elem(user_friend_list):
    #     return list(user_friend_list[(i * 25):(i * 25 + 25)] for i in range(len(user_friend_list) // 25 + 1))
    #
    #
    # def main():
    #     user_id, user_friend_list = get_friend_list()
    #     with open('full_list.txt', 'w') as f:
    #         f.write('%s\n' % user_id)
    #     lst_of_users_lists = spt_lst_by_25_elem(user_friend_list)
    #
    #     full_list_of_lists = dict()
    #     count = int(input('Введите ограничение для списка друзей друзей: '))
    #     for users_short_list in lst_of_users_lists:
    #         short_dict = get_friends_list_execute(users_short_list, count)
    #         full_list_of_lists.update(short_dict)
    #
    #     with open('full_list.txt', 'a') as f:
    #         json.dump(full_list_of_lists, f, indent=4)
    #     print(len(full_list_of_lists))
    #
    #
    # if __name__ == '__main__':
    # main()
