# Shelly Light Control

## Introduction

In this project we connect several Shelly controlled lights to a WLan, and then control those lights with Node-RED flows, which themselves are activated by an NFC Card/Reader. The NFC Reader is connected to a Raspberry PI which has a simple driver to trigger Node-RED flows,

The controlling software stack (Node-RED and Mosquitto) may be hosted on the Raspberry PI or some other device connected to the same network (e.g. a NAS that can run Docker containers).



## BOM

### Hardware

* Shelly RGBW2 LED Controller
* Shelly Button1 WLan Switch
* Shelly DUO RGBW WLan Lamp
* Raspberry PI 4 or Pi Zero 2 W
* PN532 NFC HAT


### Software

* Node-RED flow controller
* Mosquitto MQTT broker
* Possible PN532 drivers:
  * https://github.com/nfc-tools/libnfc
  * https://github.com/adafruit/Adafruit_CircuitPython_PN532



## Design

### Shelly Button1

#### Button Configuration

A Shelly Button1 can be configured with 4 button press actions:

* Short Push.
* 2xShort Push.
* 3xShort Push.
* Long Push (parameter `longpush_duration_ms_max`: 800 2000 mSec).


Additional parameters to be programmed:

* remain_awake (0..5 sec)
* longpush_duration_ms_max (800..2000 mSec)
* multipush_time_between_pushes_ms_max (200..2000 mSec)
* actions (shortpush_url, double_shortpush_url, triple_shortpush_url & longpush_url)
  * index (0)
  * urls (string array)
  * enabled
* led_status_disable (boolean)


> API DOC : [Shelly Button1 Overview](https://shelly-api-docs.shelly.cloud/gen1/#shelly-button1-overview)

#### Button Behaviour

| State   | Button Press  | Action  |
|:--|:--|---|
| Lights Off | Single Press  | Main light on. |
| Lights Off | Double/Long Press  | Lights On (at previous brightness, colour). |
| Lights On | Single Press | All lights Off. |
| Lights On | Double/Long Press | Lights Brightness (cycle preset brightness values each 1s). |
| Lights Brightness  | Single Press | Lights On. |
| Lights Brightness | Double/Long Press | Lights Colour (cycle preset colour values each 1s). |
| Lights Colour | Single Press | Lights On. |


### NFC Card

#### Card Programming

NFC Cards are individually programmed with a feature set that corresponds to the States of the Light Controller. Therefore each NFC Card can  be programmed to have only a subset of the possible Card Behaviours (see following section for a list of those behaviours).

#### Card Layout

| Block   | Content  | Notes  |
|:--|:--|:--|
| 6 | Name | Card owner name. |
| 8 | Actions | Encoded list of actions for this card (e.g. "On,Of,Br,Co"). |
| 9 | Lights | Encoded list of light zones controlled by this card. |


#### Card Behaviours

| State   | Card  | Action  |
|:--|:--|---|
| Lights Off | Card touch  | Lights On (at previous brightness, colour). |
| Lights Off | Card touch >1s  | Lights Brightness (cycle preset brightness values each 1s). |
| Lights Brightness  | Card remove | Lights On. |
| Lights On | Card touch | Lights Off. |
| Lights On | Card touch >1s | Lights Colour (cycle preset colour values each 1s). |
| Lights Colour | Card remove | Lights On. |


#### Shellylight NFC CLI

The Shellylight NFC CLI (see projects/light/shellylight in this repo) can be used
to Listen, Program and then publish MQTT messages based on card actions.


##### Listen

```bash
$ shellylight nfc --listen
NFC Listen using PN532 with SPI connection ...
PN532: ic=50, ver=1, rev=6
Listening for cards (ctrl-c to exit) ...
Card found, UID=6a 53 7a 15
  MiFare Blocks:
  [00] 6a 53 7a 15 56 08 04 00 62 63 64 65 66 67 68 69    jSz.V...bcdefghi
  [01] 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ................
  [02] 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ................
  [03] 00 00 00 00 00 00 ff 07 80 69 ff ff ff ff ff ff    .........i......
  [04] 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ................
  [05] 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ................
  [06] 66 6f 6f 20 20 20 20 20 20 20 20 20 20 20 20 20    foo             
  [07] 00 00 00 00 00 00 ff 07 80 69 ff ff ff ff ff ff    .........i......
  [08] 4f 6e 2c 4f 66 2c 42 72 2c 43 6f 20 20 20 20 20    On,Of,Br,Co     
  [09] 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20                    
...
Card removed.
Listening for cards (ctrl-c to exit) ...
```

##### Program

```bash
$ shellylight nfc --program --name foo --actions All
NFC Listen using PN532 with SPI connection ...
PN532: ic=50, ver=1, rev=6
Listening for cards (ctrl-c to exit) ...
Card found, UID=6a 53 7a 15
 write b'foo             ' @ 6
 write b'On,Of,Br,Co     ' @ 8
 write b'                ' @ 9
  [06] 66 6f 6f 20 20 20 20 20 20 20 20 20 20 20 20 20    foo             
  [08] 4f 6e 2c 4f 66 2c 42 72 2c 43 6f 20 20 20 20 20    On,Of,Br,Co     
  [09] 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20                    
Card removed.
```

##### MQTT (publisher)

```bash
$ shellylight nfc --mqtt --broker red --topic lights 
NFC Listen using PN532 with SPI connection ...
PN532: ic=50, ver=1, rev=6
Listening for cards (ctrl-c to exit) ...
Card found, UID=03 55 ef 96
  [06] 66 6f 6f 20 20 20 20 20 20 20 20 20 20 20 20 20    foo             
  [08] 4f 6e 2c 4f 66 2c 42 72 2c 43 6f 20 20 20 20 20    On,Of,Br,Co     
  [09] 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20                    
Send to broker:localhost on topic:test ...
Card removed.
Listening for cards (ctrl-c to exit) ...
```


## Bringup

### Python Package

```bash
$ git clone https://github.com/trulede/raspberry.docker.git
$ cd raspberry.docker/projects/light/shellylight
$ python -m pip install -e .

# Normally your shell will have this PATH set.
$ export PATH=~/.local/bin:$PATH

# Run the CLI application.
$ shellylight --help
usage: shellylight [-h] {nfc,switch} ...

Shelly Light Project

positional arguments:
  {nfc,switch}  commands
    nfc         NFC Command
    switch       Switch Command

optional arguments:
  -h, --help     show this help message and exit
```

### PN532 NFC HAT

On the PN532 NFC HAT, set the following jumpers:

* L0 -> L
* L1 -> H
* RSTPDN -> D20

and the DIP switch to:

* SCK = ON
* MISO = ON
* MOSI = ON
* NSS = ON (P4/D4/BCM)
* SCL = OFF
* SDA = OFF
* RX = OFF
* TX = OFF

Now connect the PN532 NFC HAT to the Raspberry PI. Further documentation available in the [PN532 NFC HAT Wiki](https://www.waveshare.com/wiki/PN532_NFC_HAT), [PN532 Datasheet](https://www.waveshare.com/w/upload/f/f1/Pn532ds.pdf) or [PN532 User Manual](https://www.waveshare.com/w/upload/b/bb/Pn532um.pdf).


```bash
# Enable SPI.
$ sudo raspi-config

# Run the NFC Listen command.
$ shellylight nfc --listen
NFC Listen using PN532 with SPI connection ...
PN532: ic=50, ver=1, rev=6
Listening for cards (ctrl-c to exit) ...
Card found, UID=6a 53 7a 15
  MiFare Blocks:
  [00] 6a 53 7a 15 56 08 04 00 62 63 64 65 66 67 68 69    jSz.V...bcdefghi
  [01] 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00    ................
  ...
  NTAG Blocks:
Block scan complete.
Card removed.
```