<p align="center"> 
<img src="https://raw.githubusercontent.com/binarycounter/PkSploit/master/pksploitlogo.png">
</p>

---
WARNING: UNDER HEAVY DEVELOPMENT!

BOOTLEG FLASH FUNCTION SOMEWHAT UNTESTED BECAUSE I WRECKED MINE WHILE TRYING TO SOLDER A BATTERY TO IT. WORKED BEFORE I KILLED IT THO :P

---


## TL;DR

This is a suite of tools allowing you to dump rom/save data and reflash save data on any GB and GBC cartridge using nothing but a Pokemon Gen 1 cart, a link cable and an Arduino compatible microcontroller (e.g. Arduino Nano or any ATmega368p board). 

Exploit and some arduino code based on: https://github.com/vaguilar/pokemon-red-cable-club-hack


## Features
* **All Gen 1 carts supported** *(I think)*: Tested on US Pokemon Red, German Pokemon Blue, French Pokemon Yellow. 
* **ROM dumping:** Play those classic games on an emulator without relying on virus-riddled (and illegal) ROM download sites. 
* **SRAM dumping:** Save your childhood save games from imminent battery doom.
* **SRAM writing:** Ever wanted to try out someone else's save game?
* **Write and execute code:** Try out your small gameboy programs on actual hardware!
* **Quick start without trading:** The included build script generates save files that directly jump into PkSploit's main routine after loading. Have your link up and running in only a few seconds! Those can (of course) be uploaded via PkSploit itself. 

*... And here's where it gets interesting ...*
* **Erase/Rewrite ROM on flash based bootlegs/flashcarts!** Replace the game completely with whatever ROM you want. (Special patches to support saving on carts without battery soon(TM))
#
 **Yes that means you can replace that crappy bootleg romhack with Pokemon Prism, LSDj, Nanoloop or whatever you want!**
 
 *Did i mention those bootlegs cost like 4 USD and basically replace a flashcart!?*
 *Did i also mention that the required hardware to do all of this costs less than 2 USD and is easy to build!?*

## How?
* The Arduino communicates with the Gameboy using the Link Port. It pretends to be another Gameboy running a Pokemon Gen 1 game, willing to trade. 
* When entering the trade, it sends corrupted party data which causes the gameboy to execute a chunk of the party data as code.
* The code can be made to do pretty much anything that fits in ~192 byte, but in this instance it's a routine that reopens the serial link to provide a interface that can be used to read/write to any part of memory within the Gameboy's limitations.
* Since the code is running in WRAM, you can cartswap to read/write to any gameboy cartridge. This works best on a Gameboy Color or Pocket, but should work on all gameboy platforms (better results when using a cheat device as passthrough. See FAQ)
* Overwriting the bootleg works because it uses flash memory instead of ROM. These flash chips have a special command interface allowing to erase sectors and reprogram them. I discovered that this interface is accessable within the gameboy when i was [debugging/reverse engineering](https://gist.github.com/binarycounter/9bd93ef4271a11aee3e395d04b93ed3a) how my Pokemon bootleg could save without a battery. (Hint: The rom is hacked to save to flash instead of SRAM ;))

## Hardware Prerequisites
* Arduino compatible microcontroller, preferably one with 5V logic and >16Mhz clock speed. (E.g. an Atmega326p)
* Gameboy DMG, Color, Pocket, Light, GBA, GBA SP... *Basically any Gameboy with a link port.*
* Link Cable or any other way to connect the Arduino to the Gameboy's Link Interface

## Software Prerequisites
* Python 2.7
* PySerial
* Arduino IDE
* RGBDS (Included)

## Hardware Build
*TODO. Basically cut a link cable in half and wire up 4 pins from it to the arduino.*
## Software Build
**Currently only builds on Windows, but there's no reason it shouldn't work on other OS (I'm just lazy)**
1. Install Prerequisites
2. Clone: `git clone http://github.com/binarycounter/pksploit` (Or just download the repository as a zip)
3. Enter build directory: `cd PkSploit/build/`
4. Copy `sample_config.ini` to `config.ini` and edit your path, board name and port.
5. Build: `py build.py`
6. Enter python directory: `cd ../python/`
7. Run: `py pksploit.py`

## FAQ
*Q: My bootleg doesn't save when i write to SRAM!*

**A: Your bootleg likely doesn't include a battery and instead relies on patching the ROM to backup SRAM into flash. In some Pokemon bootlegs you can call `$3FA6` to trigger the routine that does this. For other bootleg games... I don't know. If you send me a tracelog or a romdump/patch i'll let you know if i can support it!**

*Q: My gameboy keeps crashing or restarting when I attempt cartswapping!*

**A: How many times did you try it? It can take me up to 10 times (on a bad day) before i successfully cartswap. Use the hacked save files to make attempts faster!**

*Q: My gameboy still keeps crashing!*

**A: Try a cheat device (e.g. Action Replay) as passthrough adapter. Those don't connect the RESET line between gameboy and cartridge. This prevents the gameboy from attempting to restart. You can also try putting tape over the 3rd Pin from the right, if you have more patience than me.** 

*Q: I looked into your code and.... what the....*

**A: Yes, i know. Bare with me, this is my first serious python project. Feel free to refactor this mess...;)**


## Planned Features

* Find and Port Code to other Link Cable related ACE exploits
* Make GBA version (exploiting multiboot) to allow dump/write/flash of GBA bootlegs.

---

**DISCLAIMER: I AM NOT RESPONSIBLE FOR ANYTHING, INCLUDING LOSS OF DATA, BROKEN GAMEBOYS, OR TEARS BECAUSE YOU ACCIDENTALLY OVERWRITE YOUR CHILDHOOD SAVE FILE WITH YOUR SICK 3 STARTER TEAM**

**I AM NOT AFFILIATED OR ENDORSED BY NINTENDO. THIS REPOSITORY DOES NOT CONTAIN NINTENDO OR GAMEFREAK CODE OR DATA**
