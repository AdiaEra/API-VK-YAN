import json
import requests
from tqdm import tqdm
from pprint import pprint
import configparser


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token_vk,
            'v': version
        }

    def get_user(self):
        users_url = self.url + 'users.get'
        users_params = {
            'user_ids': id_user
        }
        res = requests.get(users_url, params={**self.params, **users_params}).json()
        return res

    def get_photos(self):
        photos_url = self.url + 'photos.get'
        photos_params = {
            'owner_id': id_user,
            'album_id': 'profile',
            'extended': '1',
            'photo_sizes': '1',
            'count': 5
        }
        res = requests.get(photos_url, params={**self.params, **photos_params}).json()
        return res

    def get_unpack_photo(self, vk_json):
        """Функция формирует список альбомов"""
        album = vk_json['response']['items']

        return album

    def get_photo_list(self, album):
        """Функция формирует список фотографий с максимальным размером"""
        type_size = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10}
        list_photo = []
        for i in album:
            name = {}
            name['file_name'] = i['likes']['count']
            size_max = max(i['sizes'], key=lambda x: type_size[x['type']])
            name['url'] = size_max['url']
            list_photo.append(name)

        return list_photo

    def get_json_file(self, album):
        """Функция формирует файл для записи в json"""
        vk_sizes = {'s': 1, 'm': 2, 'o': 3, 'p': 4, 'q': 5, 'r': 6, 'x': 7, 'y': 8, 'z': 9, 'w': 10}
        info_json = []
        for photo in album:
            name = {}
            size = max(photo['sizes'], key=lambda x: vk_sizes[x["type"]])
            name['file_name'] = f"{photo['likes']['count']}_{photo['date']}.jpg"
            name['type'] = size['type']
            info_json.append(name)
        return info_json


class YaUser:
    def __init__(self, token: str):
        self.token = token_yan

    def get_headers(self):
        return {'Content-Type': 'application/json',
                'Authorization': 'OAuth {}'.format(self.token)
                }

    def get_files_list(self):  # подаёт список файлов, упорядоченный по имени (функция не нужна)
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources/files'
        headers = self.get_headers()
        response = requests.get(files_url, headers=headers)
        return response.json()

    def get_folder(self, path):
        folder_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        response = requests.put(f'{folder_url}/?path={path}', headers=headers)

    def _get_upload_link(self, disk_file_path):
        upload_url = 'https://cloud_api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': disk_file_path, 'overwrite': 'true'}
        response = requests.get(upload_url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, disk_file_path, filename):
        result = self._get_upload_link(disk_file_path=disk_file_path)
        url = result.get('href')
        response = requests.put(url, data=open(filename, 'rb'))
        response.raise_for_status()
        if response.status_code == 201:
            print('Success')

    def load_url_file(self, list_photo, folder_name):
        """Функция осуществляет скачивание фотографий по url."""
        link_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        for link_file in tqdm(list_photo):
            params = {'url': link_file['url'],
                      'path': f"{folder_name}/{str(link_file['file_name'])}"}
            requests.post(link_url, headers=headers, params=params)
            try:
                response = requests.get(link_file['url'])
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                print("Фото по этому url, не существует")
                print(link_file['url'])


def get_save_json(file):
    with open("name_list.json", 'w') as f:
        json.dump(file, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('settings.ini')
    # config.sections()
    token_vk = config['VkYan']['token_vk']
    token_yan = config['VkYan']['token_yan']
    vk_user = VkUser(token_vk, '5.131')
    id_user = input('Введите id пользователя: ')
    res_user = vk_user.get_user()
    # pprint(res_user)
    res_photo = vk_user.get_photos()  # <= сюда вводится id пользователя
    # pprint(res_photo)
    unpack = vk_user.get_unpack_photo(res_photo)
    name_list_size = vk_user.get_photo_list(unpack)
    # pprint(name_list_size)
    res_json = vk_user.get_json_file(unpack)
    # pprint(res_json)
    yan_user = YaUser(token_yan)
    folder_name = 'neto_test'
    res = yan_user.get_files_list()
    # pprint(res)
    yan_user.get_folder(folder_name)
    # pprint(yan_user.get_files_list())
    yan_user.load_url_file(name_list_size, folder_name)
    get_save_json(res_json)