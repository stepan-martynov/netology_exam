from urllib.parse import urlencode
from pprint import pprint
import sys
import time
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

class CallApi:
    def __init__(self, method, params):
        self.method = method
        self.params = params
        self.params['V'] = 5.65
        self.url_base = 'https://api.vk.com/method/'
        self.error_counter = 0

    def __str__(self):
        print(self.method)

    def response(self):
        try:
            response = requests.get(''.join([self.url_base, self.method]), self.params).json()
            if 'error' in response:
                if response['error']['error_code'] == 6:
                    self.error_counter += 1
                    time.sleep(0.3)
                    response(self)
                elif response['error']['error_code'] == 5:
                    raise Exception(response)
                else:
                    self.error_counter += 1
                if self.error_counter >= 3:
                    raise Exception(response)
        except Exception as vk_api_error:
            print('\nOooops, error: {}'.format(response['error']['error_msg']))
        return response['response']


def get_user_id(user_id, access_token):
    try:
        user_id = int(user_id)
    except ValueError:
        method = 'users.get'
        params = {
            'user_ids': user_id,
            'access_token': access_token
        }
        user_id = CallApi(method, params).response()[0]['uid']
    return user_id


def get_user_groups(user_id, access_token):
    params = {
        'user_id': user_id,
        'access_token': access_token
    }
    method = 'groups.get'

    return set(CallApi(method, params).response())


def get_user_friends_list(user_id, access_token):
    params = {
        'user_id': user_id,
        'access_token': access_token
    }
    method = 'friends.get'
    return CallApi(method, params).response()


def create_list_of_friends_list(user_id, access_token):
    params = {
        'user_id': user_id,
        'access_token': access_token
    }
    method = 'friends.get'
    friends_list = CallApi(method, params).response()
    list_of_friends_lists = list()
    step = 25
    for i in range(0, len(friends_list), step):
        list_of_friends_lists.append(friends_list[i: i + step])
    return list_of_friends_lists


def term_print_dot(all_groups, i, unique_groups_list):
    dots = '.' * int(i % 4) + '.'
    spaces = ' ' * (4 - len(dots))
    sys.stdout.write("\rОсталось {} уникальных групп из {}. /{}/".format(unique_groups_list, all_groups, dots + spaces))


def get_groups_info(access_token, groups_ids):
    print()
    print('Формируем расширенный список уникальных групп')

    method = 'groups.getById'

    params = {
        'group_ids': ','.join(map(str, groups_ids)),
        'fields': 'members_count',
        'access_token': access_token
    }
    groups_info = CallApi(method, params).response()

    print('Записываем в файл')
    with open('groups_info.json', 'w', encoding='utf-8') as f:
        f.write('//Writed at {}. {} unque groups.\n'.format(time.ctime(time.time()), len(groups_info)))
        json.dump(groups_info, f, indent=2, ensure_ascii=False)
    print('Файлы находятся в файле groups_info.json')


def get_and_filter_groups_set(list_of_friends_lists, all_groups, groups_ids, access_token):
    for i, short_friends_list in enumerate(list_of_friends_lists):

        method = 'execute'
        req_code = ',\n'.join(['"{}": API.groups.get({{"user_id": {}}})'.format(i, i) for i in short_friends_list])
        req_code = 'return {%s};' % req_code
        params = {
            'code': req_code,
            'access_token': access_token
        }
        friends_groups_dict = CallApi(method, params).response()

        friends_groups_list = set()
        for uid in friends_groups_dict:
            if friends_groups_dict[uid]:
                friends_groups_list = friends_groups_list | set(friends_groups_dict[uid])
        groups_ids = groups_ids.difference(friends_groups_list)
        groups_list_len = len(groups_ids)
        term_print_dot(all_groups, i, groups_list_len)
    return groups_ids


def main():
    user_id = input('Введите id пользователя, за которым будем следить: ')
    access_token = input('Введите access token: ')

    pprint(time.ctime(time.time()))

    user_id = get_user_id(user_id, access_token)

    groups_ids = get_user_groups(user_id, access_token)

    list_of_friends_lists = create_list_of_friends_list(user_id, access_token)

    all_groups = len(groups_ids)

    groups_ids = get_and_filter_groups_set(list_of_friends_lists, all_groups, groups_ids, access_token)

    get_groups_info(access_token, groups_ids)
    pprint(time.ctime(time.time()))


if __name__ == '__main__':
    main()
