from pprint import pprint
import sys
import time
from urllib.parse import urlencode
import requests

AOUTH_URL = 'https://oauth.vk.com/authorize'
APP_ID = 6052865
V = '5.64'

params = dict()

auth_data = {
    'client_id': APP_ID,
    'display': 'mobile',
    'response_type': 'token',
    'scope': 'friends,groups',
    'v': V
}


# print('?'.join((AOUTH_URL, urlencode(auth_data))))

def get_friend_list(user_id, access_token):
    params = {
        'user_id': user_id,
        'access_token': access_token
    }
    response = requests.get('https://api.vk.com/method/friends.get', params)
    user_friend_list = response.json()['response']
    return user_friend_list


def get_user_group_list(user_id, access_token):
    # user_id = input('Введите id пользователя, список групп которого хотите посмотреть: ')

    params = {
        'user_id': user_id,
        'access_token': access_token
    }

    response = requests.get('https://api.vk.com/method/groups.get', params)
    user_group_list = response.json()['response']
    return set(user_group_list)


def get_list_friends_groups(friends_list, access_token):
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


def term_print_dot(all_groups, i, unique_groups_list):
    hashes = '.' * int(i % 4) + '.'
    spaces = ' ' * (4 - len(hashes))
    pr_br = hashes + spaces
    sys.stdout.write("\rОсталось {} уникальных групп из {}. /{}/".format(unique_groups_list, all_groups, pr_br))
    # sys.stdout.flush()

def main():
    user_id = input('Введите id пользователя, за которым будем следить: ')
    access_token = input('Введите access token: ')
    friends_list = get_friend_list(user_id, access_token)
    list_of_friends_lists = creat_list_of_friends_list(friends_list)
    group_list = get_user_group_list(user_id, access_token)
    all_groups = len(group_list)

    for i, short_friends_list in enumerate(list_of_friends_lists):
        friends_groups_list = get_list_friends_groups(short_friends_list, access_token)
        group_list = group_list.difference(friends_groups_list)
        unique_groups_list = len(group_list)
        term_print_dot(all_groups, i, unique_groups_list)
        time.sleep(0.3)
    pprint(' ')
    pprint('Список уникальных групп:')
    pprint(group_list)


if __name__ == '__main__':
    main()
