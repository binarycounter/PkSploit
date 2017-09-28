import os
import sys
import serial
import threading 
import time
 

nintendologo="".join(map(chr,[0xCE,0xED,0x66,0x66,0xCC,0x0D,0x00,0x0B,0x03,0x73,0x00,0x83,0x00,0x0C,0x00,0x0D,0x00,0x08,0x11,0x1F,0x88,0x89,0x00,0x0E,0xDC,0xCC,0x6E,0xE6,0xDD,0xDD,0xD9,0x99,0xBB,0xBB,0x67,0x63,0x6E,0x0E,0xEC,0xCC,0xDD,0xDC,0x99,0x9F,0xBB,0xB9,0x33,0x3E]))
    

#Let's write some non flexible code first, just so that i have something to work on

ser = serial.Serial()
state = "none"
cmdstr=""
cmdpar1=0
cmdpar2=0
cmdpar3=0
cmdpar4=0
cmddone=False
cmdoutput=""

cartmbc=0
cartbanks=0
srambanks=0




def main():
    global state
    state="noserial"
    print "Waiting for Serial Port to Open... (If the program hangs here, close your Arduino Software)."
    ser.baudrate = 28800
    ser.port = 'COM3'
    ser.timeout = 0.01
    ser.open() 
    print "Connected"
    state="serialopen"
    serialprocess = threading.Thread(target = serialf)
    serialprocess.daemon = True
    serialprocess.start()
    print "Waiting for Arduino Reset. (Press the reset button on your arduino if this hangs)"
    while state!="arduinoconnected":
        time.sleep(0.1)
    print "Reset complete. Please initiate the trade on the gameboy."
    while state!="pksploit_menu":
        time.sleep(0.1)
        if state=="pksploit_mq":
            print "Trade already happened. Gameboy is already running PkSploit!"
            state="pksploit_menu"
    print "Giving the gameboy a few seconds to initialize..."
    time.sleep(2)


    interfaceprocess = threading.Thread(target = interfacef)
    interfaceprocess.daemon = True
    interfaceprocess.start()
    while True:
        time.sleep(1)

    



#Options:
# 1. Read/Verify Rom Header.
# 2. Read entire Rom (will block if header seems corrupted / check nintendo logo?)
# 3. Read entire SRAM
# 4. Read Custom Block of memory
# 5. Restart (Jump to $1f54)



def interfacef():
    global cmdoutput, state
    while True:
        choice=""
        while choice not in range(1,5):
            print "---------------------------"
            print "What do you want to do?"
            print ""
            print "1. Display And Verify Header"
            print "2. Dump ROM"
            print "3. Dump SRAM"
            print "4. Dump Custom Block"
            print ""
            print "9. Exit"
            try:
    	        choice = int(raw_input('--> '))
    	        if choice == 9:
    		        sys.exit(0)
            except SystemExit:
    	        sys.exit(0)
            except:
    	        print "Invalid Number"
    	        choice = 0

        if choice == 1:
            verifyheader()
        if choice == 2:
            dumprom()
        if choice == 3:
            dumpsram()
        if choice == 4:
            dumpcustom()
         



def verifyheader():
    global cmdoutput, nintendologo, cartmbc, cartbanks, srambanks
    command("dump",0x00,0x50,0x01,0x00) #Dump $50 bytes at address $0100    
    if cmdoutput[4:-28]!=nintendologo:
        print "Nintendo logo doesn't match."
        print "Cartridge possibly drity or broken."
        return False
    else:
        print "Cart has a valid Nintendo Logo in the header"
    print "Cart name: "+cmdoutput[52:-12]
    
    if ord(cmdoutput[67:-12]) == 0x80:
        print "Cart has Gameboy Color enhancements"
    if ord(cmdoutput[67:-12]) == 0xC0:
        print "Cart Is a Gameboy Color Exclusive"
    
    if ord(cmdoutput[70:-9]) == 0x03:
        print "Cart has Super Gameboy enhancements"
    if ord(cmdoutput[74:-5]) == 0x00:
        print "Cart is a Japanese exclusive"
    if ord(cmdoutput[74:-5]) == 0x01:
        print "Cart is a Non-Japanese exclusive"
    print "Cart Type: "+str(ord(cmdoutput[71:-8]))
    cartmbc=ord(cmdoutput[71:-8])
    print "ROM Size: "+str(ord(cmdoutput[72:-7]))
    cartbanks=ord(cmdoutput[72:-7])
    print "RAM Size: "+str(ord(cmdoutput[73:-6]))
    srambanks=ord(cmdoutput[73:-6])

    print "Header dump ($100-$150):"
    print " ".join("{:02x}".format(ord(c)) for c in cmdoutput)

    
    return True

def dumprom():
    i=0
    banks=32 #32banks for this test

    if verifyheader()==False:
        print "Header is broken, aborted dump."
        return False
    rom=""
    command("dump",0x40,0x00,0x00,0x00)
    rom=cmdoutput
    i+=1
    print "Dumped "+str(i) +"/"+str(banks)+ " Banks."
    while i < banks:
        command("setbyte",0x20,0x00,i,0x00)
        command("dump",0x40,0x00,0x40,0x00)
        rom+=cmdoutput
        i+=1
        print "Dumped "+str(i) +"/"+str(banks)+ " Banks."

    print "Rom dump complete"
    fo = open("rom.gb", "wb")
    fo.write(rom)
    fo.close()
    return rom
    

def dumpsram():
    print "stub"

def dumpcustom():
    print "stub"


def serialf():
    global ser, state, cmdstr, cmdpar1, cmdpar2, cmdpar3, cmdpar4, cmddone, cmdoutput
    buf=""

    while True:
        buf+=ser.read(1)
        if state == "serialopen":
            if "Boot complete" in buf:
                state="arduinoconnected"
                buf=""
                time.sleep(1) #Giving the arduino some time to init
        if state == "arduinoconnected":
            if "StatusConnected" in buf:
                print "Link established"
                buf=""
            if "StatusMQ" in buf:
                state="pksploit_mq"
                buf=""
            if "StatusTradeCenter" in buf:
                print "Gameboy selected Trade Center"
                buf=""
            if "StatusSending" in buf:
                print "Sending data..."
                buf=""
            if "StatusMenu" in buf:
                state="pksploit_menu"
                buf=""
        if state == "pksploit_menu":
            #wait for commands
            time.sleep(0.10)
            if cmdstr == "setcounter":
                ser.write(chr(0x11)) #Arduino command HEX 11: Set internal counter
                ser.write(chr(cmdpar1))
                ser.write(chr(cmdpar2))
                buf=""
                cmdstr=""
                cmdoutput=""
                cmddone=True
            if cmdstr == "setbyte":
                ser.write(chr(0xAA))
                ser.write(chr(cmdpar1))
                ser.write(chr(cmdpar2))
                ser.write(chr(cmdpar3))
                buf=""
                cmdstr=""
                cmdoutput=""
                time.sleep(0.1)
                cmddone=True

            if cmdstr == "dump":
                ser.write(chr(0x11)) #Arduino command HEX 11: Set internal counter
                ser.write(chr(cmdpar1))
                ser.write(chr(cmdpar2))
                time.sleep(0.10)
                ser.write(chr(0x22)) #Arduino command HEX 22: Set block mode to "dump" 
                ser.write(chr(0x55)) #PkSploit Command HEX 55: Block transfer
                ser.write(chr(cmdpar1)) #High byte of byte number
                ser.write(chr(cmdpar2)) #Low byte of byte number
                ser.write(chr(cmdpar3)) #High byte of start address
                ser.write(chr(cmdpar4)) #Low Byte of start address
                buf=""
                
                while "StatusMenu" not in buf:
                    buf+=ser.read(1)
                    
                    if len(buf) % 10==0:
                        print ".",
                print "."
                cmdoutput=buf[:-11]
                cmdstr=""
                cmddone=True
            

                
                

            
def command(cmd,p1,p2,p3,p4):
    #Small helper function that wraps the serial loop
    global cmdstr, cmddone, cmdpar1, cmdpar2, cmdpar3, cmdpar4
    
    cmdstr=cmd
    cmdpar1=p1
    cmdpar2=p2
    cmdpar3=p3
    cmdpar4=p4    

    while cmddone==False:
        time.sleep(0.10)
    time.sleep(0.10)
    cmddone=False
    return




    


main()

