import requests
import time
import json
import os


class VkUser:

    vk = 'https://api.vk.com/method/'
    token = 'ed1271af9e8883f7a7c2cefbfddfcbc61563029666c487b2f71a5227cce0d1b533c4af4c5b888633c06ae'

    def __init__(self, us_id):
        self.us_id = us_id
        self.params = {
            'v': '5.92',
            'access_token': self.token
        }

    def __and__(self, other):
        us_params = self.params
        us_params.update({'target_uid': other.us_id})
        mut_friends = requests.post(self.vk + 'friends.getMutual', params=us_params).json()['response']
        user_list = []
        for friend in mut_friends:
            user_list.append(str(VkUser(friend)))
        return user_list

    def __str__(self):
        return 'https://vk.com/id' + str(self.us_id)

    def get_users(self):
        us_params = self.params
        us_params.update({'fields': 'counters'})
        return requests.post(self.vk + 'users.get', params=us_params).json()

    def get_friends(self):
        return requests.post(self.vk + 'friends.get', params=self.params).json()

    def get_groups(self, extended='0'):
        us_params = self.params
        us_params.update({'extended': extended, 'fields': 'members_count, gid'})
        return requests.post(self.vk + 'groups.get', params=self.params).json()

    def main_get(self):
        friends = self.get_friends()['response']['items']
        friends_str = ', '.join([str(i) for i in friends])
        groups = self.get_groups('1')['response']['items']
        pop_list = []
        us_params = self.params
        us_params.update({'group_id': '', 'user_ids': friends_str})
        for index, group in enumerate(groups):
            us_params['group_id'] = group['id']
            tmp = requests.post(self.vk + 'groups.isMember', params=self.params).json()
            for elem in tmp['response']:
                if elem['member'] == 1:
                    pop_list.append(index)
                    break
            time.sleep(0.3)
            print('Обработана группа {} из {}'.format(str(index + 1), str(len(groups))))

        for index, elem in enumerate(pop_list):
            groups.pop(elem - index)
        groups_list =[]

        for group in groups:
            groups_list.append({'name': group['name'],'gid': group['id'],'members_count': group['members_count']})
        json.dump(groups_list, open(os.path.join('C:\\', 'Users', 'Артём', 'Desktop', 'test.json'), 'w'))
        return 'Готово'


user1 = VkUser(171691064)

user1.main_get()
