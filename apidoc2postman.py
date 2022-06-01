from ast import And
from inspect import Parameter
import os
import json
from re import L

base_path = os.path.dirname(os.path.abspath(__file__))

apidoc_path = os.path.join(base_path, "sameple_apidoc.json")
collection = {}

with open(apidoc_path, 'r') as infile:
    apidoc = json.load(infile)


# get collection info
collection["info"] = dict({
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    })

if "info" in apidoc:
    for key in apidoc["info"].keys():
        collection["info"][key] = apidoc["info"][key]

if "title" in collection["info"]:
    collection["info"]["name"] = collection["info"]["title"].replace(' ', '_')
else:
    collection["info"]["name"] = "new_collection"

collection_path = os.path.join(base_path, "%s.json" % collection["info"]["name"])


# get collection variables
collection["variable"] = []

if "servers" in apidoc:
    server_url = apidoc["servers"][0]["url"]
    for key in apidoc["servers"][0].keys():
        collection["variable"].append(dict({"key": key, "value": apidoc["servers"][0][key]}))
else:
    server_url = "http://localhost"


# get tags
collection["item"] = []

if "tags" in apidoc:
    for tag in apidoc["tags"]:
        collection["item"].append(dict({"name": tag["name"], "item": []}))


# get paths
# requests = []

if "paths" in apidoc:
    for path in apidoc["paths"].keys():
        endpoint = path.replace("{", ":").replace("}", "")
        url = "{{url}}/" + endpoint
        request_paths = endpoint.split("/")
        request_paths.pop(0)
        # for method in apidoc["paths"][path].keys():
        #     requests.append(dict({
        #         "name": path,
        #         "request": {
        #             "method": method,
        #             "header": [],
        #             "url": {
        #                 "raw": url,
        #                 "protocol": server_url.split(":")[0],
        #                 "host": [server_url.split("/")[2]],
        #                 "path": request_paths
        #             }
        #         }
        #     }))

        for method in apidoc["paths"][path].keys():
            request = {}
            request = dict({
                "name": path,
                "request": {
                    "method": method,
                    "header": [],
                    "url": {
                        "raw": url,
                        "host": "{{url}}",
                        "path": request_paths
                    }

                }
            })
            if "description" in apidoc["paths"][path][method]:
                request["description"] = apidoc["paths"][path][method]["description"]
            
            if "operationId" in apidoc["paths"][path][method]:
                request["operationId"] = apidoc["paths"][path][method]["operationId"]
            
            if "parameters" in apidoc["paths"][path][method]:
                request["request"]["header"] = []
                request["request"]["url"]["query"] = []

                for param in apidoc["paths"][path][method]["parameters"]:
                    print(param)
                    p = dict({
                        "key": param["name"],
                    })

                    if "type" in param["schema"]:
                        p["type"] = param["schema"]["type"]

                    if "required" in param and param["required"]:
                        p["description"] = "required. "
                    else:
                        p["description"] = ""
                        p["disabled"] = True

                    if "description" in param:
                        p["description"] += param["description"]


                    if param["in"] == "header":
                        request["request"]["header"].append(p)
                    if param["in"] == "query":
                        request["request"]["url"]["query"].append(p)
 

            if "tags" in apidoc["paths"][path][method]:
                for tag in apidoc["paths"][path][method]["tags"]:
                    for item in collection["item"]:
                        if tag in item["name"]:
                            item["item"].append(request)
            else:
                collection["item"].append(request)


# print(requests)
print(collection)

with open(collection_path, 'w') as outfile:
    json.dump(collection, outfile)