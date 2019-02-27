import requests
import time
import json
import os
from urllib.error import HTTPError


class VkUser:

    vk = 'https://api.vk.com/method/'
    with open(os.path.join('token.json'), encoding='utf-8') as file:
        token = json.load(file)['token']

    def __init__(self, us_id):
        self.us_id = us_id
        self.params = {
            'v': '5.92',
            'access_token': self.token
        }

    def __str__(self):
        return 'https://vk.com/id' + str(self.us_id)

    def vk_request(self, method, user_params):
        try:
            result = requests.post(self.vk + method, params=user_params)
            result.raise_for_status()
            if result.json()['error']['error_code'] == 6:
                time.sleep(0.3)
                return self.vk_request(method, user_params)
        except KeyError:
            return result.json()
        except HTTPError:
            return self.vk_request(method, user_params)

    def get_users(self):
        user_params = self.params.copy()
        user_params.update({'fields': 'counters'})
        return self.vk_request('users.get', user_params)

    def get_friends(self):
        return self.vk_request('friends.get', self.params)

    def get_groups(self, extended='0'):
        user_params = self.params.copy()
        user_params.update({'extended': extended, 'fields': 'members_count, gid'})
        return self.vk_request('groups.get', user_params)

    def get_common_groups(self):
        friends = self.get_friends()['response']['items']
        friends_str = ', '.join([str(i) for i in friends])
        groups = self.get_groups('1')['response']['items']
        pop_list = []
        user_params = self.params.copy()
        user_params.update({'group_id': '', 'user_ids': friends_str, 'extended': '1'})
        for index, group in enumerate(groups):
            user_params['group_id'] = group['id']
            tmp = self.vk_request('groups.isMember', user_params)
            for elem in tmp['response']:
                if elem['member'] == 1:
                    pop_list.append(group['id'])
                    break
            print('Обработана группа {} из {}'.format(index + 1, str(len(groups))))
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
