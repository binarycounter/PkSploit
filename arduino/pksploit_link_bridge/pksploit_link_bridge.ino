// Original file by
// Esteban Fuentealba
// 2014/05/12

//Heavily modified by BinaryCounter 
//to support the PkSploit Interface

//Hope this satisfies the Apache License :/


// Link Cable     Arduino      Desc
// 6              GND          GND
// 5              2            SC
// 2              3            SI
// 3              6            SO
#include <avr/pgmspace.h>

#include "pokemon.h"
#include "data.h"

//Faster digital read write code from
//http://masteringarduino.blogspot.de/2013/10/fastest-and-smallest-digitalread-and.html
#define portOfPin(P)\
  (((P)>=0&&(P)<8)?&PORTD:(((P)>7&&(P)<14)?&PORTB:&PORTC))
#define ddrOfPin(P)\
  (((P)>=0&&(P)<8)?&DDRD:(((P)>7&&(P)<14)?&DDRB:&DDRC))
#define pinOfPin(P)\
  (((P)>=0&&(P)<8)?&PIND:(((P)>7&&(P)<14)?&PINB:&PINC))
#define pinIndex(P)((uint8_t)(P>13?P-14:P&7))
#define pinMask(P)((uint8_t)(1<<pinIndex(P)))

#define pinAsInput(P) *(ddrOfPin(P))&=~pinMask(P)
#define pinAsInputPullUp(P) *(ddrOfPin(P))&=~pinMask(P);digitalHigh(P)
#define pinAsOutput(P) *(ddrOfPin(P))|=pinMask(P)
#define digitalLow(P) *(portOfPin(P))&=~pinMask(P)
#define digitalHigh(P) *(portOfPin(P))|=pinMask(P)
#define isHigh(P)((*(pinOfPin(P))& pinMask(P))>0)
#define isLow(P)((*(pinOfPin(P))& pinMask(P))==0)
#define digitalState(P)((uint8_t)isHigh(P))

int volatile CLOCK_PIN = 2;
int volatile SO_PIN = 6;
int volatile SI_PIN = 3;
int volatile data = 0;
int volatile val = 0;
byte volatile lsend = 0x00;
int ledStatus = 13;

unsigned volatile long lastReceive = 0;
volatile byte outputBuffer = 0x00;
volatile int counterRead = 0;
volatile boolean sending = false;
volatile trade_centre_state_t nextstate = PKSPLOIT_MENU;
volatile int counter = 0;
volatile byte command = 0x00;
volatile int counter2 = 00;
volatile connection_state_t connection_state = NOT_CONNECTED;
volatile trade_centre_state_t trade_centre_state = INIT;



void setup() {
  pinMode(SI_PIN, INPUT);
  digitalWrite( SI_PIN, HIGH);  
  pinMode(SO_PIN, OUTPUT);
  pinMode(ledStatus, OUTPUT);
  digitalWrite(ledStatus, LOW);
  digitalWrite(SO_PIN, LOW);
  pinMode(CLOCK_PIN, INPUT);
  digitalWrite(CLOCK_PIN, HIGH);
  attachInterrupt( 0, clockInterrupt, RISING );
  Serial.begin(28800);
 Serial.println("Boot complete");
}


void clockInterrupt(void) {
 //timer=millis();
  byte in;
  unsigned long t = 0;
  if(lastReceive > 0) {
    if( micros() - lastReceive > 120 ) {
      counterRead = 0;
      val = 0;
      in = 0x00;
    }
  }
  
  if(digitalState(SI_PIN) == HIGH){
    val |= ( 1 << (7-counterRead) );
    in |= ( 1 << (7-counterRead) );
  }
  if(counterRead == 7) {
    //Serial.write((byte)val);
    outputBuffer = handleIncomingByte((byte)val);
    
    
    val = 0;
    in = 0x00;
    counterRead = -1;
  }
  
  counterRead++;
  lastReceive = micros();
  while( ((digitalState(CLOCK_PIN) | CLOCK_PIN) & CLOCK_PIN)  == 0);
  if(outputBuffer & 0x80 ? SO_PIN : 0!=0)
  {
  digitalHigh(SO_PIN);
  }else{digitalLow(SO_PIN);}

  outputBuffer = outputBuffer << 1;
  
}
byte handleIncomingByte(byte in) {
   
  byte send = 0x00;
  
  switch(connection_state) {
  case NOT_CONNECTED:
    if (in==0xCD)
    {connection_state = TRADE_CENTRE;
    trade_centre_state = PKSPLOIT_MENU;
    Serial.print("StatusMQ");}
    if(in == PKMN_MASTER)
      send = PKMN_SLAVE;
    else if(in == PKMN_BLANK)
      send = PKMN_BLANK;
    else if(in == PKMN_CONNECTED) {
      send = PKMN_CONNECTED;
      connection_state = CONNECTED;
      Serial.print("StatusConnected");   
    }
    break;

  case CONNECTED:
    if(in == PKMN_CONNECTED)
      send = PKMN_CONNECTED;
    else if(in == PKMN_TRADE_CENTRE){
      connection_state = TRADE_CENTRE;
      Serial.print("StatusTradeCenter");}
    else if(in == PKMN_COLOSSEUM)
      connection_state = COLOSSEUM;
    else if(in == PKMN_BREAK_LINK || in == PKMN_MASTER) {
      connection_state = NOT_CONNECTED;
      send = PKMN_BREAK_LINK;
      Serial.print("StatusDisconnected");
                        
    } else {
      send = in;
    }
    break;

  case TRADE_CENTRE:
    if(trade_centre_state == INIT && in == 0x00) {
      if(counter++ == 5) {
        trade_centre_state = READY_TO_GO;
      Serial.print("StatusSending");
      }
      send = in;
    } else if(trade_centre_state == READY_TO_GO && (in & 0xF0) == 0xF0) {
      trade_centre_state = SEEN_FIRST_WAIT;
      send = in;
    } else if(trade_centre_state == SEEN_FIRST_WAIT && (in & 0xF0) != 0xF0) {
      send = in;
      counter = 0;
      trade_centre_state = SENDING_RANDOM_DATA;
    } else if(trade_centre_state == SENDING_RANDOM_DATA && (in & 0xF0) == 0xF0) {
      if(counter++ == 5) {
        trade_centre_state = WAITING_TO_SEND_DATA;
      }
      send = in;
    } else if(trade_centre_state == WAITING_TO_SEND_DATA && (in & 0xF0) != 0xF0) {
      counter = 0;
      send = DATA_BLOCK[counter++];
      trade_centre_state = SENDING_DATA;
    } else if(trade_centre_state == SENDING_DATA) {
      send = DATA_BLOCK[counter++];
      if(counter == 619) {
        trade_centre_state = PKSPLOIT_MENU;
        Serial.print("StatusMenu");
      }
    }
     else if(trade_centre_state == PKSPLOIT_MENU) {
       
      if(Serial.available()<3 && !sending){trade_centre_state=nextstate;return send;}
      
      send=Serial.read();
      if(sending==false){ //Not already sending, must be first byte (aka command)
      switch (send)
      {
        case 34: //Internal CMD 0x22, set nextstate to PKSPLOIT_DUMP_BLOCK
          nextstate=PKSPLOIT_DUMP_BLOCK;
          send=00;
          break;
        case 68: //Internal CMD 0x44, set nextstate to PKSPLOIT_SEND_BLOCK
          nextstate=PKSPLOIT_SEND_BLOCK;
          send=00;
          break;
        case 17: //Internal CMD 0x11
          counter2=Serial.read()*256+Serial.read();
          send=00;
          break;
      }
      
      sending=true;}
      
      if(!Serial.available()){sending=false;}
      
     }
    else if(trade_centre_state == PKSPLOIT_DUMP_BLOCK) {
      Serial.write(in);
      
      if(counter2==0)
      {
        trade_centre_state = PKSPLOIT_MENU;
        nextstate = PKSPLOIT_MENU;
        Serial.print("StatusMenu");
      }
      counter2--;
      


    } else {
      send = in;
    }
    break;

  case COLOSSEUM:
    send = in;
    break;

  default:
    send = in;
    break;
  }
  return send;
}

void loop() { 

}
