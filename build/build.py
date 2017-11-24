#!python2
import os
import sys
import shutil
import ConfigParser


print "PkSploit Build Script - Revision 24-11-17"

if not os.path.exists("config.ini"):
		print "No config.ini file! Rename and edit sample_config.ini in this folder!"
		sys.exit(1)

Config = ConfigParser.ConfigParser()
Config.read("config.ini")

#ConfigParser Helper function from the Python wiki
#https://wiki.python.org/moin/ConfigParserExamples

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1



choice=""
everything=5
if len(sys.argv) > 1:
	if sys.argv[1] == "full":
		choice=everything

odir=ConfigSectionMap("General")["outputdir"]
while choice not in range(1,6):
	print "---------------------------"
	print "What do you want to build?"
	print ""
	print "1. Assemble Gameboy ASM"
	print "2. Assemble Gameboy ASM (Patch Savefile for quick start)"
	print "3. Prepare Arduino Project"
	print "4. Build and Upload Arduino Project"
	print "5. Everything (run \"py build.py full\" to skip this menu in the future)"
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

def assemble():
	print "Assembling Gameboy Code with trade offsets"
	if os.path.exists(odir+"/gb_asm_trade/"):
		shutil.rmtree(odir+"/gb_asm_trade/")
	shutil.copytree("../gb_asm/",odir+"/gb_asm_trade/")
	fa=open(odir+"/gb_asm_trade/main.asm","rb")
	code=fa.read()
	fa.close()
	fa=open(odir+"/gb_asm_trade/main.asm","wb")
	fa.write("rOFFSET EQUS \"$c486\"\n\rrEXTRA EQUS \"\""+code)
	fa.close()
	os.system("rgbasm.exe -o "+odir+"temp.o "+odir+"gb_asm_trade/main.asm")
	os.system("rgblink.exe -o "+odir+"temp.gb "+odir+"temp.o")
	fi = open(odir+"temp.gb","rb")
	gb_rom = fi.read()
	fi.close()
	fo = open(odir+"main.bin", "wb")
	fo.write(gb_rom[0x150:0x214])
	fo.close()
	print "Done Assembling Gameboy Code"
	return

def makesave():
	print "Assembling Gameboy Code with save file offsets"
	if os.path.exists(odir+"/gb_asm_save/"):
		shutil.rmtree(odir+"/gb_asm_save/")
	shutil.copytree("../gb_asm/",odir+"/gb_asm_save/")
	fa=open(odir+"/gb_asm_save/main.asm","rb")
	code=fa.read()
	fa.close()
	fa=open(odir+"/gb_asm_save/main.asm","wb")
	fa.write("rOFFSET EQUS \"$d280\"\n\rrEXTRA EQUS \"jr .turnoff\""+code)
	fa.close()
	os.system("rgbasm.exe -o "+odir+"temp_save.o "+odir+"gb_asm_save/main.asm")
	os.system("rgblink.exe -o "+odir+"temp_save.gb "+odir+"temp_save.o")
	fi = open(odir+"temp_save.gb","rb")
	gb_rom = fi.read()
	fi.close()
	fo = open(odir+"main_save.bin", "wb")
	fo.write(gb_rom[0x150:0x214])
	fo.close()
	print "Done Assembling Gameboy Code"

	fsg=open("../savefile_templates/pokemon_blue_german.sav","rb")
	save=fsg.read()

	

	fsg.close()
	fp = open(odir+"main_save.bin","rb")
	code=fp.read()
	fp.close()

	save=save[:9847]+code+save[10043:]
	
	#generate valid checksum
	checksum=0
	save_data = map(ord, save[9624:13602])
	for num,bb in enumerate(save_data):
		checksum=checksum+bb
	flip=0xFF
	checksum=chr((checksum%256)^flip)

	save=save[:13603]+checksum+save[13604:]

	fsgs = open(odir+"pokemon_blue_german_pksploit.sav", "wb")
	fsgs.write(save)
	fsgs.close()
	return


def prepare():
	print "Preparing Arduino Project"

	if not os.path.exists(odir+"main.bin"):
		print "Gameboy Code not assembled yet, doing that now..."
		assemble()
	if os.path.exists(odir+ConfigSectionMap("Arduino")['projectname']+"/"):
		shutil.rmtree(odir+ConfigSectionMap("Arduino")['projectname']+"/")
	shutil.copytree("../arduino/"+ConfigSectionMap("Arduino")["projectname"]+"/", odir+ConfigSectionMap("Arduino")["projectname"]+"/")

	#Data Preperation Code By
 	#Esteban Fuentealba

	# load program to run
	fp = open(odir+"main.bin","rb")
	program_str = fp.read()
	fp.close()
	program = map(ord, program_str)
	data  = []

	# seed
	data += [182, 147, 113, 81, 51, 23, 228, 205, 184, 165]

	# preamble
	data += [253, 253, 253, 253, 253, 253, 253, 253]

	# party (bootstrap)
	party = [248, 0, 54, 253, 1, 62, 88, 197, 195, 0xd6, 0xc5, 6, 21, 21, 21, 21, 21, 21, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 227, 206, 227, 227, 255, 33, 160, 195, 1, 136, 1, 62, 0, 205, 224, 54, 17, 24, 218, 33, 89, 196, 205, 85, 25, 195, 21, 218, 139, 142, 128, 131, 136, 141, 134, 232, 232, 232, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 64, 0, 0]
	data += party

	# preamble
	data += [253, 253, 253, 253, 253]

	# patchlist (196 bytes total)
	patchlist = [255, 255] + program + ([0] * 200)
	patchlist = patchlist[:196]
	data += patchlist

	party_and_patchlist = ", ".join(map(str, party + [253, 253, 253, 253, 253] + patchlist))
	fileo = open(odir+ConfigSectionMap("Arduino")["projectname"]+"/data.h","wb")
	fileo.write("unsigned const char DATA_BLOCK[] PROGMEM  = {" + party_and_patchlist + "};")
	fileo.close()
	print "Done Preparing Arduino Project"
	return


def buildarduino():
	print "Building and uploading Arduino Project"
	if not os.path.exists(odir+ConfigSectionMap("Arduino")["projectname"]+"/"):
		print "Arduino Project not prepared yet, doing that now..."
		prepare()
	os.system("\""+ConfigSectionMap("Arduino")['path']+"/arduino_debug.exe\" -v --upload "+odir+ConfigSectionMap("Arduino")["projectname"]+"/"+ConfigSectionMap("Arduino")["projectname"]+".ino --board "+ConfigSectionMap("Arduino")["board"]+" --port "+ConfigSectionMap("Arduino")["port"])
	print "Done Building and uploading Arduino Project"
	return

if not os.path.exists(odir):
	os.makedirs(odir)


if choice == 1 or choice == everything:
	assemble()
	
if choice == 2 or choice == everything:
	makesave()

if choice == 3 or choice == everything:
	prepare()
	
if choice == 4 or choice == everything:
	buildarduino()

	
