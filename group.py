from pprint import pprint
import sys
import time
from urllib.parse import urlencode

import requests
import json


# AOUTH_URL = 'https://oauth.vk.com/authorize'
# APP_ID = 6052865
# V = '5.64'
#
# params = dict()
#
# auth_data = {
#     'client_id': APP_ID,
#     'display': 'mobile',
#     'response_type': 'token',
#     'scope': 'friends,groups',
#     'v': V
# }
#
# print('?'.join((AOUTH_URL, urlencode(auth_data))))

def simple_request_to_api(req_url, params):
    resp = requests.get(req_url, params).json()
    if 'error' in resp.keys():
        with open('api_error.log', 'a') as f:
            f.write(
                '{}: {} // {}\n'.format(time.ctime(time.time()), resp['error']['error_msg'], ' '.join(params.values())))
        time.sleep(0.4)
        simple_request_to_api(req_url, params, **code_str)
    resp = resp['response']
    return resp


def get_list_friends_groups(friends_list, access_token):
    req_link = 'https://api.vk.com/method/execute'

    req_code = ',\n'.join(['"%d": API.groups.get({"user_id": %d})' % (i, i) for i in friends_list])
    req_code = 'return {%s};' % req_code
    req_data = {
        'code': req_code,
        'access_token': access_token
    }

    response = requests.get(req_link, req_data)

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
    dots = '.' * int(i % 4) + '.'
    spaces = ' ' * (4 - len(dots))
    sys.stdout.write("\rОсталось {} уникальных групп из {}. /{}/".format(unique_groups_list, all_groups, dots + spaces))


def main():
    with open('api_error.log', 'w') as f:
        f.write('Started at {}\n'.format(time.ctime(time.time())))
    access_token = input('Введите access token: ')
    user_id = input('Введите id пользователя, за которым будем следить: ')
    pprint(time.ctime(time.time()))
    try:
        user_id = int(user_id)
    except ValueError:
        req_url = 'https://api.vk.com/method/users.get'
        params = {
            'user_ids': user_id,
            'access_token': access_token
        }
        user_id = simple_request_to_api(req_url, params)[0]['uid']

    params = {
        'user_id': user_id,
        'access_token': access_token
    }
    req_url = 'https://api.vk.com/method/friends.get'
    friends_list = simple_request_to_api(req_url, params)

    list_of_friends_lists = creat_list_of_friends_list(friends_list)

    params = {
        'user_id': user_id,
        'access_token': access_token
    }
    req_url = 'https://api.vk.com/method/groups.get'

    groups_ids = set(simple_request_to_api(req_url, params))
    all_groups = len(groups_ids)

    for i, short_friends_list in enumerate(list_of_friends_lists):
        friends_groups_list = get_list_friends_groups(short_friends_list, access_token)
        groups_ids = groups_ids.difference(friends_groups_list)
        groups_list_len = len(groups_ids)
        term_print_dot(all_groups, i, groups_list_len)
        time.sleep(0.3)
    print()
    print('Формируем расширенный список уникальных групп')

    req_url = 'https://api.vk.com/method/groups.getById'

    params = {
        'group_ids': ','.join(map(str, groups_ids)),
        'fields': 'members_count',
        'access_token': access_token
    }
    groups_info = simple_request_to_api(req_url, params)

    print('Записываем в файл')
    with open('groups_info.json', 'w', encoding='utf-8') as f:
        f.write('Writed at {}. {} unque groups\n'.format(time.ctime(time.time()), len(groups_info)))
        json.dump(groups_info, f, indent=2, ensure_ascii=False)
    print('Файлы находятся в файле groups_info.json')
    pprint(time.ctime(time.time()))


if __name__ == '__main__':
    main()
