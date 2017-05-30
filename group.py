from pprint import pprint
import time
import json
from urllib.parse import urlencode
import requests

AOUTH_URL = 'https://oauth.vk.com/authorize'
APP_ID = 6052865
V = '5.64'
access_token = '34bb0e68405a6a0a07079cb693d2e3dfb830107ff415677fe8e59b8561d1130018f9a375e2a1db93d20f5'
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


# def get_user_group_list(user_id='4058867'):
#     user_id = input('Введите id пользователя, список групп которого хотите посмотреть: ')
#
#     params = {
#         'user_id': user_id,
#         # 'extended': 1,
#         # 'fields': 'name, gid, members_count',
#         'access_token': access_token
#     }
#
#     response = requests.get('https://api.vk.com/method/groups.get', params)
#     user_group_list = response.json()['response']
#     return set(user_group_list)


# pprint(get_user_group_list())
friends_list = get_friend_list()
pprint(len(friends_list))


def get_list_friends_groups(friends_list):
    req_link = 'https://api.vk.com/method/execute'
    friends_groups = set()

    req_code = ',\n'.join(['"%d": API.groups.get({"user_id": %d})' % (i, i) for i in friends_list])
    req_code = 'return {%s};' % req_code
    req_data = {
        'code': req_code,
        'access_token': access_token
    }

    response = requests.get('?'.join((req_link, urlencode(req_data))))
    # return response.json()['response']

    friends_groups_dict = response.json()['response']
    friends_groups_list = set()

    # pprint(friends_groups_dict)
    for i in friends_groups_dict:
        pprint(set(friends_groups_dict[i]))
        # friends_groups_list.union(set(friends_groups_dict[i]))
        # friends_groups_list.union(value)

    return friends_groups_list

pprint(get_list_friends_groups(friends_list[0:24]))


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
