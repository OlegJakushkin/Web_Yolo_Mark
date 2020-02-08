# Web_Yolo_Mark
GUI for marking bounded boxes of objects in images for training neural network like Yolo 

[![CircleCI](https://circleci.com/gh/OlegJakushkin/Web_Yolo_Mark.svg?style=svg)](https://circleci.com/gh/OlegJakushkin/Web_Yolo_Mark)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Pulls](https://img.shields.io/docker/pulls/olejak/web_mark_yolo)](https://hub.docker.com/r/olejak/web_mark_yolo)

[!How to use this (in russian)](https://docs.google.com/presentation/d/e/2PACX-1vQrO13OqmhA_7h5FGCiOuaW9YlVC9iysVQxXnRfP-MWkU3hraF5K1HcQ2KMDROvVg/pub?start=true&loop=true&delayms=30000)

## Install

### From Dockerhub
start
 - on FLASK_ADDR 0.0.0.0 (localhost and public IP if node has one) 
 - on FLASK_PORT 5002 (port can be changed) maped to 8890 on local system
 - with ADMIN_PASSWORD user password `Sc@_9Nt1f1c`
 - with shared between users images directory on a host node `/full/path/to/a/shared/images/folder/`
 - with db and logs directory on a host node `/full/path/to/a/shared/db/folder/`

```bash
docker run -d -p 8890:5002  -e ADMIN_PASSWORD=Sc@_9Nt1f1c -e FLASK_PORT=5002 -e FLASK_ADDR='0.0.0.0' -v /full/path/to/a/shared/images/folder/:/opt/marker/uploads -v /full/path/to/a/shared/db/folder/:/opt/marker/db olejak/web_mark_yolo:latest
```

### Build from Source
 - Get code
```bash
git clone --recursive https://github.com/OlegJakushkin/Web_Yolo_Mark 
cd Web_Yolo_Mark 
```

 - To edit backend open PyCharm in this folder, run after installing this dependencies (tested on top of Anaconda3)
 ```bash
 pip install flask-admin flask_login flask_sqlalchemy flask_user==1.* flask_compress flask_httpauth flask_restplus protobuf flask_dropzone flask_uploads flask-triangle  flask_restful  flask-locale flask-cors Flask-Caching Flask-BabelEx flask_babel
 ```
 
 - To edit Markup vector editing UI open WebStorm in ./assets/editor folder 
 
 - To simply build and run use next commands
```bash
docker build -t oj/web_mark_yolo:latest .
docker run -d -p 8890:5002  -e ADMIN_PASSWORD=Sc@_9Nt1f1c -e FLASK_PORT=5002 -e FLASK_ADDR='0.0.0.0' -v /full/path/to/a/shared/images/folder/:/opt/marker/uploads -v /full/path/to/a/shared/db/folder/:/opt/marker/db olejak/web_mark_yolo:latest
```
