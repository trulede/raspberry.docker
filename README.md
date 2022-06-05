# raspberry.docker
Raspberry Pi with Docker


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
```


### File Sharing with SMB

```bash
$ sudo nano /etc/samba/smb.conf   # see partial sample below
$ sudo smbpasswd -a trule
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

### Redis

```bash
$ mkdir redis
$ cd redis
$ curl -O https://raw.githubusercontent.com/antirez/redis/7.0/redis.conf
$ vim redis.conf   # see partial sample below
$ echo "alias redis-cli='docker exec -it redis redis-cli'" >> ~/.bashrc
$ docker run -d \
    --name redis \
    --restart unless-stopped \
    -v ~/redis/redis.conf:/usr/local/etc/redis/redis.conf \
    -v ~/redis/data:/data \
    -p 6379:6379 \
    redis:latest \
    redis-server /usr/local/etc/redis/redis.conf
$ redis-cli set foo bar
OK
$ redis-cli get foo
"bar"
```

~/redis/redis.conf
```inifile
databases 2
maxmemory 256mb
appendonly yes
appendfsync no
```


### Mosquito MQTT Broker

```bash
$ mkdir -p mosquitto/data
$ docker run -d \
    --name mosquitto \
    --restart unless-stopped \
    -v ~/mosquitto/data:/mosquitto/data \
    -p 1883:1883 \
    -p 9001:9001 \
    eclipse-mosquitto:latest
```


### Node Red

Extremely helpful guide:  [Running under Docker](https://nodered.org/docs/getting-started/docker).

```bash
$ mkdir -p nodered/data
$ echo "alias nodered-bash='docker exec -it nodered /bin/bash" >> ~/.bashrc
$ docker run -d \
    --name nodered \
    --restart unless-stopped \
    -v ~/nodered/data:/data \
    -p 1880:1880 \
    nodered/node-red:latest
```
