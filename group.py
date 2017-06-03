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

def call_api(method, params):
    url_base = 'https://api.vk.com/method/'

    resp = requests.get(''.join([url_base, method]), params).json()
    if 'error' in resp.keys():
        with open('api_error.log', 'a') as f:
            f.write(
                '{}: {} // {}\n'.format(time.ctime(time.time()), resp['error']['error_msg'], ' '.join(params.values())))
        time.sleep(0.4)
        # call_api(req_url, params, **code_str)
    resp = resp['response']
    return resp


def create_list_of_friends_list(friends_list):
    list_of_friends_lists = list()
    step = 25
    for i in range(0, len(friends_list), step):
        list_of_friends_lists.append(friends_list[i: i + step])
    return list_of_friends_lists


def term_print_dot(all_groups, i, unique_groups_list):
    dots = '.' * int(i % 4) + '.'
    spaces = ' ' * (4 - len(dots))
    sys.stdout.write("\rОсталось {} уникальных групп из {}. /{}/".format(unique_groups_list, all_groups, dots + spaces))


def main():
    with open('api_error.log', 'w') as f:
        f.write('Started at {}\n'.format(time.ctime(time.time())))

    user_id = input('Введите id пользователя, за которым будем следить: ')
    access_token = input('Введите access token: ')

    pprint(time.ctime(time.time()))
    try:
        user_id = int(user_id)
    except ValueError:
        method = 'users.get'
        params = {
            'user_ids': user_id,
            'access_token': access_token
        }
        user_id = call_api(method, params)[0]['uid']

    params = {
        'user_id': user_id,
        'access_token': access_token
    }
    method = 'friends.get'
    friends_list = call_api(method, params)

    list_of_friends_lists = create_list_of_friends_list(friends_list)

    params = {
        'user_id': user_id,
        'access_token': access_token
    }
    method = 'groups.get'

    groups_ids = set(call_api(method, params))
    all_groups = len(groups_ids)

    for i, short_friends_list in enumerate(list_of_friends_lists):

        method = 'execute'
        req_code = ',\n'.join(['"{}": API.groups.get({{"user_id": {}}})'.format(i, i) for i in short_friends_list])
        req_code = 'return {%s};' % req_code
        params = {
            'code': req_code,
            'access_token': access_token
        }
        friends_groups_dict = call_api(method, params)

        friends_groups_list = set()
        for uid in friends_groups_dict:
            if friends_groups_dict[uid]:
                friends_groups_list = friends_groups_list | set(friends_groups_dict[uid])
        groups_ids = groups_ids.difference(friends_groups_list)
        groups_list_len = len(groups_ids)
        term_print_dot(all_groups, i, groups_list_len)
        time.sleep(0.3)
    print()
    print('Формируем расширенный список уникальных групп')

    method = 'groups.getById'

    params = {
        'group_ids': ','.join(map(str, groups_ids)),
        'fields': 'members_count',
        'access_token': access_token
    }
    groups_info = call_api(method, params)

    print('Записываем в файл')
    with open('groups_info.json', 'w', encoding='utf-8') as f:
        f.write('Writed at {}. {} unque groups.\n'.format(time.ctime(time.time()), len(groups_info)))
        json.dump(groups_info, f, indent=2, ensure_ascii=False)
    print('Файлы находятся в файле groups_info.json')
    pprint(time.ctime(time.time()))


if __name__ == '__main__':
    main()
