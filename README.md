# PkSploit
**WARNING: UNDER HEAVY DEVELOPMENT, LIKELY WONT WORK**
This is a suite of tools allowing you to dump rom/save data and reflash save data on any GB and GBC cartridge using nothing but a Pokemon Gen 1 cart, a link cable and an Arduino compatible microcontroller (e.g. Arduino Nano or any ATmega368p board).

## How?
The Arduino communicates with the Gameboy using the Link Port. It pretends to be another Gameboy running a Pokemon Gen 1 game, willing to trade. When entering the trade, it sends corrupted party data which causes the gameboy to execute a chunk of the party data as code.

Still setting up this repository...

