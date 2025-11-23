#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoWebsockets.h>
#include <ArduinoJson.h>

using namespace websockets;

WebsocketsClient client;

const char* WIFI_SSID = "Prevish";
const char* WIFI_PASSWORD = "Vialatina@43";

const char* SERVER_URL = "ws://localhost:5000";  
String cameraId = "";

void onMessageCallback(WebsocketsMessage message) {
  String payload = message.data();

  // Try parse JSON
  StaticJsonDocument<256> doc;
  DeserializationError err = deserializeJson(doc, payload);

  if (err) {
    Serial.print("Received non-JSON message: ");
    Serial.println(payload);
    return;
  }

  const char* type = doc["type"];

  if (strcmp(type, "registered") == 0) {
    cameraId = doc["Id"].as<String>();
    Serial.print("[");
    Serial.print(cameraId);
    Serial.println("]: Server confirmed registration.");
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println("Camera: STARTED");

  // Connect to WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");

  // Connect to WebSocket
  client.onMessage(onMessageCallback);

  Serial.println("Connecting to WebSocket...");
  if (client.connect(SERVER_URL)) {
    Serial.println("Connected!");

    // Send registration JSON
    StaticJsonDocument<128> doc;
    doc["type"] = "register";
    doc["deviceType"] = "camera";

    String jsonString;
    serializeJson(doc, jsonString);

    client.send(jsonString);
    Serial.println("Sent registration request to server...");
  } else {
    Serial.println("WebSocket Connection Failed!");
  }
}

void loop() {
  client.poll();   // Required for receiving messages
}