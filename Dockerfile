from continuumio/anaconda3
maintainer OJ
user root

ENV ADMIN_PASSWORD=Sc@_9Nt1f1c FLASK_PORT=5002

run conda install  -c conda-forge numpy pip conda && \
	conda update  -c conda-forge -y --all

run pip install flask-admin flask_login flask_sqlalchemy flask_user=1.* flask_compress flask_httpauth flask_restplus protobuf flask_dropzone flask_uploads flask-triangle  flask_restful  flask-locale flask-cors Flask-Caching Flask-BabelEx flask_babel
	
cmd  /bin/bash -c "mkdir -p /opt/marker && cd /opt/marker && git clone --recursive https://github.com/OlegJakushkin/Web_Yolo_Mark ; cd ./Web_Yolo_Mark && python --multiproc mark.py