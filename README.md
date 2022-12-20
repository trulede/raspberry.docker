# raspberry.docker

Raspberry Pi with Docker.

### Included Projects:

* [Light](projects/light/README.md) - Shelly light controller using NFC (PN532 NFC HAT), NodeRED and Python. `shellylight` CLI application includes NFC subcommand for programming NFC cards.



## Raspberry PI OS

Use the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) to install Raspberry PI OS (I used the 64 bit variant).


## Software Setup

> Note: All commands are relative to your home directory unless otherwise noted.


### System Packages

```bash
$ sudo apt-get update
$ sudo apt install -y \
    build-essential \
    curl \
    git \
    libffi-dev \
    libssl-dev \
    python3 \
    python3-dev \
    python3-pip\
    samba \
    samba-common-bin \
    vim
$ sudo apt autoremove
```


### Docker

```bash
$ curl -fsSL https://get.docker.com -o get-docker.sh
$ sudo sh get-docker.sh
$ sudo pip3 install docker-compose

$ sudo usermod -aG docker <user>
$ sudo usermod -aG docker Pi
$ sudo systemctl enable docker

$ docker network create pi
```


### File Sharing with SMB

```bash
$ sudo nano /etc/samba/smb.conf   # see partial sample below
$ sudo smbpasswd -a <user>
$ sudo systemctl restart smbd
```

/etc/samba/smb.conf
```inifile
[homes]
   comment = Home Directories
   browseable = no
   read only = no
   create mask = 0775
   directory mask = 0775
   valid users = %S
```

The SMB share can be accessed via this address: `\\raspberrypi\<user>`.


## Container Setup

> Note: All containers are connected to the Docker Network "pi" so that they can communicate with each other.


### Configuration Files

#### Redis

```bash
$ mkdir -p ~/containers/redis
$ cd ~/containers/redis
$ curl -O https://raw.githubusercontent.com/antirez/redis/7.0/redis.conf
$ vim redis.conf   # see partial sample below
$ echo "alias redis-cli='docker exec -it redis redis-cli'" >> ~/.bashrc
```

~/containers/redis/redis.conf
```inifile
databases 2
maxmemory 256mb
appendonly yes
appendfsync no
```


#### Mosquitto MQTT Broker

```bash
$ mkdir -p ~/containers/mosquitto/config
$ echo "listener 1883 0.0.0.0" >> ~/containers/mosquitto/config/mosquitto.conf
$ echo "allow_anonymous true" >> ~/containers/mosquitto/config/mosquitto.conf
```

#### Node Red

Extremely helpful guide:  [Running under Docker](https://nodered.org/docs/getting-started/docker).

```bash
$ mkdir -p ~/containers/nodered/data
$ echo "alias nodered-bash='docker exec -it nodered /bin/bash" >> ~/.bashrc
```


### Docker Compose (to start containers)

```bash
# Clone this repo.
$ git clone https://github.com/trulede/raspberry.docker.git
$ cd raspberry.docker

# Setup and start the Docker containers/services.
$ docker network create pi
$ docker compose up -d
Running 3/3
Container nodered    Started
Container redis      Started
Container mosquitto  Started
$ docker compose ps
NAME                SERVICE     STATUS    PORTS
mosquitto           mosquitto   running   0.0.0.0:1883->1883/tcp, :::1883->1883/tcp
nodered             nodered     running   0.0.0.0:1880->1880/tcp, :::1880->1880/tcp
redis               redis       running   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp
```


### Testing the Containers/Services

#### Redis

```bash
$ redis-cli set foo bar
OK
$ redis-cli get foo
"bar"
```


#### Mosquitto MQTT Broker

Testing the MMQT Broker with Python:

```python
import paho.mqtt.client as mqtt
client = mqtt.Client()
client.connect('localhost', 1883)
client.disconnect()
```


#### Node Red

The open Node-RED at http://localhost:1880.
