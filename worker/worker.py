import asyncio
import aio_pika
import json
import numpy as np
from sklearn.cluster import KMeans
import logging
import os



CONFIG = json.load(open('config.json', 'r'))

async def process_data(data_points, num_clusters, max_iterations, initial_centroids):
    if num_clusters <= 0: 
        return "Ошибка: количество кластеров должно быть больше 0"

    if isinstance(initial_centroids, str) and initial_centroids in ['k-means++', 'random']:
        init_method = initial_centroids
    else:
        init_method = np.array(initial_centroids) if len(
            initial_centroids) > 0 else 'k-means++'

    kmeans = KMeans(n_clusters=num_clusters,
                    max_iter=max_iterations, init=init_method)
    kmeans.fit(data_points)

    centroids = kmeans.cluster_centers_.tolist()  
    labels = kmeans.labels_.tolist() 
    cluster_sizes = [labels.count(i) for i in range(num_clusters)]
    total_distance = kmeans.inertia_

    response = {
        "centroids": [{"id": i, "coordinates": centroid} for i, centroid in enumerate(centroids)],
        "assignments": [{"point": point.tolist(), "cluster_id": cluster_id} for point, cluster_id in zip(data_points, labels)],
        "cluster_sizes": [{"id": i, "size": size} for i, size in enumerate(cluster_sizes)],
        "total_distance": total_distance
    }

    return json.dumps(response)


async def worker():
    connection = await aio_pika.connect_robust(f"amqp://{CONFIG["rabbitmq"]["user"]}:{CONFIG["rabbitmq"]["password"]}@rabbitmq/")
    channel = await connection.channel()

    await channel.set_qos(prefetch_count=1)
    request_queue = await channel.declare_queue(CONFIG["rabbitmq"]["routing_key"], durable=True)

    async for message in request_queue:
        async with message.process():
            data = json.loads(message.body.decode())
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            logger.info("im working!")

            if "data_points" in data and "num_clusters" in data and "max_iterations" in data:
                data_points = np.array(data["data_points"])
                num_clusters = data["num_clusters"]
                max_iterations = data["max_iterations"]

                initial_centroids = data.get("initial_centroids", 'k-means++')
                if initial_centroids != 'k-means++':
                    initial_centroids = np.array(initial_centroids)
                response_message = await process_data(data_points, num_clusters, max_iterations, initial_centroids)
            
            else:
                response_message = "Ошибка: неправильный формат данных"

            if message.reply_to:
                await channel.default_exchange.publish(
                    aio_pika.Message(
                        body=response_message.encode(),
                        correlation_id=message.correlation_id,
                    ),
                    routing_key=message.reply_to,
                )

if __name__ == "__main__":
    asyncio.run(worker())
