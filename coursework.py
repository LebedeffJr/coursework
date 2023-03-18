import requests
from datetime import datetime
from tqdm import tqdm


class VK:
    URL = 'https://api.vk.com/method/'
    def __init__ (self, token, version):
        self.params = {
            'access_token' : token,
            'v' : version
        }

    def get_prof_photo_url(self, owner_id = None):
        url_g_p = self.URL + 'photos.get'
        get_photo_params = {
            'owner_id' : owner_id,
            'album_id' : 'profile',
            'extended' : 1
        }
        req = requests.get(url_g_p, params={**self.params, **get_photo_params}).json()
        url_msp_list = []
        i = 0
        for info in req['response']['items']:
            for photos in info['sizes']:
                if photos['type'] == 'w' and i < 6:
                    url_msp_list.append(photos['url'])
                    i += 1
        i = 0
        name_list = []
        for name in req['response']['items']:
            if name['likes']['count'] not in name_list and i < 6:
                name_list.append(str(name['likes']['count']))
                i += 1
            elif name['likes']['count'] in name_list and i < 6:
                name_list.append(datetime.fromtimestamp(name['date']).strftime('%Y/%m/%d'))
                i += 1
            else:
                break
        name_url = zip(name_list, url_msp_list)
        return name_url


class YaDiskUpload:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth ' + self.token
        }
        self.api_url = 'https://cloud-api.yandex.net/'

    def create_folder(self, folder_path):
        url = self.api_url + 'v1/disk/resources'
        params = {'path': folder_path}
        response = requests.put(url, headers=self.headers, params=params)
        return response

    def upload_file(self, url, file_name, folder_path):
        self.create_folder(folder_path)
        file_data = requests.get(url).content
        params = {
            'path': folder_path + '/' + file_name,
            'overwrite': 'true'
        }
        response = requests.get(self.api_url + 'v1/disk/resources/upload', headers=self.headers, params=params)
        print(response.json())
        upload_url = response.json()['href']
        response = requests.put(upload_url, headers=self.headers, data=file_data)
        response.raise_for_status()
        return response

if __name__ == "__main__":
    vk_token = 'The VK-token was here!'
    vk_client = VK(vk_token, '5.131')
    ya_token = 'The Yandex-token was here!'
    ya_client = YaDiskUpload(ya_token)
    dict_photos = dict(vk_client.get_prof_photo_url())
    print(dict_photos)
    for name, url in tqdm(dict_photos.items()):
        upload_path = "/vk_photos"
        ya_client.upload_file(url, name + '.jpg', upload_path)
