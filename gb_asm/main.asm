;Author: BinaryCounter (23-09-17)


    SECTION "Program Start",HOME[$150]
Boot::

.setup
ld a, [$ffff] ;Disable those pesky serial interrupts, ugh.
and $f7
ld [$ffff], a

;Maybe draw something to the screen here?
;After that, disable interrupts so we have full control

di
.menu

;Basic Command interface.
;Usage: GB sends $CD, Client responds with command
;Hex commands:
; $AA - Set Byte
; $55 - Run Block Transfer Routine (Read/Write blocks of memory)
; $33 - Jump to Address

ld a, $CD
call serial + $c486 
cp $AA
jr z, .setbyte
cp $55 
jr z, .transfer
cp $33 
jr z, .jump
jr .menu

;Command 33, jump to address
;Usage: 	GB sends $10, Client responds with High byte of address,
;		 	GB sends $20, Client responds with low byte of address.
;			GB jumps to address, make sure to jump back .setup to return.
.jump
call getaddress + $c486 
jp [hl]


;Command AA, set byte
;Usage: 	GB sends $10, Client responds with High byte of address,
;		 	GB sends $20, Client responds with low byte of address.
;			GB sends $30, Client responds with byte to be written, 
;			command writes byte and returns to menu
.setbyte
call getaddress + $c486 
ld a, $30
call serial + $c486 
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
call getaddress + $c486 
ld b, h
ld c, l
call getaddress + $c486 

.loop1
    ld a, [hl] 
	call serial + $c486 
	bit 0, d ;Is write bit set?
	jr z, .skipwrite
	ld [hl], a
.skipwrite
	inc hl
	;------
	dec bc
	ld  a, b
	or  c
	jr  nz, .loop1
;loopend	


jr .menu





;General-Purpose functions

getaddress: ;	GB sends $10, Client responds with High byte of address,
;		 		GB sends $20, Client responds with low byte of address. 
;				destroys a, returns address in hl
ld a, $10
call serial + $c486 
ld h, a
ld a, $20
call serial + $c486 
ld l, a
ret

serial: ;writes value in A to serial and puts response in A


ld [$ff01],a ;Serial Data Register
ld a, $81 ; 
ld [$ff02],a ;Serial Mode
.waitloop1
ld a, [$ff02]
and $80
call delay + $c486 
jr nz, .waitloop1 ;Waits for data
ld a, [$ff01]
ret

delay: ;delays by value in FFF0
ld a, [$FFF0]
.wastetime
	dec a
	nop
	nop
	nop
	nop
	nop
jr nz, .wastetime
ret
;loopend	
