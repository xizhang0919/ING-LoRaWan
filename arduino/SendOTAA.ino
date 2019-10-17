#include <TheThingsNetwork.h>
#include "DHT.h"
#include <string.h>
#include <ctype.h>

// Set your AppEUI and AppKey
const char *appEui = "70B3D57ED0023C4B";
const char *appKey = "E91FF06786EBAB84BD9B0845F548198D";

const int inputPin = A0;  // use A0 pin in Uno
const int DHTPIN = A1;

#define loraSerial Serial1
#define debugSerial Serial

#define DHTTYPE DHT22

// Replace REPLACE_ME with TTN_FP_EU868 or TTN_FP_US915
#define freqPlan TTN_FP_EU868

TheThingsNetwork ttn(loraSerial, debugSerial, freqPlan);

DHT dht(DHTPIN, DHTTYPE);

void setup()
{
  loraSerial.begin(57600);
  debugSerial.begin(9600);

  // Wait a maximum of 10s for Serial Monitor
  while (!debugSerial && millis() < 10000)
    ;

  debugSerial.println("-- STATUS");
  ttn.showStatus();

  debugSerial.println("-- JOIN");
  ttn.join(appEui, appKey);

  pinMode(inputPin, INPUT);

  dht.begin();

}

void loop()
{
  debugSerial.println("-- LOOP");

  int moistureValue = analogRead(inputPin);
  
  debugSerial.println(moistureValue);

  char moisture;
  if (moistureValue > 700) {
    moisture = 'L';
  } else if (moistureValue > 400 && moistureValue <=700) {
    moisture = 'M';
  } else if (moistureValue <= 400) {
    moisture = 'H';
  }

  float temperatureValue = dht.readTemperature();;

   char temperature[6];
   sprintf(temperature, "%.2f", temperatureValue);

   char payload[10];
   int ind=0;
   payload[ind++] = moisture;
   payload[ind++] = '#';

   for(int j=0;j<sizeof(temperature);j++) {
      if (isdigit(temperature[j])) {
         int val = temperature[j] - '0';
         char alpha = (char) ('A' + val);
         payload[ind++] = alpha;
      }
      else {
         payload[ind++] = '#';
      }
   }
  payload[ind] = '#';
  ttn.sendBytes(payload, sizeof(payload));
  
  delay(1000);
}

