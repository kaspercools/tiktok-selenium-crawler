from ast import keyword
import glob
import os.path
from os import path
import json
from re import A
import shutil
import uuid

todoPath = "./todo"
skippedPath = "./skipped"
resultsPath = "./results"
pendingPath = "./pending"


def get_files(dir):
    return glob.glob(dir)


def read_json(file):
    with open(file, encoding="utf-8") as data_file:
        print(file)
        data = json.loads(data_file.read())

    return data


# {'status': 'building', 'message': 'Dataset is not ready yet, try again in 10s'}
def is_processing_needed(file, data):
    if data["status"] == "building":
        shutil.move(file, skippedPath)
        return False
    return True


def create_individual_documents(data):
    posts = []

    for categoryCollection in data:
        if not 'top_videos' in categoryCollection:
            continue
        
        # print(categoryCollection)
        if not 'title' in categoryCollection:
            keyword='unknown'
            id=str(uuid.uuid1())
        else:
            keyword = categoryCollection["title"]
            id=categoryCollection["id"]

        keywordPath = path.join(todoPath, keyword)
        if not path.exists(keywordPath):
            os.mkdir(keywordPath)

        if not path.exists(path.join(keywordPath, id + ".json")):
            posts += retrieve_individual_document_data(
                keyword, categoryCollection["top_videos"]
            )

            write_json_to_file(
                posts, path.join(keywordPath, id+ ".json")
            )
    


def write_json_to_file(data, path):
    with open(path, "w") as outfile:
        json.dump(data, outfile)


def retrieve_individual_document_data(keyword, videos):
    posts = []
    print(keyword)
    for videoPost in videos:
        post = {}
        
        post["keyword"] = keyword
        post["id"] = videoPost["id"]
        post["content"] = videoPost["description"]
        post["created_on"] = videoPost["create_time"]
        post["diggCount"] = videoPost["diggCount"]
        post["shareCount"] = videoPost["shareCount"]
        post["commentCount"] = videoPost["commentCount"]
        post["playCount"] = videoPost["playCount"]
        post["username"] = videoPost["username"]
        post["influencer_id"] = videoPost["influencer_id"]
        post["video"] = {
            "id": videoPost["video"]["id"],
            "duration": videoPost["video"]["duration"],
        }
        post["music"] = {
            "id": videoPost["music"]["id"],
            "title": videoPost["music"]["title"],
            "is_original": videoPost["music"]["original"],
            "url": videoPost["music"]["playurl"],
        }

        if "authorname" in post["music"]:
            post["music"]["authorname"] = videoPost["music"]["authorname"]

        post["comments"] = []
        posts.append(post)

    return posts

def run():
    jsonFiles = get_files("./todo/*.json")

    for dataFile in jsonFiles:
        data = read_json(dataFile)
        if not isinstance(data, list):
            print(is_processing_needed(dataFile, data))

        create_individual_documents(data)
        shutil.move(dataFile, resultsPath)

if __name__ == "__main__":
    run()


