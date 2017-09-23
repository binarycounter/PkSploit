;Author: BinaryCounter (23-09-17)


    SECTION "Program Start",WRAMX[$D000]
Boot::

.setup


.menu

;Basic Command interface.
;Usage: GB sends $CD, Client responds with command
;Hex commands:
; $AA - Set Byte
; $55 - Run Block Transfer Routine (Read/Write blocks of memory)
; $33 - Jump to Address

ld a, $CD
call serial
cp $AA
jr z, .setbyte
cp $55 
jr z, .transfer
cp $33 
jr z, .jump
jr .menu


.setbyte

;todo

jr .menu

.transfer

;todo

jr .menu


;Command 33, jump to address
;Usage: 	GB sends $A0, Client responds with High byte of address,
;		 	GB sends $B0, Client responds with low byte of address.
;			GB jumps to address, make sure to jump back .setup to return.
.jump

ld a, $A0
call serial
ld h, a
ld a, $B0
call serial
ld l, a
jp [hl]





.serial ;writes value in A to serial and puts response in A


ld [$ff01],a ;Serial Data Register
ld a, $81 ; 
ld [$ff02],a ;Serial Mode
.waitloop1
ld a, [$ff02]
and $80
jr nz, .waitloop1
ld a, [$ff01]
ret