import os
import shutil
import json
from collections import defaultdict

import requests

import keys


def parse_steps(steps, directory):
    point_images = defaultdict(dict)

    def parse_point(point):
        if 'resource' in point:
            del point['resource']
        if 'images' not in point:
            point['images'] = ['null']
        current = point_images[point['name']]
        for url in point['images']:
            if not (url == 'null' or url in current):
                file_name = f'{point["name"]} {len(current)}.jpg'
                img_data = requests.get(url).content
                with open(os.path.join(directory, 'img', file_name), 'wb') as handler:
                    handler.write(img_data)
                    current[url] = os.path.join('img', file_name)

        images = filter(lambda u: u != 'null', point['images'])
        point['images'] = [point_images[point['name']][url] for url in images]
        if 'name' in point:
            point['descriptions'] = [point['name']]
            del point['names']
        if 'images' in point: 
            string = point['images'][0]
            point['images'] = { 'filename': string}
    for step in steps:
        parse_point(step['start_point'])
        parse_point(step['end_point'])


def parse_path(path):
    if len(path['pathData'].get('steps', [])) < 2:
        return

    path_id = path['_id']
    directory = f'path_{path_id}'
    os.makedirs(directory)
    os.makedirs(os.path.join(directory, 'img'))
    parsed_path = {}
    parsed_path['steps'] = path['pathData']['steps']

    parse_steps(parsed_path['steps'], directory)

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
