![Logo of the project](logo.jpg)

# LEGO Hub Toolkit
> Pythonic connector for the LEGO Mindstorms/Spike Prime robot hub (Linux, Mac, Windows)

The LEGO Mindstorms Robot Inventor kit (51515) is powered by a hub that contains a programmable micropython-based microprocessor.  The LEGO Hub Toolkit provides a python communications library that enables a PC to connect to the Hub using USB and/or Bluetooth.  On top of this communications library are some tools that let you monitor the reobot's sensors while it runs as well as to download, start, and stop programs on the hub. 

The toolkit fulfils a couple of use cases not provided by LEGO's tools.
1. Writing code for the robot using a linux or Mac PC.
1. Writing a custom application to monitor the robot state as it moves about the world.

The communications library is designed to maintain a connection with the hub, using either USB or Bluetooth with automatic switchover from USB to Bluetooth and vice-versa.  On top of the communications is a client layer that provides classes to encode and decode the hub messages and to maintain the hub state on the PC side.  The hub state includes the onboard gyroscope sensor values as well as the motors and sensors currently plugged into the hub's ports.  On top of the client layer are a couple of example applications to demonstrate monitoring and control.

The LEGO Spike Prime kit apparently uses the same hub -- this toolkit was inspired by and directly uses code for Spike Prime (see Acknowledgements, below).  As such, I expect much of the code to be usable with Spike Prime, though this has not been tested.


## Getting started

The example shell commands below are shown as for a linux shell command line.  

The toolkit is written in Python.  You will need Python installed (toolkit is currently developed using Python 3.9).  

Install pre-requisite Python packages.

```shell
pip3 install -r requirements.txt
```
Check if any errors during install they will need to be corrected before proceeding.

for notes on  returements for debian/raspberry-pi see section below.

Connect the hub using USB.  

List the programs currently stored on the hub:

```shell
python3 run_command.py ls
Slot Decoded Name                               Size Last Modified        Project_id   Type      
   0 Zero motors                                733b 2020-12-30 04:02:45  lmlJdiW3kVR2 scratch   
   1 MR1 - Line Follower                       3641b 2020-12-31 17:47:18  T8g7vJ4jYExt python    
   2 MR1 - Wanderer                            2650b 2020-12-31 17:47:49  GzcKr5xPBJrQ python    
   3 MR1 - Connect the Dots                    4375b 2021-01-01 02:11:06  Qm_0zJkWgkGM python    
   4 MR1 - Navigator 1                        13563b 2021-01-04 05:20:15  sUtzpgAokATv python    
   5 Project 3                                  128b 2021-01-02 18:52:18  bGz62LGIzCOl python    
   6 Guard my room 3                           8115b 2020-12-29 17:16:28  kDj0zNTjueJV scratch   
   8 Grab and move                             8949b 2020-12-30 03:49:16  V12C35ra2EdG scratch   
  10 Hi World                                    13b 2021-02-01 04:05:14  50uN1ZaRpHj2 python    
  11 Winner! 6                                 7226b 2020-12-29 22:00:17  cis5eAYFX5bd scratch   
```

## Configuration

Out of the box, the software uses the USB cable to connect to the hub.  It will automatically determine the correct USB device.  

If the auto-detection does not work on your system, or if you wish to use bluetooth, the connection can be specified by configuration file.

If using Bluetooth:
1. Pair the hub with your system.  Use your system's regular tool for doing this.
   - also see https://dwalton76.github.io/spikedev/repl.html
1. Obtain the hub's Bluetooth address -- likely using the same tool as in the previous step.  It will be in the form of six hexadecimal number separated by colons; e.g. 38:0B:3C:AA:B6:CE
   - darwin shell can provide a list `system_profiler SPBluetoothDataType`
   - linux `hciconfig` 

Create and edit the configuration file:

1. Locate the correct user_config_dir for your system (see https://pypi.org/project/appdirs/) and create a sub-directory named 'lego-hub-tk'.
   - For linux, this will be `mkdir ~/.config/lego-hub-tk/`
1. Copy the template file lego_hub.yaml to the newly-created directory.
   - For linix, this will be `cp lego_hub.yaml ~/.config/lego-hub-tk/lego_hub.yaml`
1. Edit your copy of lego_hub.yaml, following the notes in the template file.
   - For linix, this will be `nano ~/.config/lego-hub-tk/lego_hub.yaml`


## Features

### Runing code on the hub - command line

The python3 script `run_command.py` can
* list programs stored on the hub
* upload a program to the hub
* start a program on the hub
* stop the program currently running on the hub

Usage:
```shell
python3 run_program.py ls
python3 run_program.py cp myprogram.py 4
python3 run_program.py start 4
python3 run_program.py stop
```

### Runing code on the hub - GUI

The GUI program hubcontrol can be used to run a program on the hub and display the console output and status while it runs.  

### Monitoring running hub

The script hubstatus displays the live hub status.

Usage:
```shell
python3 hubstatus.py
```

A window should open displaying the hub status details of the connection type, on-board sensors (yaw, pitch, roll), and the status of the six ports (A-F).  The Hub Gesture value indicates when the hub is tapped, double-tapped, etc.

### Python scripting

See the [API Design documentation](design.md).

### Raspberry Pi 

the following is needed for linux, and raspberry-pi

```shell
sudo apt-get install bluetooth libbluetooth-dev
sudo python3 -m pip install pybluez
```

after all packages are confirmed installed you may need to add `export PATH="$HOME/bin:$PATH"`

## Contributing

If any the above instructions are unclear or incorrect, please do open an issue.

If you'd like to contribute, please fork the repository and use a feature
branch. Pull requests are warmly welcome.

Thanks to:
- Eric T. ([ws1088](https://github.com/ws1088)) for Mac & Windows support and many other improvements!
- Kelly ([SpudGunMan](https://github.com/SpudGunMan)) for design & doc suggestions

## Links

- Project homepage: https://github.com/smr99/lego-hub-tk
- Repository: https://github.com/smr99/lego-hub-tk
- Issue tracker: https://github.com/smr99/lego-hub-tk/issues
- Related LEGO hub projects:
  - Spike Tools: https://github.com/nutki/spike-tools
  - Spike Prime info and micropython decompiler: https://github.com/gpdaniels/spike-prime
  - Spike Prime Extension for VS Code https://github.com/sanjayseshan/spikeprime-vscode
  - Pybricks https://pybricks.com/
- Related MicroPython projects:
  - rshell (Remote MicroPython Shell): https://github.com/dhylands/rshell

### Acknowledgements

This project owes a particular debt of gratitude to several other open source projects.

#### [Remote MicroPython Shell](https://github.com/dhylands/rshell)

Provided the inspiration -- and the core pyudev code -- for USB autodetect.  Additionally, rshell was hugely helpful in exploring the on-board python Read-Evaluate-Print-Loop (REPL) and the hub's file structure.

#### [Spike Tools](https://github.com/nutki/spike-tools)

Provided the core code for decoding the JSON message structure.  The script run_command.py in this toolkit started as a copy of spikejsonrpc from spike tools, with the serial handling code replaced by the comm library.


## Licensing

The code in this project is licensed under MIT license.
