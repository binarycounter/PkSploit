<p align="center"> 
<img src="https://raw.githubusercontent.com/binarycounter/PkSploit/master/pksploitlogo.png">
</p>

---
**WARNING: UNDER HEAVY DEVELOPMENT, LIKELY WONT WORK! ALSO I'M STILL SETTING THIS REPOSITORY UP!**

**DISCLAIMER: I AM NOT RESPONSIBLE FOR ANYTHING, INCLUDING LOSS OF DATA, BROKEN GAMEBOYS, OR TEARS BECAUSE YOU ACCIDENTILLY OVERWROTE YOUR CHILDHOOD SAVE FILE WITH YOUR SICK 3 STARTER TEAM**

---

This is a suite of tools allowing you to dump rom/save data and reflash save data on any GB and GBC cartridge using nothing but a Pokemon Gen 1 cart, a link cable and an Arduino compatible microcontroller (e.g. Arduino Nano or any ATmega368p board). Exploit based on: https://github.com/vaguilar/pokemon-red-cable-club-hack

In the future this might be a cheap & dirty way to test code on hardware using a bootleg cartridge as permanent flash storage.

## How?
* The Arduino communicates with the Gameboy using the Link Port. It pretends to be another Gameboy running a Pokemon Gen 1 game, willing to trade. 
* When entering the trade, it sends corrupted party data which causes the gameboy to execute a chunk of the party data as code.
* The code can be made to do pretty much anything that fits in ~192 byte, but in this instance it's a routine that reopens the serial link to provide a interface that can be used to read/write to any part of memory within the Gameboy's limitations.
* (No writing to ROM obviously, but reprogramming flash based cartrigdes (e.g. bootlegs) may be possible in the future)

## Hardware Prerequisites
* Arduino Compatible Microcontroller
* Gameboy DMG, Color, Pocket, Light (Any gameboy up until GBA)

## Software Prerequisites
* Python 2.7
* PySerial
* Arduino IDE
* RGBDS

## Build

1. Install Prerequisites: `TODO`
2. Clone: `git clone http://github.com/binarycounter/pksploit`
3. Enter build directory: `cd PkSploit/build/`
4. Edit Config: `TODO`
5. Build: `py build.py`





## Planned Features

* Get everything ported over from old private codebase.
* Hex command to call an address
* Flash bootlegs? ([Still investigating](https://gist.github.com/binarycounter/9bd93ef4271a11aee3e395d04b93ed3a))
* Gameboy Advance?
* Find and Port Code to other Link Cable related ACE exploits


Still setting up this repository...


**I AM NOT AFFILIATED OR ENDORSED BY NINTENDO. THIS REPOSITORY DOES NOT CONTAIN NINTENDO OR GAMEFREAKS CODE OR DATA**
