
import os
from .config import download_dir
from .persistent_list import PersistentList

queue_path = os.path.join(download_dir, "queue.json")
data = PersistentList(queue_path)
running_tasks = []
