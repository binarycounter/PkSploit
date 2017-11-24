;Author: BinaryCounter (23-09-17)



;Uncomment one of the following 2 lines when not assembling using the buildscript. 
;rOFFSET EQUS "$c486" ;OFFSET for Trade
;rOFFSET EQUS "$d280" ;OFFSET for SaveFile

;When manually assembling for SaveFile uncomment one of these linse too, to turnoff LCD (to prevent burn-in of pokemon center still frame)
;rEXTRA EQUS ".turnoff" ;Extra for Save
;rEXTRA EQUS "" ;Extra for trade

valAA EQUS "$AA"
val55 EQUS "$55"

    SECTION "Program Start",ROM0[$150]
Boot::

.setup
ld a, [$ffff] ;Disable those pesky serial interrupts, ugh.
and $f7
ld [$ffff], a

;set default vars

ld a, $00
ld [$FFF1], a

;Maybe draw something to the screen here?
;After that, disable interrupts so we have full control


di


.premenu

ld a, $FF
ld [$FFF0], a

.menu

;Basic Command interface.
;Usage: GB sends $CD, Client responds with command
;Hex commands:
; $AA - Set Byte
; $55 - Run Block Transfer Routine (Read/Write blocks of memory)
; $33 - Jump to Address
 
ld a, $CD
call serial + rOFFSET
cp $AA
jr z, .setbyte
cp $55 
jr z, .transfer
cp $33 
jr z, .jump
cp $66 
jr z, .turnoff
jr .menu

;Command 66, jump to address
;Usage: 	GB waits for Vblank and turns off LCD.
.turnoff: 
ld a, [$FF40] 
bit 7, a
jr z, .premenu ;Return right away if screen already off
ld      a,[$FF44]         ; Loop until in first part of vblank
cp      145
jr      nz,.turnoff
ld hl, $FF40
res     7,[hl]
jr .premenu

;Command 33, jump to address
;Usage: 	GB sends $10, Client responds with High byte of address,
;		 	GB sends $20, Client responds with low byte of address.
;			GB jumps to address, return to menu with a ret instruction

.jump
call getaddress + rOFFSET
call callwrapper + rOFFSET
jr .premenu



;Command AA, set byte
;Usage: 	GB sends $10, Client responds with High byte of address,
;		 	GB sends $20, Client responds with low byte of address.
;			GB sends $30, Client responds with byte to be written, 
;			command writes byte and returns to menu
.setbyte
call getaddress + rOFFSET
ld a, $30
call serial + rOFFSET
ld [hl], a
jr .menu


;Command 55, Block transfer
;Usage: 	GB sends $10, Client responds with High byte of byte count,
;		 	GB sends $20, Client responds with low byte of byte count.
;			GB sends $10, Client responds with High byte of start address,
;		 	GB sends $20, Client responds with low byte of start address.
;			Command performs block transfer, returns to menu

.transfer
ld a, [$FFF1] 
ld d, a        ; load command Settings (See set byte for options)
call getaddress + rOFFSET
ld b, h
ld c, l
call getaddress + rOFFSET

.loop1
    ld a, [hl] 
	call serial + rOFFSET
	bit 0, d ;Is write bit set?
 	jr z, .skipwrite
	 bit 1, d ;Bootleg write set?
	jr z, .skipbootleg
	call bootlegwrite + rOFFSET
.skipbootleg
 	ld [hl], a	
.skipwrite
	inc hl
	;------
	dec bc
	ld  a, b
	or  c
	jr  nz, .loop1
;loopend	


jr .premenu

bootlegwrite:

ld e, a
ld a, [$FFF2]
ld [$2100], a
call delay + rOFFSET
ld a, valAA
ld [$0AAA], a
nop
ld a, val55
ld [$0555], a
nop
ld a, $A0
ld [$0AAA], a
nop
ld a,e
ld [hl], a
; .waitforwrite
; ld a, [hl]
; cp b
; jr nz, .waitforwrite
call delay + rOFFSET
ret



;General-Purpose functions

getaddress: ;	GB sends $10, Client responds with High byte of address,
;		 		GB sends $20, Client responds with low byte of address. 
;				destroys a, returns address in hl
ld a, $10
call serial + rOFFSET
ld h, a
ld a, $20
call serial + rOFFSET
ld l, a
ret

serial: ;writes value in A to serial and puts response in A


ld [$ff01],a ;Serial Data Register
ld a, $81 ; 
ld [$ff02],a ;Serial Mode
.waitloop1
ld a, [$ff02]
and $80
jr nz, .waitloop1 ;Waits for data
call delay + rOFFSET
ld a, [$ff01]
ret

callwrapper:
jp hl

delay: ;delays by value in FFF0
ld a, [$FFF0]
jr z, .skipdelay
.wastetime
	dec a
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
	nop
jr nz, .wastetime
.skipdelay
ret
;loopend	
