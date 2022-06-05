import os
import json
import argparse

base_path = os.path.dirname(os.path.abspath(__file__))

def get_arguments():
    parser = parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="path of the apidoc file", type=str, required=True)
    args = parser.parse_args()
    return args


def get_apidoc(path):
    if os.path.exists(path):
        try:
            with open(path, 'rb') as infile:
                apidoc = json.load(infile)
            return apidoc
        except:
            print("failed to load json object from ", path)
            exit(1)
    else:
        print("path %s is not found" % path)
        exit(1)


def apidoc2postman(apidoc):
    # create a postman temp collection
    collection = dict({"info": {
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        }
    })

    # parse apidoc for postman collection info
    if "info" in apidoc:
        for key in apidoc["info"].keys():
            collection["info"][key] = apidoc["info"][key]

    if "title" in collection["info"]:
        collection["info"]["name"] = collection["info"]["title"].replace(' ', '_')
    else:
        collection["info"]["name"] = "new_collection"

    # parse apidoc for postman collection variables
    collection["variable"] = []

    if "servers" in apidoc:
        for key in apidoc["servers"][0].keys():
            collection["variable"].append(dict({"key": key, "value": apidoc["servers"][0][key]}))
    else:
        if "host" in apidoc:
            collection["variable"].append(dict({"key": "url", "value": apidoc["host"]}))
        else:
            collection["variable"].append(dict({"key": "url", "value": "http://localhost"}))

    # parse apidoc for postman collection items (folders)
    collection["item"] = []

    if "tags" in apidoc:
        for tag in apidoc["tags"]:
            collection["item"].append(dict({"name": tag["name"], "item": []}))


    # parse apidoc for postman collection items (requests)
    if "paths" in apidoc:
        for path in apidoc["paths"].keys():
            endpoint = path.replace("{", ":").replace("}", "")
            url = "{{url}}/" + endpoint
            request_paths = endpoint.split("/")
            request_paths.pop(0)

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
                            "path": request_paths,
                            "query": []
                        }

                    }
                })
                if "description" in apidoc["paths"][path][method]:
                    request["description"] = apidoc["paths"][path][method]["description"]
                
                if "operationId" in apidoc["paths"][path][method]:
                    request["operationId"] = apidoc["paths"][path][method]["operationId"]
                
                if "parameters" in apidoc["paths"][path][method]:
                    for param in apidoc["paths"][path][method]["parameters"]:
                        p = dict({
                            "key": param["name"],
                        })

                        if "required" in param and param["required"]:
                            p["description"] = "required. "
                        else:
                            p["description"] = ""
                            p["disabled"] = True

                        if "description" in param:
                            p["description"] += param["description"]
                        
                        if "type" in param:
                            p["type"] = param["type"]

                        if "schema" in param:
                            if "type" in param["schema"]:
                                p["type"] = param["schema"]["type"]
                            if "enum" in param["schema"]:
                                p["description"] = "%s; available values: %s" % (p["description"], param["schema"]["enum"])

                        if param["in"] == "header":
                            request["request"]["header"].append(p)
                        if param["in"] == "query":
                            request["request"]["url"]["query"].append(p)
    

                if "tags" in apidoc["paths"][path][method]:
                    for tag in apidoc["paths"][path][method]["tags"]:
                        appended = False
                        for item in collection["item"]:
                            if tag == item["name"]:
                                item["item"].append(request)
                                appended = True
                        if not appended:
                            tag_dict = dict({"name": tag, "item": []})
                            tag_dict["item"].append(request)
                            collection["item"].append(tag_dict)
                else:
                    collection["item"].append(request)

    return collection


def sort_item(item):
    if "item" in item:
        # sort each subitem
        for subitem in item["item"]:
            sort_item(subitem)

    if "request" in item:
        # sort request headers
        item["request"]["header"].sort(key=lambda x: x["key"])
        # sort request query params
        item["request"]["url"]["query"].sort(key=lambda x: x["key"])

    # sort items
    item.sort(key=lambda x: x["name"])


def sort(collection):
    # sort collection variables
    if "variable" in collection:
        collection["variable"].sort(key=lambda x: x["key"])

    # sort collection folders
    if "item" in collection:
        sort_item(collection["item"])

    return collection


def dump(collection):
    # print(collection)
    collection_path = os.path.join(base_path, "%s.json" % collection["info"]["name"])

    with open(collection_path, 'w') as outfile:
        json.dump(collection, outfile)
    
    print("postman collection is created on", collection_path)


def run():
    args = get_arguments()
    apidoc = get_apidoc(args.path)
    collection = apidoc2postman(apidoc)    
    dump(sort(collection))
    

if __name__ == "__main__":
    run()
