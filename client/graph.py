import sys
import os
import asyncio
import client as cl
import json

import matplotlib.pyplot as plt
import numpy as np


def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def main():
    files = sys.argv[1:]
    create_folder_if_not_exists("client/graphs")
    '''
    client = cl.AsyncClusterClient(manager_url)
    for id in ids:  
        try:
            result = await client.get_result(headers, id)
        except Exception as e:
            print(f"Error: {e}")
            continue
        with open(f"client/results/{id}.json", 'w') as f:
            f.write(json.dumps(result, indent=4))
    '''
    for file in files:      
        with open(file) as f: 
            data = json.load(f) 
            classes = json.loads(data['assignments'])  
            points = np.array(json.loads(data['data_points']))
            _centroids = json.loads(data['centroids']) 
            centroids = np.array([i['coordinates'] for i in _centroids])
            ids = [i['id'] for i in _centroids]
            plt.scatter(centroids[:, 0], centroids[:, 1], marker='x', s=150,linewidths = 5, zorder = 10, c=ids)
            plt.scatter(points[:, 0], points[:, 1], c=classes)            
            plt.savefig(f"client/graphs/{file.split('/')[-1].split('.')[0]}.png") 
            plt.clf()
            #for i in centroids;
            #  id.append(i['ids'])

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("no tasks provided")
    else:
        main()