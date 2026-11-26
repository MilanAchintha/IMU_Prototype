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

#define BATCH_SIZE 100

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
    static uint8_t batch_buffer[PACKET_SIZE * BATCH_SIZE]; // static uint8_t batch_buffer[2400];

    // Number of packets collected so far
    static uint16_t batch_count = 0;

    uint8_t packet[PACKET_SIZE];

    // Maintain WebSocket connection
    websocket_loop();

    if (websocket_is_connected())
    {
        // Receive packets from FreeRTOS queue
/*Try to get one packet from the queue.
If a packet is available, execute the loop.
If the queue is empty, stop the loop.*/
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
            if (batch_count >= BATCH_SIZE)
            {
                // Send all 100 packets together
                if (websocket_send_binary( // While this sending while condition is not executed..the data is collected to queue
                        batch_buffer,
                        sizeof(batch_buffer)))
                {
                    // Serial.println("100 packets sent!");
                    successful_batches++;
                    successful_packets += BATCH_SIZE;
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
