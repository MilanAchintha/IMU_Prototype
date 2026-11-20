
// #include <Arduino.h>

// #include "wifi_manager.h"
// #include "websocket_client.h"

// const char* SERVER_IP = "192.168.43.19";
// const uint16_t SERVER_PORT = 8080;

// unsigned long last_send_time = 0;

// void setup()
// {
//     Serial.begin(115200);

//     // Connect to Wi-Fi
//     wifi_init();

//     wifi_print_ip();

//     // Initialize WebSocket
//     websocket_init(SERVER_IP, SERVER_PORT);
// }

// void loop()
// {
//     // Keep WebSocket connection alive
//     websocket_loop();

//     // Send message every 2 seconds
//     if (websocket_is_connected())
//     {
//         if (millis() - last_send_time >= 2000)
//         {
//             last_send_time = millis();

//             websocket_send("Hello from ESP32!");

//             Serial.println("Message sent to Python");
//         }
//     }
// }




#include <Arduino.h>

#include "imu_data.h"
#include "packet.h"

void setup()
{
    Serial.begin(115200);

    delay(1000);

    Serial.println();
    Serial.println("==============================");
    Serial.println("    IMU PACKET RECEIVER");
    Serial.println("==============================");

    // Initialize IMU generation task and packet queue
    if (!imu_data_init())
    {
        Serial.println("ERROR: IMU initialization failed!");

        while (1)
        {
            delay(1000);
        }
    }

    Serial.println("Packet queue initialized successfully!");
    Serial.println("Waiting for packets...");
}

void loop()
{
    uint8_t packet[PACKET_SIZE];

    // Receive all available packets from the queue
    while (packet_receive(packet))
    {
        Serial.println();

        Serial.println("----- RECEIVED PACKET -----");

        for (int i = 0; i < PACKET_SIZE; i++)
        {
            Serial.printf("%02X ", packet[i]);
        }

        Serial.println();
        Serial.println("---------------------------");
    }

    delay(1);
}
