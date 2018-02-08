import time
import threading

import pymongo
import docker

from lib.config import Config

from slugify import slugify

def check_status():
  client    = docker.from_env()
  db_client = pymongo.MongoClient("mongodb://{}/ardegra".format(Config.DATABASE_ADDRESS))
  try:
    db = db_client["ardegra"]
    while True:
      documents = db.agentJobs.find({"status": "working"})
      for document in documents:
        try:
          container_name = slugify(document["spiderName"], to_lower=True)
          client.containers.get(container_name)
        except docker.errors.NotFound as err:
          print("[check_status] {} has stopped".format(container_name))
          db.agentJobs.update({"_id": document["_id"]}, {"$set": {"status": "stopped"}})
      time.sleep(5)
  except Exception as err:
    print("[check_status] {}".format(str(err)))
  finally:
    client.close()

def run_spider(spider_name, image_name):
  print("[agent] Pulling image: {}".format(image_name))
  client = docker.from_env()
  client.images.pull(image_name)
  print("[agent] Image pulled")
  
  container_name = slugify(spider_name, to_lower=True)
  print("[agent] Running container {}".format(container_name))
  client.containers.run(
    image=image_name, 
    command='python run.py "{}"'.format(spider_name),
    auto_remove=True,
    detach=True,
    name=container_name,
    volumes={Config.ARDEGRA_DIRECTORY: {"bind": "/root/app", "mode": "rw"}},
    working_dir="/root/app"
  )
  print("[agent] is running: {}".format(container_name))

def run():
  client = pymongo.MongoClient("mongodb://{}/ardegra".format(Config.DATABASE_ADDRESS))
  try:
    db        = client["ardegra"]
    documents = db.agentJobs.find({"status": "queueing"})
    for document in documents:
      run_spider(spider_name=document["spiderName"], image_name=document["imageName"])
      db.agentJobs.update({"_id": document["_id"]}, {"$set": {"status": "working"}})
  except Exception as err:
    print("[agent] {}".format(str(err)))
  finally:
    client.close()

if __name__ == "__main__":
  t = threading.Thread(target=check_status)
  t.start()
  
  while True:
    run()
    time.sleep(5)
