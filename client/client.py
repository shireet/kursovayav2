import httpx
import json

class AsyncClusterClient:
    def __init__(self, manager_url, timeout=10.0):
        self.manager_url = manager_url
        self.timeout = httpx.Timeout(timeout, connect=5.0)
        self.session = httpx.AsyncClient(timeout=self.timeout)

    async def __aenter__(self):
        await self.session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def send_points_to_manager_async(self, points, k, max_iter,headers):
        url = f"{self.manager_url}/cluster/"  
        data = {"data_points": points,
                "num_clusters": k,
                "max_iterations": max_iter}
        response = await self.session.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self.session.aclose()

    async def get_result(self, header, id):
        url = f"{self.manager_url}/result/{id}"
        response = await self.session.get(url, headers=header)
        response.raise_for_status()
        return response.json()

class SyncClusterClient:
    def __init__(self, manager_url, timeout=10.0):
        self.manager_url = manager_url
        self.timeout = httpx.Timeout(timeout, connect=5.0)
        self.session = httpx.Client(timeout=self.timeout)

    def send_points_to_manager_sync(self, points, k, max_iter, headers):
        url = f"{self.manager_url}/cluster/"
        data = {"data_points": points,
                "num_clusters": k,
                "max_iterations": max_iter}
        response = self.session.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_result(self, header, id):
        url = f"{self.manager_url}/result/{id}"
        response = self.session.get(url, headers=header)
        response.raise_for_status()
        return response.json()

    def close(self):
        self.session.close()
