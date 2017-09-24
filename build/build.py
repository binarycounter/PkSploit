import os
import sys
print "PkSploit Build Script - Revision 24-09-17"

choice=""
everything=4;
dir="dist/";
while choice not in range(1,5):
	print "---------------------------"
	print "What do you want to build?"
	print ""
	print "1. Assemble Gameboy ASM"
	print "2. Prepare Arduino Project"
	print "3. Build exe (py2exe)"
	print "4. Everything"
	print ""
	try:
		choice = int(raw_input('--> '))
	except:
		print "Invalid Number"
		choice = 0;


if not os.path.exists(dir):
    os.makedirs(dir)
	
if choice == 1 or choice == everything:
	print "Assembling Gameboy Code"
	
	os.system("rgbasm.exe -o "+dir+"main.o ../gb_asm/main.asm")
	os.system("rgblink.exe -o "+dir+"main.gb "+dir+"main.o")
	