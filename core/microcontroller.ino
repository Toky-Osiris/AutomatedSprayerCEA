#include <WiFi.h>
#include <ArduinoJson.h>

const char* ssid = "enter ssid";
const char* password = "enter password";
// WiFi credentials

WiFiServer server(1234);

// Pump and solenoid pins

const int pumpPin=23;
const int solenoidPins[]={18,19,21,22,25,26};
const int numSolenoids= sizeof(solenoidPins)/sizeof(solenoidPins[0]);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected.");
  pinMode(pumpPin, OUTPUT);
  digitalWrite(pumpPin, LOW);
  for (int i=0; i<numSolenoids; i++) {
    pinMode(solenoidPins[i], OUTPUT);
    digitalWrite(solenoidPins[i],LOW);
  }

  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
        while (client.connected()) {
      if (client.available()) {
        String jsonString = client.readStringUntil('\n');  // Read until newline
        Serial.println("Signal received : " + jsonString);

        bool ok = processJson(jsonString);
        if (ok) {
          client.print("Now spraying!\n");
        } else {
          client.print("JSON error\n");
        }
      }
    }

    client.stop();
    return;
  }

  Serial.println("Listening...");
  delay(10000);
}

bool processJson(String jsonString ) {
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, jsonString);
  if (error) {
    Serial.print("JSON parse error: ");
    Serial.println(error.c_str());
    return false;
  }
// Get solenoid array and duration
  JsonArray solenoids = doc["solenoids"];
  int duration = doc["duration"] | 18000;  // Default to 18s if missing

  if (solenoids.size() == 0) {
    Serial.println("No solenoid data found!");
    shutdown();
    return false;
  }

  bool anyActive = false;
  for (int i = 0; i < numSolenoids && i < solenoids.size(); i++) {
    if (solenoids[i] == 1) {
      anyActive = true;

      break;
    }
  }

  if (!anyActive) {
    Serial.println("No solenoids requested!");
    shutdown();
    return true;
  }

  // Activate
    digitalWrite(pumpPin, HIGH);
  Serial.println("Turning pump and solenoids ON...");
  for (int i = 0; i < numSolenoids && i < solenoids.size(); i++) {
    digitalWrite(solenoidPins[i], solenoids[i] == 1 ? HIGH : LOW);
  }


  Serial.print("Activation for 18 seconds... \n");

  delay(duration);
  shutdown();
  return true;
}

void shutdown() {
  Serial.println("Shutting  down...");
  digitalWrite(pumpPin, LOW);
  for (int i = 0; i < numSolenoids; i++) {
    digitalWrite(solenoidPins[i], LOW);
  }
  Serial.println("Pumps and solenoids are now OFF...");
  Serial.println("==================================");
}