#include <Arduino.h>

#include "imu_data.h"
#include "packet.h"
#include "wifi_manager.h"
#include "websocket_client.h"

uint32_t successful_batches = 0;
uint32_t failed_batches = 0;
uint32_t successful_packets = 0;

// Laptop's Wi-Fi IPv4 address
#define SERVER_IP "192.168.1.4"

#define SERVER_PORT 8080

void setup()
{
    Serial.begin(115200);

    delay(1000);

    wifi_init();
    wifi_print_ip();

    websocket_init(SERVER_IP, SERVER_PORT);

    imu_data_init();
}

void loop()
{
    // Store 100 packets in one batch
    static uint8_t batch_buffer[PACKET_SIZE * 100]; // static uint8_t batch_buffer[2400];

    // Number of packets collected so far
    static uint16_t batch_count = 0;

    uint8_t packet[PACKET_SIZE];

    // Maintain WebSocket connection
    websocket_loop();

    if (websocket_is_connected())
    {
        // Receive packets from FreeRTOS queue
        while (packet_receive(packet))
        {
            // Calculate the position to store this packet
            uint16_t offset = batch_count * PACKET_SIZE;

            // Copy 24-byte packet into batch buffer
            memcpy(
                &batch_buffer[offset],
                packet,
                PACKET_SIZE);

            // Increase collected packet count
            batch_count++;

            // Check whether 100 packets have been collected
            if (batch_count >= 100)
            {
                // Send all 100 packets together
                if (websocket_send_binary(
                        batch_buffer,
                        sizeof(batch_buffer)))
                {
                    // Serial.println("100 packets sent!");
                    successful_batches++;
                    successful_packets += 100;
                }
                else
                {
                    // Serial.println("Batch send failed!");
                    failed_batches++;
                }

                // Reset batch counter
                batch_count = 0;
            }
        }
    }

    // Print statistics every 1 second
    static unsigned long lastPrint = 0;

    if (millis() - lastPrint >= 1000)
    {
        Serial.println("\n--- DATA STATISTICS ---");

        Serial.printf("Generated : %lu\n", (unsigned long)generatedCount);
        Serial.printf("Queue Sent: %lu\n", (unsigned long)sentCount);
        Serial.printf("Received  : %lu\n", (unsigned long)receivedCount);
        Serial.printf("Dropped   : %lu\n", (unsigned long)droppedCount);
        Serial.printf("Successful batches : %lu\n", (unsigned long)successful_batches);
        Serial.printf("Failed batches     : %lu\n", (unsigned long)failed_batches);
        Serial.printf("Successful packets : %lu\n", (unsigned long)successful_packets);

        Serial.println("-----------------------");

        lastPrint = millis();
    }

    delay(1);
}


// #include <WiFi.h>
// #include <WebSocketsClient.h>

// const char* ssid = "MAB";
// const char* password = "1234567890";

// const char* serverIP = "192.168.43.19";
// const uint16_t serverPort = 8080;

// WebSocketsClient webSocket;

// void webSocketEvent(
//     WStype_t type,
//     uint8_t* payload,
//     size_t length
// ) {
//     switch (type) {

//         case WStype_CONNECTED:
//             Serial.println("WebSocket Connected!");

//             webSocket.sendTXT("Hello from ESP32!");
//             break;

//         case WStype_DISCONNECTED:
//             Serial.println("WebSocket Disconnected!");
//             break;

//         case WStype_TEXT:
//             Serial.print("Python says: ");
//             Serial.write(payload, length);
//             Serial.println();
//             break;

//         default:
//             break;
//     }
// }

// void setup() {

//     Serial.begin(115200);

//     WiFi.begin(ssid, password);

//     Serial.print("Connecting to WiFi");

//     while (WiFi.status() != WL_CONNECTED) {
//         delay(500);
//         Serial.print(".");
//     }

//     Serial.println("\nWiFi Connected!");
//     Serial.println(WiFi.localIP());

//     webSocket.begin(
//         serverIP,
//         serverPort,
//         "/"
//     );

//     webSocket.onEvent(webSocketEvent);

//     webSocket.setReconnectInterval(3000);
// }

// void loop() {
//     webSocket.loop();
// }


// #include <WiFi.h>

// const char* ssid = "SLT-Fiber-2.4G_2880";
// const char* password = "coin6657";

// const char* serverIP = "192.168.1.4";
// const uint16_t serverPort = 8080;

// WiFiClient client;

// void setup()
// {
//     Serial.begin(115200);

//     WiFi.begin(ssid, password);

//     while (WiFi.status() != WL_CONNECTED)
//     {
//         delay(500);
//         Serial.println("Connecting to WiFi...");
//     }

//     Serial.println("WiFi Connected!");

//     Serial.print("ESP32 IP: ");
//     Serial.println(WiFi.localIP());

//     Serial.println("Connecting to TCP server...");

//     if (client.connect(serverIP, serverPort))
//     {
//         Serial.println("TCP Connected!");

//         client.println("Hello from ESP32!");

//         delay(1000);

//         client.stop();
//     }
//     else
//     {
//         Serial.println("TCP Connection Failed!");
//     }
// }

// void loop()
// {
// }
