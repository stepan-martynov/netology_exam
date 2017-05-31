from pprint import pprint
import json
from urllib.parse import urlencode
import requests

print('Данные используемые при разработке\n'
      'access_token = 34bb0e68405a6a0a07079cb693d2e3dfb830107ff415677fe8e59b8561d1130018f9a375e2a1db93d20f5\n'
      'user_id = 4058867')
AOUTH_URL = 'https://oauth.vk.com/authorize'
APP_ID = 6052865
V = '5.64'

access_token = input('Введите access token: ')
params = dict()

auth_data = {
    'client_id': APP_ID,
    'display': 'mobile',
    'response_type': 'token',
    'scope': 'friends,groups',
    'v': V
}


# print('?'.join((AOUTH_URL, urlencode(auth_data))))

def get_friend_list(user_id):

    params = {
        'user_id': user_id,
        'access_token': access_token
    }
    response = requests.get('https://api.vk.com/method/friends.get', params)
    user_friend_list = response.json()['response']
    return user_friend_list


def get_user_group_list(user_id):
    # user_id = input('Введите id пользователя, список групп которого хотите посмотреть: ')

    params = {
        'user_id': user_id,
        'access_token': access_token
    }

    response = requests.get('https://api.vk.com/method/groups.get', params)
    user_group_list = response.json()['response']
    return set(user_group_list)


def get_list_friends_groups(friends_list):
    req_link = 'https://api.vk.com/method/execute'

    req_code = ',\n'.join(['"%d": API.groups.get({"user_id": %d})' % (i, i) for i in friends_list])
    req_code = 'return {%s};' % req_code
    req_data = {
        'code': req_code,
        'access_token': access_token
    }

    response = requests.get('?'.join((req_link, urlencode(req_data))))

    friends_groups_dict = response.json()['response']
    friends_groups_list = set()

    for i in friends_groups_dict:
        if friends_groups_dict[i]:
            friends_groups_list = friends_groups_list | set(friends_groups_dict[i])

    return friends_groups_list

def creat_list_of_friends_list(friends_list):
    list_of_friends_lists = list(friends_list[(i * 25):(i * 25 + 25)] for i in range(len(friends_list) // 25 + 1))
    return list_of_friends_lists

def main():

    user_id = input('Введите id пользователя, за которым будем следить: ')
    friends_list = get_friend_list(user_id)
    list_of_friends_lists = creat_list_of_friends_list(friends_list)

    group_list = get_user_group_list(user_id)
    pprint(len(group_list))

    for short_friends_list in list_of_friends_lists:
        friends_groups_list = get_list_friends_groups(short_friends_list)
        group_list = group_list.difference(friends_groups_list)
        pprint(len(group_list))

    pprint(group_list)

if __name__ == '__main__':
    main()