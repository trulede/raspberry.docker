# Shelly Light Control

## Introduction

In this project we connect several Shelly controlled lights to a WLan, and then control those lights with Node-RED flows, which themselves are activated by an RFID Card/Reader. The RFID Reader is connected to a Raspberry PI which has a simple driver to trigger Node-RED flows,

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
  * https://github.com/ikelos/pynfc
  * https://github.com/adafruit/Adafruit_CircuitPython_PN532
  * https://github.com/adafruit/Adafruit_Python_PN532



## Design

### Shelly Button1

#### Button Configuration

> TODO: Determine button configuration. Button configuration may be done with a CLI tool or via Shelly App.


#### Button Behaviour

| State   | Button Press  | Action  |
|:-:|:-:|---|
| Lights Off | Single Press  | Main light on. |
| Lights Off | Double/Long Press  | Lights On (at previous brightness, colour). |
| Lights On | Single Press | All lights Off. |
| Lights On | Double/Long Press | Lights Brightness (cycle preset brightness values each 1s). |
| Lights Brightness  | Single Press | Lights On. |
| Lights Brightness | Double/Long Press | Lights Colour (cycle preset colour values each 1s). |
| Lights Colour | Single Press | Lights On. |


### RFID Card

#### Card Programming

RFID Cards are individually programmed with a feature set that corresponds to the States of the Light Controller. Therefore each RFID Card can  be programmed to have only a subset of the possible Card Behaviours (see following section for a list of those behaviours).

> TODO: Determine RFID Card programming layout. CLI tool will be required.


#### Card Behaviours

| State   | Card  | Action  |
|:-:|:-:|---|
| Lights Off | Card touch  | Lights On (at previous brightness, colour). |
| Lights Off | Card touch >1s  | Lights Brightness (cycle preset brightness values each 1s). |
| Lights Brightness  | Card remove | Lights On. |
| Lights On | Card touch | Lights Off. |
| Lights On | Card touch >1s | Lights Colour (cycle preset colour values each 1s). |
| Lights Colour | Card remove | Lights On. |
