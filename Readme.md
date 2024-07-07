# Lego-Spike-Prime-OPCUA

This repo showcases an example how to utilize Lego Spike Prime engines and 
sensors together with OPC UA.

## How to get the station running

- Setup a Raspberry Pi (I am using a Model 3B+)
- assemble the buildHAT as described in the manual
- connect a
    - Lego Force Sensor to buildHAT Port A
    - Lego Servo Motor to buildHAT Port C
    - Lego Light Matrix to buildHAT Port D
- connect via ssh to the RaspberryPI and follow some steps below

```bash
# Install dependencies
sudo apt install python3-build-hat

# Clone this repo and run the OPCUA server & station logic
git clone https://github.com/Spansky/lego-spike-prime-opcua.git 
cd lego-spike-prime-opcua
make run
```

## Project Structure

In /src you will find following files:

- station.py
    - establishes connection to the buildHAT and the connected devices/sensors
    - runs station internal logic, e.g. reacting on force sensor input, color 
    led matrix

- opcuaserver.py
    - runs a OPCUA server using module 
    [asyncua](https://github.com/FreeOpcUa/opcua-asyncio) 

- main.py - Runs two async processes
    - opcuaserver
    - some station logic

## Blog Post

This repo accompanies a blog post that I wrote on LinkedIn.
[Blog Post](https://www.linkedin.com/pulse/making-opcua-fun-lego-turning-complex-technology-leon-sczepansky-jrkee/)

...to be continued...

