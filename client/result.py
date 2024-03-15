import sys
import os
import asyncio
import client as cl
import json


CONFIG = json.load(open('config.json', 'r'))


async def main():
    ids = sys.argv[1:]
    manager_url = f"http://{CONFIG['fast']['name']}:{CONFIG['fast']['port']}"
    headers = {'accept': 'application/json'}
    create_folder_if_not_exists("client/results")
    client = cl.AsyncClusterClient(manager_url)
    for id in ids:  
        try:
            result = await client.get_result(headers, id)
        except Exception as e:
            print(f"Error: {e}")
            continue
        with open(f"client/results/{id}.json", 'w') as f:
            f.write(json.dumps(result, indent=4))    


def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("no tasks provided")
    else:
        asyncio.run(main())
        