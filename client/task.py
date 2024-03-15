import asyncio
import client as cl
import timeit
import json
import sys
import os
import time


CONFIG = json.load(open('config.json', 'r'))

def is_valid_file(file_path):
    if not os.path.isfile(file_path):
        return False
    if not file_path.endswith('.json'):
        return False
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            if not content:
                return False
            data = json.loads(content)
            required_keys = ["data_points", "num_clusters", "max_iterations"]
            return all(key in data for key in required_keys)
    except (json.JSONDecodeError, FileNotFoundError):
        return False
    return True

    

async def Process_task_async(client, task, headers):
    data = json.load(open(task, 'r'))
    points = data["data_points"]
    max_iter = data["max_iterations"]
    k = data["num_clusters"]
    result = await client.send_points_to_manager_async(points, k, max_iter, headers)
    print(result['correlation_id'])



def Process_task_sync(client, task, headers):
    data = json.load(open(task, 'r'))
    points = data["data_points"]
    max_iter = data["max_iterations"]
    #k = data["num_clusters"]
    k = CONFIG["k_mean"]["centers"]
    result = client.send_points_to_manager_sync(points, k, max_iter, headers)
    print(result['correlation_id'])

async def Run_async(tasks, manager_url, headers):
    client = cl.AsyncClusterClient(manager_url)
    await asyncio.gather(*(Process_task_async(client, task, headers) for task in tasks))
    await client.close()

def Run_sync(tasks, manager_url, headers):
    client = cl.SyncClusterClient(manager_url)
    for task in tasks:
        Process_task_sync(client, task, headers)
    client.close()

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

async def main():
    manager_url = f"http://127.0.0.1:{CONFIG['fast']['port']}"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    start_time = timeit.default_timer()
    await Run_async(sys.argv[1:], manager_url, headers)
    end_time = timeit.default_timer()
    #print(f"Total async time: {end_time - start_time}")

    

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("no tasks provided")
        sys.exit(1)
    for file_path in sys.argv[1:]:
        if not is_valid_file(file_path):
            print(f"Invalid file: {file_path}")
            sys.exit(1)
    asyncio.run(main())
