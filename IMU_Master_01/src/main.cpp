
#include <Arduino.h>

#include "wifi_manager.h"
#include "websocket_client.h"

const char* SERVER_IP = "192.168.43.19";
const uint16_t SERVER_PORT = 8080;

unsigned long last_send_time = 0;

void setup()
{
    Serial.begin(115200);

    // Connect to Wi-Fi
    wifi_init();

    wifi_print_ip();

    // Initialize WebSocket
    websocket_init(SERVER_IP, SERVER_PORT);
}

void loop()
{
    // Keep WebSocket connection alive
    websocket_loop();

    // Send message every 2 seconds
    if (websocket_is_connected())
    {
        if (millis() - last_send_time >= 2000)
        {
            last_send_time = millis();

            websocket_send("Hello from ESP32!");

            Serial.println("Message sent to Python");
        }
    }
}
