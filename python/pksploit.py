#!python2
import os
import sys
if (sys.version_info > (3, 0)):
    print("This script is for Python 2.x only. Sorry about that :/")
    exit(1)
import serial
import threading 
import time
import Tkinter, tkFileDialog
import constants

#Let's define some stuff

ser = serial.Serial()

ser.baudrate = 28800
ser.port = constants.port
ser.timeout = 0.05

state = "none"
cmdstr=""
cmdpar1=0
cmdpar2=0
cmdpar3=0
cmdpar4=0
cmddone=False
cmdoutput=""
lcdon=True
mq=False

#Change to 0xA9 and 0x56 if bootleg flash functions don't work
valAA=0xAA
val55=0x55


root = Tkinter.Tk()
root.withdraw()

cartmbc=0
cartbanks=0
cartsrambanks=0
cartname=""



def main():
    global state, mq
    state="noserial"

    print "Waiting for Serial Port to Open... (If the program hangs here, close your Arduino Software)."

    
    ser.open() #Open Serial Connection (This blocks until port is open)

    print "Serial port opened."

    state="serialopen" #Signal state of the port to serial handler

    #Start serial handler thread
    serialprocess = threading.Thread(target = serialf)
    serialprocess.daemon = True
    serialprocess.start()

    print "Waiting for Arduino Reset. (Press the reset button on your arduino if this hangs)"

    while state!="arduinoconnected":    #Block until serial thread signals that the arduino is ready
        time.sleep(0.1)
    
    print "Reset complete. Please initiate the trade (or load the prepared save file) on the gameboy."

    while state!="pksploit_menu":   #Block until serial thread signals that Gameboy loaded PkSploit
        time.sleep(0.1)
        if state=="pksploit_mq":    #Special case for when the gameboy is already running PkSploit without trading (e.g from a rom, or after a restart)
            print "Quick Menu triggered. Gameboy is already running PkSploit!"
            state="pksploit_menu"
            mq=True
    print "Initializing..."
    

    #Start Cli interface thread
    interfaceprocess = threading.Thread(target = interfacef)
    interfaceprocess.daemon = True
    interfaceprocess.start()
    while True:
        time.sleep(1)

    



#Main cli interface
def interfacef():
    global cmdoutput, state, mq
    if mq == False:
        time.sleep(2)
    initpksploit()
    while True:
        choice=""
        while choice not in range(1,20):
            print "---------------------------"
            print "What do you want to do?"
            print ""
            print "1. Display And Verify Header    5. Write SRAM (Deletes Save)     9.  Bootleg/FC: Erase Flash"
            print "2. Dump ROM                     6. Write Byte                    10. Bootleg/FC: Flash ROM"
            print "3. Dump SRAM                    7. Call address                  11. Bootleg/FC: Flash Byte"
            print "4. Dump Custom Block            8. Restart Gameboy (Call $100)   12. Toggle LCD"
            print " "
            print "0. Exit"
            
                            
            
            try:
    	        choice = int(raw_input('--> '))
    	        if choice == 0:
    		        sys.exit(0)
            except SystemExit:
    	         os._exit(1)
            except:
    	        print "Invalid Number"
    	        choice = 0

        options =  {1: verifyheader,
                    2: dumprom,
                    3: dumpsram,
                    4: dumpcustom,
                    5: writesram,
                    6: writebyte,
                    7: jumpto,
                    8: restartgb,
                    9: eraseflash,
                    10:flashrom,
                    11:flashbyte,
                    12:togglelcd,
                    13:flashexperiment,
                    14:flashromexpe,
                    15:teststuff}
        
        options[choice]()
        
        
        
def initpksploit():
    
    command("setbyte",0xFF,0x26,0x00,0x00) #Mute Sound
    command("turnofflcd",0,0,0,0)
    #command("send",0x9C,0x00,constants.pksploitlogo,constants.modeWrite)   
    command("turnonlcd",0,0,0,0)
    command("setbyte",0x00,0x00,0x00,0x00) #Disable SRAM access for safety reasons
    command("setbyte",0xFF,0xF1,constants.modeRead,0x00) #Disable writing for safety reasons
    command("setbyte",0xFF,0xF0,0x00,0x00) #Let's speed this bi--- up
    return
def verifyheader():
    #Header information from http://gbdev.gg8.se/wiki/articles/The_Cartridge_Header
    #This doesn't actually verify the checksum, only the logo. But i figured, if 48 byte in a row are dumped correctly, the cart is probably working.
    global cmdoutput, nintendologo, cartmbc, cartbanks, srambanks, cartname, cartsrambanks
    command("dump",0x00,0x50,0x01,0x00) #Dump $50 bytes at address $0100    
    if cmdoutput[4:-28]!=constants.nintendologo: #Check if logo on the cart matches nintendo logo 
        print "Nintendo logo doesn't match."
        print "Cartridge possibly drity or broken."
        print "Header dump ($100-$150):"
        print " ".join("{:02x}".format(ord(c)) for c in cmdoutput)
        return False #Return false if it doesn't. Stops rom dump functions from dumping invalid roms
    else:
        print "Cart has a valid Nintendo Logo in the header"
    print "Cart name: "+cmdoutput[52:-12]
    cartname=cmdoutput[52:-12]
    
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
    print "ROM Size: "+str(constants.rombanks[ord(cmdoutput[72:-7])]*16)+ "KB / " + str(constants.rombanks[ord(cmdoutput[72:-7])])+ " Banks"
    cartbanks=constants.rombanks[ord(cmdoutput[72:-7])]

    if ord(cmdoutput[73:-6]) == 0:
        print "RAM Size: 0KB (Cart doesn't have SRAM)"
    else: 
        if ord(cmdoutput[73:-6]) == -1:
            print "RAM Size: 2KB / 1 Bank (Only 1/4th of the bank is mapped)"
        else:
            print "RAM Size: " + str(constants.srambanks[ord(cmdoutput[73:-6])]*8) + "KB / " + str(constants.srambanks[ord(cmdoutput[73:-6])]) + " Bank(s)"
        
    cartsrambanks=constants.srambanks[ord(cmdoutput[73:-6])]

    print "Header dump ($100-$150):"
    print " ".join("{:02x}".format(ord(c)) for c in cmdoutput)

    
    return True

def dumprom():
    global root, cartname, cartbanks
  
    if verifyheader()==False:
        print "Header is broken, aborted dump."
        return False
    print "Validated header."
    file_path = tkFileDialog.asksaveasfilename(defaultextension=".gb", initialfile=''.join(e for e in cartname if e.isalnum())+".gb") #Get filename to write
    if file_path == "None" or file_path == "":
        return False
    fo = open(file_path, "wb")
    rom=""
    banks=cartbanks #Get number of banks 
    i=0
    command("setbyte",0xFF,0xF0,0x00,0x00)
    command("dump",0x40,0x00,0x00,0x00)
    rom=cmdoutput
    fo.write(cmdoutput)
    i+=1
    print "Dumped "+str(i) +"/"+str(banks)+ " Banks."
    while i < banks:
        command("setbyte",0xFF,0xF0,0x00,0x00)
        command("setbyte",0x20,0x00,i,0x00)
        command("dump",0x40,0x00,0x40,0x00)
        rom+=cmdoutput
        fo.write(cmdoutput)
        fo.flush()
        os.fsync(fo)
        i+=1
        print "Dumped "+str(i) +"/"+str(banks)+ " Banks."

    print "Rom dump complete"
    
    
    fo.close()
    return rom
    

def dumpsram():
    global root, cartname, cartsrambanks
    
    if verifyheader()==False:
        print "Header is broken, aborted dump."
        return False
    print "Validated header."
    
    banks=cartsrambanks 
    if banks == 0:
        print "No SRAM detected. aborted dump."
        return False

    file_path = tkFileDialog.asksaveasfilename(defaultextension=".sav", initialfile=''.join(e for e in cartname if e.isalnum())+".sav")
    if file_path == "None" or file_path == "":
        return False
    fo = open(file_path, "wb")
    sram=""
    command("setbyte",0x00,0x00,0x0a,0x00) #Enable SRAM
    if banks == -1:
        print "2KB SRAM dumping not supported yet."
    else:
        i=0
        while i < banks:
            i+=1
            
            command("setbyte",0x40,0x00,i-1,0x00) #Switch SRAM Bank
            command("dump",0x20,0x00,0xa0,0x00)
            sram=cmdoutput
            fo.write(cmdoutput)
            fo.flush()
            os.fsync(fo)
            print "Dumped "+str(i) +"/"+str(banks)+ " Banks."

        command("setbyte",0x00,0x00,0x00,0x00) #Disable SRAM
    print "SRAM dump complete"
    
    
    fo.close()
    return sram

def dumpcustom():
    a1 = int(raw_input('Start Address (High Byte)> '), 16)
    a2 = int(raw_input('Start Address (Low Byte)> '), 16)
    c1 = int(raw_input('Amount of bytes (High Byte)> '), 16)
    c2 = int(raw_input('Amount of bytes (Low Byte)> '), 16)
    command("dump",c1,c2,a1,a2)
    print " ".join("{:02x}".format(ord(c)) for c in cmdoutput)


def writesram():
    global root, cartname, cartsrambanks
    
    if verifyheader()==False:
        print "Header is broken, aborted write."
        return False
    print "Validated header."
    
    banks=cartsrambanks 
    if banks == 0:
        print "No SRAM detected. aborting write."
        return False

    file_path = tkFileDialog.askopenfilename(defaultextension=".sav", initialfile=''.join(e for e in cartname if e.isalnum())+".sav")
    if file_path == "None" or file_path == "":
        return False
    fo = open(file_path, "rb")
    save = fo.read()
    sram=""
    
    command("setbyte",0x00,0x00,0x0a,0x00) #Enable SRAM
    
    if banks == -1:
        print "2KB SRAM writing not supported yet."
    else:
        i=0
        while i < banks:
            i+=1
            
            data=save[0+(i-1)*8192:8192+(i-1)*8192]
            command("setbyte",0x00,0x00,0x0a,0x00) #Enable SRAM          
            command("setbyte",0x40,0x00,i-1,0x00) #Switch SRAM Bank   

            #TODO make this mess into a loop        
            command("send",0xA0,0x00,data[0:1024],constants.modeWrite)            
            command("send",0xA4,0x00,data[1024:2048],constants.modeWrite)           
            command("send",0xA8,0x00,data[2048:3072],constants.modeWrite)            
            command("send",0xAC,0x00,data[3072:4096],constants.modeWrite)            
            command("send",0xB0,0x00,data[4096:5120],constants.modeWrite)            
            command("send",0xB4,0x00,data[5120:6144],constants.modeWrite)            
            command("send",0xB8,0x00,data[6144:7168],constants.modeWrite)
            command("send",0xBC,0x00,data[7168:8192],constants.modeWrite)
            
            
        
            print "Wrote "+str(i) +"/"+str(banks)+ " Banks."
        command("setbyte",0xFF,0xF1,constants.modeRead,0x00) #Disable Writing
        command("setbyte",0x00,0x00,0x00,0x00) #Disable SRAM
    print "SRAM write complete"
    
    
    fo.close()
    return


def writebyte():
    a1 = int(raw_input(' Address (High Byte)> '), 16)
    a2 = int(raw_input(' Address (Low Byte)> '), 16)
    b = int(raw_input('Byte to be written> '), 16)
    command("setbyte",a1,a2,b,0x00)
    return

def jumpto():
    a1 = int(raw_input(' Address (High Byte)> '), 16)
    a2 = int(raw_input(' Address (Low Byte)> '), 16)
    command("jump",a1,a2,0,0)
    print "Jumped. PkSploit will be unresponsive until the Gameboy returns. (If it ever does)"
    return

def restartgb():
    command("jump",0x01,0x00,0,0)
    print "Restarted gameboy, exiting PkSploit."
    os._exit(1)
    return

def eraseflash():
    command("setbyte",0x21,0x00,0x00,0x00)
    command("setbyte",0x0A,0xAA,valAA,0x00)
    command("setbyte",0x05,0x55,val55,0x00)
    command("setbyte",0x0A,0xAA,0x80,0x00)
    command("setbyte",0x0A,0xAA,valAA,0x00)
    command("setbyte",0x05,0x55,val55,0x00)
    command("setbyte",0x0a,0xaa,0x10,0x00)
    print "Erasing flash..."
    print "This can take up to 30 seconds, so let's wait that long."
    time.sleep(30)
    return

def flashrom():
    print "Not yet implemented, sorry :/"
    return

def togglelcd():
    global lcdon
    if lcdon == True:
        command("turnofflcd",0,0,0,0)
        print "LCD off."
    else:
        command("turnonlcd",0,0,0,0)
        print "LCD on."
    return

def teststuff():
    data=constants.data[0:1024]
    c=chr(len(data) / 256)
    print "{:02x}".format(ord(c))
    c=chr(len(data) % 256)
    print "{:02x}".format(ord(c))
    return

def flashromexpe():
    global cmdoutput
    #data="".join(map(chr,[0xAF,0xEA,0x05,0xC0,0xFA,0x05,0xC0,0xA7,0xC0,0x76,0x00,0x18,0xF7,0xFF,0xFF,0xFF,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xC3,0x40,0xC2,0xFF,0xFF,0xFF,0xFF,0xFF,0xC3,0x43,0xC2,0xFF,0xFF,0xFF,0xFF,0xFF,0xD9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xD9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xD9,0x21,0x01,0xC0,0x01,0xFF,0x1F,0x18,0x0E,0x21,0x00,0x98,0x01,0x00,0x08,0x18,0x06,0x21,0x00,0x80,0x01,0x00,0x20,0xAF,0xC3,0x1C,0x0C,0xF5,0xF0,0x41,0xE6,0x02,0x28,0xFA,0xF0,0x41,0xE6,0x02,0x20,0xFA,0xF1,0xC9,0x3E,0x20,0xE0,0x00,0xF0,0x00,0xF0,0x00,0x2F,0xE6,0x0F,0xCB,0x37,0x47,0x3E,0x10,0xE0,0x00,0xF0,0x00,0xF0,0x00,0xF0,0x00,0xF0,0x00,0xF0,0x00,0xF0,0x00,0x2F,0xE6,0x0F,0xB0,0x47,0xFA,0x03,0xC0,0xA8,0xA0,0xEA,0x02,0xC0,0x78,0xEA,0x03,0xC0,0x3E,0x30,0xE0,0x00,0xC9,0xF0,0x40,0xCB,0x7F,0xC2,0x53,0x0F,0x11,0x00,0x98,0x06,0x12,0x0E,0x14,0x2A,0x12,0x13,0x0D,0x20,0xFA,0x0E,0x14,0x7B,0xC6,0x0C,0x30,0x01,0x14,0x5F,0x05,0x20,0xEE,0xC9,0x11,0x00,0x98,0x06,0x12,0x0E,0x14,0x2A,0xD6,0x20,0x12,0x13,0x0D,0x20,0xF8,0x0E,0x14,0x7B,0xC6,0x0C,0x30,0x01,0x14,0x5F,0x05,0x20,0xEC,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0x00,0xC3,0x50,0x01,0xCE,0xED,0x66,0x66,0xCC,0x0D,0x00,0x0B,0x03,0x73,0x00,0x83,0x00,0x0C,0x00,0x0D,0x00,0x08,0x11,0x1F,0x88,0x89,0x00,0x0E,0xDC,0xCC,0x6E,0xE6,0xDD,0xDD,0xD9,0x99,0xBB,0xBB,0x67,0x63,0x6E,0x0E,0xEC,0xCC,0xDD,0xDC,0x99,0x9F,0xBB,0xB9,0x33,0x3E,0x42,0x4F,0x54,0x42,0x20,0x49,0x4E,0x56,0x49,0x54,0x45,0x00,0x00,0x00,0x00,0x00,0x44,0x53,0x00,0x19,0x00,0x00,0x01,0x33,0x00,0xED,0x90,0xC0,0xF5,0xF3,0xCD,0x61,0x00,0x3E,0x5D,0xEA,0x00,0xC0,0x3E,0xD9,0xEA,0x40,0xC2,0xEA,0x43,0xC2,0x3E,0x01,0xE0,0xFF,0xFB,0x21,0xA0,0xC2,0x11,0x04,0x01,0x06,0x30,0x1A,0x13,0xD5,0x5F,0xCD,0xDC,0x01,0xCB,0x33,0xCD,0xDC,0x01,0xD1,0x05,0x20,0xF0,0x21,0xA0,0xC2,0x11,0x10,0x80,0x0E,0x10,0x2A,0x47,0xF0,0x41,0xE6,0x02,0x20,0xFA,0x1A,0x13,0xB8,0x20,0x05,0x0D,0x20,0xF0,0x18,0x05,0x3E,0x01,0xEA,0x04,0xC0,0xF1,0xFE,0x11,0xC2,0x5C,0x03,0x3E,0x01,0xEA,0x04,0xC0,0xF0,0x44,0xFE,0x90,0x20,0xFA,0xAF,0xE0,0x40,0x01,0x00,0x04,0x21,0xDA,0x10,0x11,0x00,0x80,0xCD,0x72,0x0E,0x21,0xF4,0x01,0xCD,0xDF,0x00,0x3E,0xE4,0xE0,0x47,0xEE,0x75,0xE0,0x40,0xFB,0xCD,0x8A,0x00,0xFA,0x02,0xC0,0xCB,0x47,0xC2,0x5C,0x03,0x76,0x00,0x18,0xF1,0xAF,0x16,0x04,0x4B,0x07,0x07,0xCB,0x21,0x30,0x02,0xC6,0x03,0x15,0x20,0xF5,0x22,0x36,0x00,0x23,0x22,0x36,0x00,0x23,0xC9,0x20,0x20,0x20,0x20,0x21,0x20,0x57,0x41,0x52,0x4E,0x49,0x4E]))
    #data=[0xAF,0xEA,0x05,0xC0,0xFA,0x05,0xC0,0xA7,0xC0,0x76,0x00,0x18,0xF7,0xFF,0xFF,0xFF,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xC3,0x40,0xC2,0xFF,0xFF,0xFF,0xFF,0xFF,0xC3,0x43,0xC2,0xFF,0xFF,0xFF,0xFF,0xFF,0xD9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xD9,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xD9,0x21,0x01,0xC0,0x01,0xFF,0x1F,0x18,0x0E,0x21,0x00,0x98,0x01,0x00,0x08,0x18,0x06,0x21,0x00,0x80,0x01,0x00,0x20,0xAF,0xC3,0x1C,0x0C,0xF5,0xF0,0x41,0xE6,0x02,0x28,0xFA,0xF0,0x41,0xE6,0x02,0x20,0xFA,0xF1,0xC9,0x3E,0x20,0xE0,0x00,0xF0,0x00,0xF0,0x00,0x2F,0xE6,0x0F,0xCB,0x37,0x47,0x3E,0x10,0xE0,0x00,0xF0,0x00,0xF0,0x00,0xF0,0x00,0xF0,0x00,0xF0,0x00,0xF0,0x00,0x2F,0xE6,0x0F,0xB0,0x47,0xFA,0x03,0xC0,0xA8,0xA0,0xEA,0x02,0xC0,0x78,0xEA,0x03,0xC0,0x3E,0x30,0xE0,0x00,0xC9,0xF0,0x40,0xCB,0x7F,0xC2,0x53,0x0F,0x11,0x00,0x98,0x06,0x12,0x0E,0x14,0x2A,0x12,0x13,0x0D,0x20,0xFA,0x0E,0x14,0x7B,0xC6,0x0C,0x30,0x01,0x14,0x5F,0x05,0x20,0xEE,0xC9,0x11,0x00,0x98,0x06,0x12,0x0E,0x14,0x2A,0xD6,0x20,0x12,0x13,0x0D,0x20,0xF8,0x0E,0x14,0x7B,0xC6,0x0C,0x30,0x01,0x14,0x5F,0x05,0x20,0xEC,0xC9,0xFF,0xFF,0xFF,0xFF,0xFF,0x00,0xC3,0x50,0x01,0xCE,0xED,0x66,0x66,0xCC,0x0D,0x00,0x0B,0x03,0x73,0x00,0x83,0x00,0x0C,0x00,0x0D,0x00,0x08,0x11,0x1F,0x88,0x89,0x00,0x0E,0xDC,0xCC,0x6E,0xE6,0xDD,0xDD,0xD9,0x99,0xBB,0xBB,0x67,0x63,0x6E,0x0E,0xEC,0xCC,0xDD,0xDC,0x99,0x9F,0xBB,0xB9,0x33,0x3E,0x42,0x4F,0x54,0x42,0x20,0x49,0x4E,0x56,0x49,0x54,0x45,0x00,0x00,0x00,0x00,0x00,0x44,0x53,0x00,0x19,0x00,0x00,0x01,0x33,0x00,0xED,0x90,0xC0,0xF5,0xF3,0xCD,0x61,0x00,0x3E,0x5D,0xEA,0x00,0xC0,0x3E,0xD9,0xEA,0x40,0xC2,0xEA,0x43,0xC2,0x3E,0x01,0xE0,0xFF,0xFB,0x21,0xA0,0xC2,0x11,0x04,0x01,0x06,0x30,0x1A,0x13,0xD5,0x5F,0xCD,0xDC,0x01,0xCB,0x33,0xCD,0xDC,0x01,0xD1,0x05,0x20,0xF0,0x21,0xA0,0xC2,0x11,0x10,0x80,0x0E,0x10,0x2A,0x47,0xF0,0x41,0xE6,0x02,0x20,0xFA,0x1A,0x13,0xB8,0x20,0x05,0x0D,0x20,0xF0,0x18,0x05,0x3E,0x01,0xEA,0x04,0xC0,0xF1,0xFE,0x11,0xC2,0x5C,0x03,0x3E,0x01,0xEA,0x04,0xC0,0xF0,0x44,0xFE,0x90,0x20,0xFA,0xAF,0xE0,0x40,0x01,0x00,0x04,0x21,0xDA,0x10,0x11,0x00,0x80,0xCD,0x72,0x0E,0x21,0xF4,0x01,0xCD,0xDF,0x00,0x3E,0xE4,0xE0,0x47,0xEE,0x75,0xE0,0x40,0xFB,0xCD,0x8A,0x00,0xFA,0x02,0xC0,0xCB,0x47,0xC2,0x5C,0x03,0x76,0x00,0x18,0xF1,0xAF,0x16,0x04,0x4B,0x07,0x07,0xCB,0x21,0x30,0x02,0xC6,0x03,0x15,0x20,0xF5,0x22,0x36,0x00,0x23,0x22,0x36,0x00,0x23,0xC9,0x20,0x20,0x20,0x20,0x21,0x20,0x57,0x41,0x52,0x4E,0x49,0x4E]
    
    #tetris as testrom
    file_path = tkFileDialog.askopenfilename(defaultextension=".gb", initialfile=''.join(e for e in cartname if e.isalnum())+".gb")
    if file_path == "None" or file_path == "":
        return False
    fo = open(file_path, "rb")
    data = fo.read()

    # for num,bb in enumerate(data):
    #     #command("setbyte",0x21,0x00,0x00,0x00)
    #     command("setbyte",0x0A,0xAA,valAA,0x00)
    #     command("setbyte",0x05,0x55,val55,0x00)
    #     command("setbyte",0x0A,0xAA,0xA0,0x00)
    #     command("setbyte",0x00+num / 256,num % 256,bb,0x00)
    #     print ".",
    #     time.sleep(0.05)
    # time.sleep(2)
    # command("setbyte",0xFF,0xF2,0x00,0x00)
    # command("setbyte",0xFF,0xF1,0xFF,0x00)
    
    time.sleep(1)
    amount=len(data)
    steps=1024
    i=0
    j=0
    while i < amount:
        print i,
        print ":",
        print i / 256,
        print "-",
        print i % 256, 
        command("setbyte",0xFF,0xF2, i / 16384 ,0x00)
        command("send",j , i % 256,data[i:i+steps],constants.modeFlash) 
        i=i+steps 
        print i 
        j=j+4
        if j==128:
            j=64
        time.sleep(0.2)
    # command("setbyte",0x21,0x00,0x00,0x00)
    # time.sleep(0.2)         
    # command("send",0x04,0x00,data[1024:2048],constants.modeFlash)           
    # time.sleep(1)
    # command("setbyte",0x21,0x00,0x00,0x00)
    # time.sleep(0.2)
    # command("send",0x08,0x00,data[2048:3072],constants.modeFlash)            
    # time.sleep(1)
    # command("setbyte",0x21,0x00,0x00,0x00)
    # time.sleep(0.2)
    # command("send",0x0C,0x00,data[3072:4096],constants.modeFlash)            
    # time.sleep(1)
    # command("setbyte",0x21,0x00,0x00,0x00)
    # time.sleep(0.2)
    # command("send",0x10,0x00,data[4096:5120],constants.modeFlash)            
    # time.sleep(1)
    # command("setbyte",0x21,0x00,0x00,0x00)
    # time.sleep(0.2)
    # command("send",0x14,0x00,data[5120:6144],constants.modeFlash)            
    # time.sleep(1)
    # command("setbyte",0x21,0x00,0x00,0x00)
    # time.sleep(0.2)
    # command("send",0x18,0x00,data[6144:7168],constants.modeFlash)
    # time.sleep(1)
    # command("setbyte",0x21,0x00,0x00,0x00)
    # time.sleep(0.2)
    # command("send",0x1C,0x00,data[7168:8192],constants.modeFlash)


    time.sleep(5)
    command("dump",0x02,0x00,0x00,0x00)

    print " ".join("{:02x}".format(ord(c)) for c in cmdoutput)
    return
def flashexperiment(): #Don't use
    global cmdoutput
    # command("setbyte",0x21,0x00,0x00,0x00)
    # command("setbyte",0x0A,0xAA,0xA9,0x00)
    # command("setbyte",0x05,0x55,0x56,0x00)
    # command("setbyte",0x0A,0xAA,0x80,0x00)
    # command("setbyte",0x0A,0xAA,0xA9,0x00)
    # command("setbyte",0x05,0x55,0x56,0x00)
    # #command("setbyte",0x0a,0xaa,0x10,0x00)
    # command("setbyte",0x00,0x00,0x30,0x00)
    # time.sleep(1)
    
    #command("setbyte",0xFF,0xF2,0x00,0x00)
    #command("setbyte",0xFF,0xF1,0x03,0x00)

    #data="".join(map(chr,range(0,20)))
    #command("send",0x00,0x00,data,0x00)
    
    command("setbyte",0x0A,0xAA,0xA9,0x00)
    command("setbyte",0x05,0x55,0x56,0x00)
    command("setbyte",0x0A,0xAA,0xA0,0x00)
    command("setbyte",0x00,0xF3,0xEF,0x00)
    time.sleep(1)
    command("setbyte",0x0A,0xAA,0xA9,0x00)
    command("setbyte",0x05,0x55,0x56,0x00)
    command("setbyte",0x0A,0xAA,0xA0,0x00)
    command("setbyte",0x00,0xF2,0xBE,0x00)
    time.sleep(1)
    command("setbyte",0x0A,0xAA,0xA9,0x00)
    command("setbyte",0x05,0x55,0x56,0x00)
    command("setbyte",0x0A,0xAA,0xA0,0x00)
    command("setbyte",0x00,0xF0,0xDE,0x00)
    time.sleep(1)
    command("setbyte",0x0A,0xAA,0xA9,0x00)
    command("setbyte",0x05,0x55,0x56,0x00)
    command("setbyte",0x0A,0xAA,0xA0,0x00)
    command("setbyte",0x00,0xF1,0xAD,0x00)
    time.sleep(1)
    
    



    command("dump",0x00,0xFF,0x00,0x00)
    print " ".join("{:02x}".format(ord(c)) for c in cmdoutput)
    return

def flashbyte():
    a1 = int(raw_input('A1> '), 16)
    a2 = int(raw_input('A2> '), 16)
    b = int(raw_input('B> '), 16)
    command("setbyte",0x0A,0xAA,valAA,0x00)
    command("setbyte",0x05,0x55,val55,0x00)
    command("setbyte",0x0A,0xAA,0xA0,0x00)
    command("setbyte",a1,a2,b,0x00)
    return


def serialf():
    global ser, state, cmdstr, cmdpar1, cmdpar2, cmdpar3, cmdpar4, cmddone, cmdoutput, lcdon
    buf=""

    while True:
        buf+=ser.read(1)
       # print buf
        if state == "serialopen":
            if "Boot complete" in buf:
                state="arduinoconnected"
                buf=""
                time.sleep(0.2) #Giving the arduino some time to init
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
            time.sleep(0.05)
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
                cmddone=True
            if cmdstr == "turnofflcd":
                ser.write(chr(0x66))
                ser.write(chr(0x00))
                ser.write(chr(0x00))
                buf=""
                cmdstr=""
                cmdoutput=""
                lcdon=False
                cmddone=True
            if cmdstr == "turnonlcd":
                ser.write(chr(0xFF))
                ser.write(chr(0x40))
                ser.write(chr(0xE3))
                
                buf=""
                cmdstr=""
                cmdoutput=""
                lcdon=True
                cmddone=True
            if cmdstr == "jump":
                ser.write(chr(0x33))
                ser.write(chr(cmdpar1))
                ser.write(chr(cmdpar2))
                buf=""
                cmdstr=""
                cmdoutput=""
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
                buf=""
                cmddone=True
            if cmdstr == "send":
                ser.write(chr(0xAA)) #Setbyte command
                ser.write(chr(0xFF)) 
                ser.write(chr(0xF1)) #Address FFF1
                ser.write(chr(cmdpar4)) #Set Write mode (See constants.py)

                ser.write(chr(0xAA)) #Setbyte command
                ser.write(chr(0xFF)) 
                ser.write(chr(0xF0)) #Address FFF0
                ser.write(chr(0xFF)) #Set FF delay time to ensure data makes it to the gameboy uncorrupted
                time.sleep(0.10)
                #cmdpar3 is data to be sent
                ser.write(chr(0x11)) #Arduino command HEX 11: Set internal counter
                ser.write(chr(len(cmdpar3) / 256)) #High Byte of Byte counter 
                ser.write(chr(len(cmdpar3) % 256)) #Low Byte of Byte counter
                ser.write(chr(0x00))
                time.sleep(0.10)
                
                ser.write(chr(0x77))
                ser.write(chr(0xDE))
                ser.write(chr(0xAD))
                ser.write(chr(0xBE))
                ser.write(chr(0xEF)) # sync failsafe
                i=0
                while i <len(cmdpar3): # Fill buffer with bytes
                    ser.write(cmdpar3[i])
                    i=i+1
                    if i % 10==0:
                        print ".",
                curbyte=""


                while "StatusMQ" not in buf: #Wait for arduino to reconnect to gameboy after serial transfer
                    buf+=ser.read(1)
                    print buf
                buf=""

                
                
                
               
                ser.write(chr(0x44)) #Arduino command HEX 22: Set block mode to "send" 
                ser.write(chr(0x55)) #PkSploit Command HEX 55: Block transfer
                ser.write(chr(len(cmdpar3) / 256)) #High Byte of Byte counter 
                ser.write(chr(len(cmdpar3) % 256)) #Low Byte of Byte counter
                ser.write(chr(cmdpar1)) #High byte of start address
                ser.write(chr(cmdpar2)) #Low Byte of start address
                while "StatusMenu" not in buf:
                    buf+=ser.read(1)
                    print buf
                    
                    #ser.write(chr(0x00))
                    
                print " ".join("{:02x}".format(ord(c)) for c in buf)    
                print " "+str(len(cmdpar3))+" bytes sent."
                buf=""
                cmdoutput=""
                #time.sleep(1.00)
                ser.write(chr(0xAA)) #Setbyte command
                ser.write(chr(0xFF)) 
                ser.write(chr(0xF1)) #Address FFF1
                ser.write(chr(0x00)) #Set Bit 0 to deactivate writing
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
        time.sleep(0.01)
    time.sleep(0.10)
    cmddone=False
    return




    


main()

