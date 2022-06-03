# apidoc2postman
This script converts apidocs to postman collection

## Prerequisites
    * python 3.9+

**Syntax:**

    py apidoc2postman.py -p <path of apidoc>

**Options:**

    --path, -p      path of apidoc

**Output:**

    the postman collection file (.json)

    
**Examples:**

    py apidoc2postman.py -p .\prva_apidoc.json

## Download apidoc from swagger ui
    1. Launch a service swagger ui
    2. click the "api-docs" hyperlink
    3. save the content of the service apidoc to a json file

## Convert apidoc to postman collection
    py apidoc2postman.py -p <path of apidoc (.json) file> 
    
    A postman collection (.json) file is created by the apidoc 

## Import collection to postman
    1. open the Postman
    2. click the Import
    3. drag and drop the postman collection (.json) file to the Postman Import dialog
    4. the postman collection will be imported with list of service endpoints

## Contact:
    jerrycpyang@gmail.com
