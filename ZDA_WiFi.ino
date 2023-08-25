#include <ESP8266WiFi.h>

const char *ssid = "ZDA WiFi";
const char *password = "12345678";

void setup() {
  WiFi.softAP(ssid,password);
}

void loop() {
  // put your main code here, to run repeatedly:
}
