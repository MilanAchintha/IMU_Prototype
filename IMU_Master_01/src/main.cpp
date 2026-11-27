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
    static uint8_t batch_buffer[PACKET_SIZE * BATCH_SIZE];

    // Number of packets collected so far
    static uint16_t batch_count = 0;  // loop never setup

    uint8_t packet[PACKET_SIZE];

    // Maintain WebSocket connection
    websocket_loop();

    if (websocket_is_connected())
    {
        // STEP 1: If 100 packets are already waiting, retry sending them
        // collected 100 packets, but the WebSocket send operation failed..so try again
        if (batch_count >= BATCH_SIZE)
        {
            if (websocket_send_binary(
                    batch_buffer,
                    sizeof(batch_buffer)))
            {
                successful_batches++;
                successful_packets += BATCH_SIZE;

                // Reset only after successful sending
                batch_count = 0;
            }
            else
            {
                failed_batches++;

                // Keep batch_count = 100.
                // Do not collect new packets.
                return;  // next loop() execution starts again from the beginning
            }
        }

        // STEP 2: Collect new packets only when the batch is not full
        while (batch_count < BATCH_SIZE && packet_receive(packet))
        {
            // Calculate the position to store this packet
            uint16_t offset = batch_count * PACKET_SIZE;

            // Copy packet into batch buffer
            memcpy(
                &batch_buffer[offset],
                packet,
                PACKET_SIZE);

            // Increase collected packet count
            batch_count++;
        }

        // STEP 3: If the batch becomes full, try sending it
        if (batch_count >= BATCH_SIZE)
        {
            if (websocket_send_binary(
                    batch_buffer,
                    sizeof(batch_buffer)))
            {
                successful_batches++;
                successful_packets += BATCH_SIZE;

                batch_count = 0;
            }
            else
            {
                failed_batches++;

                // Keep all 100 packets for the next retry
            }
        }
    }
    else
    {
        Serial.println("WebSocket not connected.");
    }

    // Print statistics every 1 second
    static unsigned long lastPrint = 0;

    if (millis() - lastPrint >= 5000)
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