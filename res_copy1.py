
import requests
import json
from tqdm import tqdm
from datetime import datetime

class VKbackap:
    
    def __init__(self, vk_user_id, vk_access_token):
        self.vk_user_id = vk_user_id
        self.vk_access_token = vk_access_token
        self.version = '5.131'
        
    def get_user_images_info(self): # function to get informaton of user images
        url = 'https://api.vk.com/method/photos.get'
        params = {'access_token' : self.vk_access_token,
                  'v' : self.version,
                  'owner_id' : self.vk_user_id, 
                  'album_id' : 'profile', 
                  'extended' : 1, 
                  'photo_sizes' : 1, 
                  'count' : 5}
        user_images = requests.get(url, params=params)
        return user_images.json()  
    
    def backup_to_yd(self, user_images): # function to upload images to YD
        
        # create folder on YD
        params = {'path': 'VK_reserve_copy'}
        headers = {'Authorization': yd_access_token}
        response = requests.put('https://cloud-api.yandex.net/v1/disk/resources', params=params, headers=headers)
    
        # iterate over images information to create data for upload to YD and json file with information of images
        images = user_images['response']['items']
        data_for_json = []
    
        for image in tqdm(images): # iterble object (images) is wrapped by tqdm class to show processbar
            image_name = f"{image['likes']['count']}_{datetime.utcfromtimestamp(int(image['date'])).strftime('%Y%m%d')}"
            image_size = ''.join(item['type'] for item in image['sizes'] if item['type'] == 'z')
            image_url = ''.join(item['url'] for item in image['sizes'] if item['type'] == 'z')
            data_for_json.append({'file_name' : f"{image_name}.jpg", 'size' : image_size})
        
            # dowload image
            response = requests.get(image_url)
            with open(f"{image_name}.jpg", 'wb') as f:
                f.write(response.content)

            # get URL for image upload to YD
            params = {'path': f"VK_reserve_copy/{image_name}.jpg"}
            response = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload', params=params, headers=headers)
            url_for_upload = response.json()['href']
        
            # upload image to YD
            with open(f"{image_name}.jpg", 'rb') as content:
                requests.put(url_for_upload, files={'file': content})
    
        # create json file with images information
        with open('images_information.json', 'w') as f:
            json.dump(data_for_json, f)
    
        print('Reserve copy complete')

    def backup(self):
        data_for_backap = self.get_user_images_info()
        return self.backup_to_yd(data_for_backap)
        
vk_user_id = str(input('Input your VK id: '))
yd_access_token = 'OAuth ' + str(input('Input your YD access token: '))
with open('access_token_vk.txt', 'r') as f:
    vk_access_token = f.read()

vk = VKbackap(vk_user_id, vk_access_token)
vk.backup()

