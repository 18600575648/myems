## MyEMS Modbus TCP Service

### Introduction

This service is a component of MyEMS to acquire data from Modbus TCP devices.

### Prerequisites

mysql-connector-python

modbus_tk

schedule

python-decouple


### Quick Run for Development

```bash
cd myems/myems-modbus-tcp
pip install -r requirements.txt
cp example.env .env
chmod +x run.sh
./run.sh
```

### Installation

### Option 1: Install myems-modbus-tcp on Docker

In this section, you will install myems-modbus-tcp on Docker.

* Copy source code to root directory

On Windows:
```bash
cp -r myems/myems-modbus-tcp c:\
cd c:\myems-modbus-tcp
```

On Linux:
```bash
cp -r myems/myems-modbus-tcp /
cd /myems-modbus-tcp
```

* Create .env file based on example.env file

Manually replace ~~127.0.0.1~~ with real **HOST** IP address.

```bash
cp example.env .env
```

* Build a Docker image

```bash
docker build -t myems/myems-modbus-tcp .
```

To build for multiple platforms and not only for the architecture and operating system that the user invoking the build happens to run.
You can use buildx and set the --platform flag to specify the target platform for the build output, (for example, linux/amd64, linux/arm64, or darwin/amd64).
```bash
docker buildx build --platform=linux/amd64 -t myems/myems-modbus-tcp .
```


* Run a Docker container on Linux (run as superuser)
```bash
docker run -d -v /myems-modbus-tcp/.env:/code/.env:ro --log-opt max-size=1m --log-opt max-file=2 --restart always --name myems-modbus-tcp myems/myems-modbus-tcp
```

* Run a Docker container on Windows (Run as Administrator)
```bash
docker run -d -v c:\myems-modbus-tcp\.env:/code/.env:ro --log-opt max-size=1m --log-opt max-file=2 --restart always --name myems-modbus-tcp myems/myems-modbus-tcp
```

* -d Run container in background and print container ID

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

* Immigrate the Docker container

To immigrate the container to another computer,
* Export image to tarball file
```bash
docker save --output myems-modbus-tcp.tar myems/myems-modbus-tcp
```
* Copy the tarball file to another computer, and then load image from tarball file
```bash
docker load --input .\myems-modbus-tcp.tar
```

### Installation Option 2: Online install on Ubuntu server with internet access

In this section, you will install myems-modbus-tcp on Ubuntu Server with internet access.

```bash
cp -r myems/myems-modbus-tcp /myems-modbus-tcp
cd /myems-modbus-tcp
pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

Copy exmaple.env file to .env and modify the .env file:
```bash
cp /myems-modbus-tcp/example.env /myems-modbus-tcp/.env
nano /myems-modbus-tcp/.env
```
Setup systemd service:
```bash
cp myems-modbus-tcp.service /lib/systemd/system/
```
Enable the service:
```bash
systemctl enable myems-modbus-tcp.service
```
Start the service:
```bash
systemctl start myems-modbus-tcp.service
```
Monitor the service:
```bash
systemctl status myems-modbus-tcp.service
```
View the log:
```bash
cat /myems-modbus-tcp.log
```

### Installation Option 3: Offline install on Ubuntu server without internet access

Download and install MySQL Connector:
```bash
cd ~/tools
wget https://cdn.mysql.com//Downloads/Connector-Python/mysql-connector-python-8.0.28.tar.gz
tar xzf mysql-connector-python-8.0.28.tar.gz
cd ~/tools/mysql-connector-python-8.0.28
python3 setup.py install
```

Download and install Schedule
```bash
cd ~/tools
git clone https://github.com/dbader/schedule.git
cd ~/tools/schedule
python3 setup.py install
```

Download and install Python Decouple
```bash
cd ~/tools
git clone https://github.com/henriquebastos/python-decouple.git
cd ~/tools/python-decouple
python3 setup.py  install
```

Download and install modbus-tk
```bash
cd ~/tools
git clone https://github.com/pyserial/pyserial.git
cd ~/tools/pyserial
python3 setup.py install
git clone https://github.com/ljean/modbus-tk.git
cd ~/tools/modbus-tk
python3 setup.py install
```

Install myems-modbus-tcp service
```bash
cp -r myems/myems-modbus-tcp /myems-modbus-tcp
cd /myems-modbus-tcp
```
Create .env file based on example.env and edit the .env file if needed:
```bash
cp /myems-modbus-tcp/example.env /myems-modbus-tcp/.env
nano /myems-modbus-tcp/.env
```
Setup systemd service:
```bash
cp myems-modbus-tcp.service /lib/systemd/system/
```
Enable the service:
```bash
systemctl enable myems-modbus-tcp.service
```
Start the service:
```bash
systemctl start myems-modbus-tcp.service
```
Monitor the service:
```bash
systemctl status myems-modbus-tcp.service
```
View the log:
```bash
cat /myems-modbus-tcp.log
```

### Add Data Sources and Points in MyEMS Admin UI

NOTE: If you modified Modbus TCP data sources and points, please restart this service:
```bash
systemctl restart myems-modbus-tcp.service
```

Input Data source protocol: 
```
modbus-tcp
```
Data source connection example:
```
{"host":"10.9.67.99","port":502}
```

Point address example:
```
{"slave_id":1, "function_code":3, "offset":0, "number_of_registers":2, "format":"<f", "byte_swap":true}
```

### Address 

#### slave_id
    The slave ID

#### function_code
```
    01 (0x01) Read Coils
    02 (0x02) Read Discrete Inputs
    03 (0x03) Read Holding Registers
    04 (0x04) Read Input Registers
    23 (0x17) Read/Write Multiple registers
```

#### offset
    The starting register address specified in the Request PDU

#### number_of_registers
    The number of registers specified in the Request PDU

#### format
Use python3 library struct to format bytes.
Python bytes objects are used to hold the data representing the C struct
and also as format strings (explained below) to describe the layout of data in the C struct.

The optional first format char indicates byte order, size and alignment:
    @: native order, size & alignment (default)
    =: native order, std. size & alignment
    <: little-endian, std. size & alignment
    >: big-endian, std. size & alignment
    !: same as >

The remaining chars indicate types of args and must match exactly;
these can be preceded by a decimal repeat count:
    x: pad byte (no data); c:char; b:signed byte; B:unsigned byte;
    ?: _Bool (requires C99; if not available, char is used instead)
    h:short; H:unsigned short; i:int; I:unsigned int;
    l:long; L:unsigned long; f:float; d:double.

Special cases (preceding decimal count indicates length):
    s:string (array of char); p: pascal string (with count byte).
Special cases (only available in native format):
    n:ssize_t; N:size_t;
    P:an integer type that is wide enough to hold a pointer.

Special case (not in native mode unless 'long long' in platform C):
    q:long long; Q:unsigned long long

Whitespace between formats is ignored.

#### byte_swap
A boolean indicates whether or not to swap adjacent bytes.  
Swap adjacent bytes of 32bits(4bytes) or 64bits(8bytes).
This is not for little-endian and big-endian swapping, and use format for that.
The option is effective when number_of_registers is ether 2(32bits) or 4(64bits), 
else it will be ignored.

### References
  [1]. http://myems.io
  
  [2]. http://www.modbus.org/tech.php
  
  [3]. https://github.com/ljean/modbus-tk

  [4]. https://docs.python.org/3/library/struct.html#format-strings