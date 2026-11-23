#include <Arduino.h>

#include "imu_data.h"
#include "packet.h"
#include "wifi_manager.h"
#include "websocket_client.h"

uint32_t successful_batches = 0;
uint32_t failed_batches = 0;
uint32_t successful_packets = 0;

// Laptop's Wi-Fi IPv4 address
#define SERVER_IP "192.168.43.19"

#define SERVER_PORT 8080

void setup()
{
    Serial.begin(115200);

    delay(1000);

    // 1. Initialize IMU data generation and queue
    if (!imu_data_init())
    {
        Serial.println("IMU initialization failed!");

        while (1)
        {
            delay(1000);
        }
    }

    // 2. Connect ESP32 to Wi-Fi
    wifi_init();

    wifi_print_ip();

    // 3. Initialize WebSocket client
    websocket_init(SERVER_IP, SERVER_PORT);

    Serial.println("System initialized!");
}

// void loop()
// {
//     uint8_t packet[PACKET_SIZE];

//     // 1. Maintain WebSocket connection
//     websocket_loop();

//     // 2. Receive packets only when WebSocket is connected.
//     // This prevents removing packets from the queue
//     // while the network is disconnected.
//     if (websocket_is_connected())
//     {
//         while (packet_receive(packet))
//         {
//             // 3. Send one 24-byte binary packet
//             if (websocket_send_binary(packet, PACKET_SIZE))
//             {
//                 // Library accepted the send operation.
//             }
//             else
//             {
//                 Serial.println("WebSocket send failed!");
//             }
//         }
//     }

//     // 4. Print statistics every 1 second
//     static unsigned long lastPrint = 0;

//     if (millis() - lastPrint >= 1000)
//     {
//         Serial.println("\n--- DATA STATISTICS ---");

//         Serial.printf(
//             "Generated : %lu\n",
//             (unsigned long)generatedCount
//         );

//         Serial.printf(
//             "Queue Sent: %lu\n",
//             (unsigned long)sentCount
//         );

//         Serial.printf(
//             "Received  : %lu\n",
//             (unsigned long)receivedCount
//         );

//         Serial.printf(
//             "Dropped   : %lu\n",
//             (unsigned long)droppedCount
//         );

//         Serial.println("-----------------------");

//         lastPrint = millis();
//     }

//     delay(1);
// }

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
            // // Calculate the position to store this packet
            // uint16_t offset = batch_count * PACKET_SIZE;

            // // Copy 24-byte packet into batch buffer
            // memcpy(
            //     &batch_buffer[offset],
            //     packet,
            //     PACKET_SIZE);

            // // Increase collected packet count
            // batch_count++;

            // // Check whether 100 packets have been collected
            // if (batch_count >= 100)
            // {
            //     // Send all 100 packets together
            //     if (websocket_send_binary(
            //             batch_buffer,
            //             sizeof(batch_buffer)))
            //     {
            //         // Serial.println("100 packets sent!");
            //         successful_batches++;
            //         successful_packets += 100;
            //     }
            //     else
            //     {
            //         // Serial.println("Batch send failed!");
            //         failed_batches++;
            //     }

            //     // Reset batch counter
            //     batch_count = 0;
            // }
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
        // Serial.printf("Successful batches : %lu\n", (unsigned long)successful_batches);
        // Serial.printf("Failed batches     : %lu\n", (unsigned long)failed_batches);
        // Serial.printf("Successful packets : %lu\n", (unsigned long)successful_packets);

        Serial.println("-----------------------");

        lastPrint = millis();
    }

    delay(1);
}
