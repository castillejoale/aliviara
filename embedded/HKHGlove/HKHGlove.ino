/*********************************************************************
 Adafruit invests time and resources providing this open source code,
 please support Adafruit and open-source hardware by purchasing
 products from Adafruit!

 MIT license, check LICENSE for more information
 All text above, and the splash screen below must be included in
 any redistribution
*********************************************************************/

#include <Arduino.h>
#include <SPI.h>
#if not defined (_VARIANT_ARDUINO_DUE_X_) && not defined (_VARIANT_ARDUINO_ZERO_)
  #include <SoftwareSerial.h>
#endif

#include "Adafruit_BLE.h"
#include "Adafruit_BluefruitLE_SPI.h"
#include "Adafruit_BluefruitLE_UART.h"

#include "BluefruitConfig.h"

/*=========================================================================
    APPLICATION SETTINGS

    FACTORYRESET_ENABLE       Perform a factory reset when running this sketch
   
                              Enabling this will put your Bluefruit LE module
                              in a 'known good' state and clear any config
                              data set in previous sketches or projects, so
                              running this at least once is a good idea.
   
                              When deploying your project, however, you will
                              want to disable factory reset by setting this
                              value to 0.  If you are making changes to your
                              Bluefruit LE device via AT commands, and those
                              changes aren't persisting across resets, this
                              is the reason why.  Factory reset will erase
                              the non-volatile memory where config data is
                              stored, setting it back to factory default
                              values.
       
                              Some sketches that require you to bond to a
                              central device (HID mouse, keyboard, etc.)
                              won't work at all with this feature enabled
                              since the factory reset will clear all of the
                              bonding data stored on the chip, meaning the
                              central device won't be able to reconnect.
    MINIMUM_FIRMWARE_VERSION  Minimum firmware version to have some new features
    MODE_LED_BEHAVIOUR        LED activity, valid options are
                              "DISABLE" or "MODE" or "BLEUART" or
                              "HWUART"  or "SPI"  or "MANUAL"
    -----------------------------------------------------------------------*/
    #define FACTORYRESET_ENABLE         1
    #define MINIMUM_FIRMWARE_VERSION    "0.6.6"
    #define MODE_LED_BEHAVIOUR          "MODE"
/*=========================================================================*/

// Create the bluefruit object using hardware SPI, using SCK/MOSI/MISO 
// hardware SPI pins and then user selected CS/IRQ/RST
Adafruit_BluefruitLE_SPI ble(BLUEFRUIT_SPI_CS, BLUEFRUIT_SPI_IRQ, BLUEFRUIT_SPI_RST);

// A small helper
void error(const __FlashStringHelper*err) {
  Serial.println(err);
  while (1);
}



/*=========================================================================*/
/*=========================================================================*/
/*=========================================================================*/
/* Objectives:
 *    - Need to handle incoming Digital Vibration messages from APP...single int?
 *    - MUST DESIGN THE DIFFERENT TYPES OF HAPTIC FEEDBACK
 *      -> Store the different vibration modes in a data structure in this
 *         file, so all the APP needs to send is the vibration mode id number
 *      -> digitalWrite() the numbers in the received id index into data structure
 *      
 */
/*=========================================================================*/
/*=========================================================================*/
/*=========================================================================*/


int thumb = A1;
int index = A2;
int middle = A3;
int ring = A4;
int pinky = A5;
int thumbVal;
int indexVal;
int middleVal;
int ringVal;
int pinkyVal;
// int data[6];


void setup(void)
{
  while (!Serial);
  delay(500);

  pinMode(thumb, INPUT);
  pinMode(index, INPUT);
  pinMode(middle, INPUT);
  pinMode(ring, INPUT);
  pinMode(pinky, INPUT);
  pinMode(9, OUTPUT);

  Serial.begin(115200);
  Serial.println(F("------------------------------------------+"));

  /* Initialise the module */
  Serial.print(F("Initialising the Bluefruit LE module: "));

  if ( !ble.begin(VERBOSE_MODE) )
  {
    error(F("Couldn't find Bluefruit, make sure it's in CoMmanD mode & check wiring?"));
  }
  Serial.println( F("OK! |") );
  Serial.println(F("------------------------------------------+"));


  /* 
   *  Disable command echo from Bluefruit
   *  
   ble.echo(false);
   */
   
  Serial.println(F("Program now starting\n"));

  ble.verbose(false);

  /* Wait for connection */
  while (! ble.isConnected()) {
      delay(500);
  }
}

void loop(void)
{
  thumbVal = analogRead(thumb);
  indexVal = analogRead(index);
  middleVal = analogRead(middle);
  ringVal = analogRead(ring);
  pinkyVal = analogRead(pinky);
//  thumb = map(thumbVal, 600, 900, 0, 180);
  /*
  data[0] = thumbVal;
  data[1] = indexVal;
  data[2] = middleVal;
  data[3] = ringVal;
  data[4] = pinkyVal;
  data[5] = 420;
  */
  /*
   * The data is sent in 5 different messages. One message for each finger.
   * The order is as follows:
   *    First message == Thumb Flex
   *    Second message == Index Flex
   *    Third Message == Middle Flex
   *    Fourth Message == Ring Flex
   *    Fifth Message = Pinky Flex
   * Then the next message received will be the next Thumb Flex value.
   
  ble.print("AT+BLEUARTTX=");
  ble.println(thumbVal);
  ble.print("AT+BLEUARTTX=");
  ble.println(indexVal);
  ble.print("AT+BLEUARTTX=");
  ble.println(middleVal);
  ble.print("AT+BLEUARTTX=");
  ble.println(ringVal);
  ble.print("AT+BLEUARTTX=");
  ble.println(pinkyVal);
  */

  // Temporary MESSY VERSION for Bluefruit LE App Display
  ble.print("AT+BLEUARTTX=");
  ble.println(thumbVal);
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(indexVal);
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(middleVal);
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(ringVal);
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(pinkyVal);
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  ble.print("AT+BLEUARTTX=");
  ble.println(" \n");
  delay(500);

  // check response stastus
  if (! ble.waitForOK() ) {
    Serial.println(F("Failed to send?"));
  }
  

  /*
   * Each message they send back to the Microcontroller is followed
   * by an "OK" message with just the 2 chars "OK". This denotes the
   * end of the message here.
  */
  ble.println("AT+BLEUARTRX");
  ble.readline();
  if (strcmp(&ble.buffer[1], "OK") == 0) {
    // no data
    return;
  }
  Serial.println(&ble.buffer[1]);
  
  if (strcmp(&ble.buffer[1], "o") == 0) {
    digitalWrite(9, HIGH);
    delay(1500);
    digitalWrite(9, LOW);
    delay(200);
    digitalWrite(9, HIGH);
    delay(200);
    digitalWrite(9, LOW);
  } else if (strcmp(&ble.buffer[1], "i") == 0) {
    digitalWrite(9, HIGH);
    delay(200);
    digitalWrite(9, LOW);
    delay(200);
    digitalWrite(9, HIGH);
    delay(200);
    digitalWrite(9, LOW);
    delay(200);
    digitalWrite(9, HIGH);
    delay(200);
    digitalWrite(9, LOW);
  }
  
  ble.waitForOK();
}
