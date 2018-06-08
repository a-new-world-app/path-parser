import os
import shutil
import json
from collections import defaultdict

import requests

import keys

def add_point(point_images, point, directory):
    current = point_images[point['name']]
    for url in point['images']:
        if not (url == 'null' or url in current):
            file_name = f'{point["name"]} {len(current)}.jpg'
            img_data = requests.get(url).content
            with open(os.path.join(directory, 'img', file_name), 'wb') as handler:
                handler.write(img_data)
                current[url] = os.path.join('img', file_name)


def parse_path(path):
    if len(path['pathData']['steps']) < 2:
        return

    point_images = defaultdict(dict)
    path_id = path['_id']
    directory = f'path_{path_id}'
    os.makedirs(directory)
    os.makedirs(os.path.join(directory, 'img'))
    parsed_path = {}
    parsed_path['steps'] = path['pathData']['steps']
    points = {}
    for step in parsed_path['steps']:
        if 'images' not in step['start_point']:
            step['start_point']['images'] = []
        add_point(point_images, step['start_point'], directory)
        step['start_point']['images'] = [point_images[step['start_point']['name']][url] for url in filter(lambda u: u != 'null', step['start_point']['images'])]
        if 'images' not in step['end_point']:
            step['end_point']['images'] = []
        add_point(point_images, step['end_point'], directory)
        step['end_point']['images'] = [point_images[step['end_point']['name']][url] for url in filter(lambda u: u != 'null', step['end_point']['images'])]

    parsed_path['start_point'] = path['pathData']['steps'][0]['start_point']
    parsed_path['end_point'] = path['pathData']['steps'][-1]['end_point']
    parsed_path = {'path': parsed_path}

    with open(os.path.join(directory, 'path.json'), 'w') as handler:
        handler.write(json.dumps(parsed_path))

    shutil.make_archive(directory, 'zip', directory)


url = 'https://a-new-world.herokuapp.com/api/completed_paths'
headers = {'Authorization': f'Bearer {keys.API_ACCESS_TOKEN}'}
r = requests.get(url, headers=headers)

for path in r.json():
    parse_path(path)
