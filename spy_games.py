import requests
import time
import json
import os
from requests import HTTPError


class VkUser:

    vk = 'https://api.vk.com/method/'
    with open(os.path.join('tok.json'), encoding='utf-8') as file:
        token = json.load(file)['token']
    vk_timeout = 0.3
    TOO_MANY_REQUESTS = 6

    def __init__(self, user_id):
        self.params = {
            'v': '5.92',
            'access_token': self.token
        }
        user_params = self.params.copy()
        user_params.update({'user_ids': user_id, 'screen_name': user_id})
        self.user_id = self.vk_request('users.get', user_params)['response'][0]['id']

    def __str__(self):
        return 'https://vk.com/id' + str(self.user_id)

    def vk_request(self, method, user_params, max_iter=20):
        try:
            if max_iter == 0:
                print('Превышен лимит ошибочных HTTP-запросов')
            result = requests.post(self.vk + method, params=user_params)
            result.raise_for_status()
            if 'response' in result.json():
                return result.json()
            elif result.json()['error']['error_code'] == self.TOO_MANY_REQUESTS:
                print('таймаут запроса {} сек.'.format(self.vk_timeout))
                time.sleep(self.vk_timeout)
                return self.vk_request(method, user_params)

        except HTTPError as err:
            print('Ошибка HTTP-запроса {}, попыток осталось: {}'.format(str(err.response)[11:14], max_iter))
            return self.vk_request(method, user_params, max_iter-1)

    def get_friends(self):
        user_params = self.params.copy()
        user_params.update({'user_id': self.user_id})
        return self.vk_request('friends.get', user_params)

    def get_groups(self, extended='0'):
        user_params = self.params.copy()
        user_params.update({'user_id': self.user_id, 'extended': extended, 'fields': 'members_count, gid'})
        return self.vk_request('groups.get', user_params)

    def get_common_groups(self):
        friends = self.get_friends()['response']['items']
        groups = self.get_groups('1')['response']['items']
        pop_list = []
        user_params = self.params.copy()
        user_params.update({'group_id': '', 'user_ids': '', 'extended': '1'})

        for index, group in enumerate(groups):
            user_params['group_id'] = group['id']
            max_len = 200
            for lst in [friends[i:i + max_len] for i in range(0, len(friends), max_len)]:
                friends_str = ', '.join([str(i) for i in lst])
                user_params['user_ids'] = friends_str
                tmp = self.vk_request('groups.isMember', user_params)
                for elem in tmp['response']:
                    if elem['member'] == 1:
                        pop_list.append(group['id'])
                        break
            print('Обработана группа {} из {}'.format(index + 1, len(groups)))
        non_unique_groups_set = set(pop_list)
        groups = [g for g in groups if g['id'] not in non_unique_groups_set]
        groups_list = []
        for group in groups:
            groups_list.append({'name': group['name'], 'gid': group['id'], 'members_count': group['members_count']})

        with open(os.path.join('test.json'), 'w') as file:
            json.dump(groups_list, file)
        return 'Готово'


user1 = VkUser(171691064)
print(user1.get_common_groups())
