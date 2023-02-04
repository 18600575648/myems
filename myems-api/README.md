# MyEMS API Service

## Introduction

RESTful API service for [MyEMS](https://github.com/MyEMS/myems) components and third party applications.

## Prerequisites

anytree

simplejson

mysql-connector-python

falcon

falcon_cors

falcon-multipart

gunicorn

et_xmlfile

jdcal

openpyxl

pillow

python-decouple

## Quick Run for Development

Quick run on Linux (NOT for production use):
```bash
cd myems/myems-api
sudo pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
cp example.env .env
sudo chmod +x run.sh
./run.sh
```

Quick run on Windows (NOT for production usage):

Find python path in Command Prompt:
```bash
where python
```
Assume the result is 'C:\Users\johnson\AppData\Local\Programs\Python\Python310\python.exe'

Copy fcntl.py and pwd.py to lib folder:
```bash
cp myems\myems-api\fcntl.py C:\Users\johnson\AppData\Local\Programs\Python\Python310\Lib
cp myems\myems-api\pwd.py C:\Users\johnson\AppData\Local\Programs\Python\Python310\Lib
```

Install and run with waitress:
```bash
pip install waitress
cd myems\myems-api
waitress-serve --listen=0.0.0.0:8000 app:api
```


## Installation

### Installation Option 1: Install myems-api on Docker

In this section, you will install myems-api on Docker.

* Copy source code to root directory

On Windows:
```bash
cp -r myems/myems-api c:\
cd c:\myems-api
```

On Linux:
```bash
cp -r myems/myems-api /
cd /myems-api
```

* Create .env file based on example.env file

Manually replace ~~127.0.0.1~~ with real **HOST** IP address.

```bash
cp example.env .env
```

* Build a Docker image

```bash
docker build -t myems/myems-api .
```

To build for multiple platforms and not only for the architecture and operating system that the user invoking the build happens to run.
You can use buildx and set the --platform flag to specify the target platform for the build output, (for example, linux/amd64, linux/arm64, or darwin/amd64).
```bash
docker buildx build --platform=linux/amd64 -t myems/myems-api .
```

* Run a Docker container

On Windows host, bind-mount a share upload folder at c:\myems-upload to the container, 
 and also bind-mount the .env to the container:
```bash
docker run -d -p 8000:8000 -v c:\myems-upload:/var/www/myems-admin/upload -v c:\myems-api\.env:/code/.env:ro --log-opt max-size=1m --log-opt max-file=2 --restart always --name myems-api myems/myems-api
```
On Linux host, bind-mount a share upload file folder at /myems-upload to the container,
 and also bind-mount the .env to the container:
```bash
docker run -d -p 8000:8000 -v /myems-upload:/var/www/myems-admin/upload -v /myems-api/.env:/code/.env:ro --log-opt max-size=1m --log-opt max-file=2 --restart always --name myems-api myems/myems-api
```

* -d Run container in background and print container ID

* -p Publish a container's port(s) to the host, 8000:8000 (Host:Container) binds port 8000 (right)  of the container to 
TCP port 8000 (left) of the host machine.

* -v If you use -v or --volume to bind-mount a file or directory that does not yet exist on the Docker host, 
-v creates the endpoint for you. It is always created as a directory. 
The ro option, if present, causes the bind mount to be mounted into the container as read-only.

* --log-opt max-size=2m The maximum size of the log before it is rolled. A positive integer plus a modifier representing the unit of measure (k, m, or g).

* --log-opt max-file=2 The maximum number of log files that can be present. If rolling the logs creates excess files, the oldest file is removed. A positive integer. 

* --restart Restart policy to apply when a container exits

* --name Assign a name to the container

The absolute path before colon is for path on host  and that may vary on your system.
The absolute path after colon is for path on container and that CANNOT be changed.
By passing .env as bind-mount parameter, you can change the configuration values later.
If you changed .env file, restart the container to make the change effective.

If you want to immigrate the image to another computer,
* Export image to tarball file
```bash
docker save --output myems-api.tar myems/myems-api
```
* Copy the tarball file to another computer, and then load image from tarball file
```bash
docker load --input .\myems-api.tar
```

### Option 2: Online install myems-api on Ubuntu Server with internet access

In this section, you will online install myems-api on Ubuntu Server with internet access.
* Copy source code to a production Ubuntu Server and then install tools
```bash
cd myems/myems-api
sudo pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

* Install  myems-api service:
```bash
sudo cp -r myems/myems-api /myems-api
```
Create .env file based on example.env and edit the .env file if needed:
```bash
sudo cp /myems-api/example.env /myems-api/.env
sudo nano /myems-api/.env
```
Check or change the listening port (default is 8000) in myems-api.service and myems-api.socket:
```bash
sudo nano /myems-api/myems-api.service
```
```bash
ExecStart=/usr/local/bin/gunicorn -b 0.0.0.0:8000 --pid /run/myems-api/pid --timeout 600 --workers=4 app:api
```
```bash
sudo nano /myems-api/myems-api.socket
```
```bash
ListenStream=0.0.0.0:8000
```
Add port to firewall:
```bash
sudo ufw allow 8000
```
Setup systemd configure files:
```bash
sudo cp /myems-api/myems-api.service /lib/systemd/system/
sudo cp /myems-api/myems-api.socket /lib/systemd/system/
sudo cp /myems-api/myems-api.conf /usr/lib/tmpfiles.d/
```
Next enable the services so that they autostart at boot:
```bash
sudo systemctl enable myems-api.socket
sudo systemctl enable myems-api.service
```
Start the services :
```bash
sudo systemctl start myems-api.socket
sudo systemctl start myems-api.service
```

### Option 3: Offline install myems-api on Ubuntu Server without internet access

In this section, you will offline install myems-api on Ubuntu Server without internet access.
* Download tools 
```bash
mkdir ~tools && cd ~/tools
git clone https://github.com/c0fec0de/anytree.git
git clone https://github.com/simplejson/simplejson.git
wget https://cdn.mysql.com//Downloads/Connector-Python/mysql-connector-python-8.0.28.tar.gz
mkdir ~/tools/falcon && cd ~/tools/falcon
pip download cython falcon falcon-cors falcon-multipart
cd ~/tools
mkdir ~/tools/gunicorn && cd ~/tools/gunicorn
pip download gunicorn
cd ~/tools
wget https://foss.heptapod.net/openpyxl/et_xmlfile/-/archive/1.1/et_xmlfile-1.1.tar.gz
cd ~/tools
git clone https://github.com/phn/jdcal.git
mkdir ~/tools/pillow && cd ~/tools/pillow 
pip download Pillow
cd ~/tools
wget https://foss.heptapod.net/openpyxl/openpyxl/-/archive/3.0.7/openpyxl-3.0.7.tar.gz
cd ~/tools
git clone https://github.com/henriquebastos/python-decouple.git
```
* Copy source code and tools to the production Ubuntu Server and then run:
```bash
cd ~/tools/anytree
python setup.py install 
cd ~/tools/simplejson
python setup.py install 
cd ~/tools
tar xzf mysql-connector-python-8.0.28.tar.gz
cd ~/tools/mysql-connector-python-8.0.28
python setup.py install
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
dpkg-reconfigure locales
pip install --upgrade --no-index --find-links ~/tools/falcon cython falcon falcon-cors falcon-multipart
pip install --no-index --find-links ~/tools/gunicorn gunicorn
cd ~/tools
tar xzf et_xmlfile-1.1.tar.gz
cd ~/tools/et_xmlfile-1.1
python setup.py install
cd ~/tools/jdcal
python setup.py install
cd ~/tools
pip install --no-index --find-links ~/tools/pillow Pillow
tar xzf openpyxl-3.0.7.tar.gz
cd ~/tools/openpyxl-3.0.7
python setup.py install
cd ~/tools/python-decouple
python setup.py install
```

* Install  myems-api service:
```bash
cp -r myems/myems-api /myems-api
```
Create .env file based on example.env and edit the .env file if needed:
```bash
cp /myems-api/example.env /myems-api/.env
nano /myems-api/.env
```
Check or change the listening port (default is 8000) in myems-api.service and myems-api.socket:
```bash
nano /myems-api/myems-api.service
```
```bash
ExecStart=/usr/local/bin/gunicorn -b 0.0.0.0:8000 --pid /run/myems-api/pid --timeout 600 --workers=4 app:api
```
```bash
nano /myems-api/myems-api.socket
```
```bash
ListenStream=0.0.0.0:8000
```
Add port to firewall:
```bash
ufw allow 8000
```
Setup systemd configure files:
```bash
cp /myems-api/myems-api.service /lib/systemd/system/
cp /myems-api/myems-api.socket /lib/systemd/system/
cp /myems-api/myems-api.conf /usr/lib/tmpfiles.d/
```
   Next enable the services so that they autostart at boot:
```bash
  systemctl enable myems-api.socket
  systemctl enable myems-api.service
```
Start the services :
```bash
systemctl start myems-api.socket
systemctl start myems-api.service
```

### Installation Option 4: Install myems-api on macOS

Please refer to [Installation on macOS (Chinese)](/myems-api/installation_macos_zh.md)


## API List

Please refer to [API List](https://myems.io/docs/api)

## References

[1]. http://myems.io

[2]. https://falconframework.org/

[3]. https://github.com/lwcolton/falcon-cors

[4]. https://github.com/yohanboniface/falcon-multipart

[5]. http://gunicorn.org

[6]. https://github.com/henriquebastos/python-decouple/

[7]. https://foss.heptapod.net/openpyxl/openpyxl

[8]. https://foss.heptapod.net/openpyxl/et_xmlfile/

[9]. https://docs.pylonsproject.org/projects/waitress/en/latest/

