#include <Arduino.h>

#include "imu_data.h"
#include "packet.h"

void setup()
{
    Serial.begin(115200);

    delay(1000);

    if (!imu_data_init())
    {
        while (1)
        {
            delay(1000);
        }
    }
}

void loop()
{
    uint8_t packet[PACKET_SIZE];

    // Keep receiving packets from the queue
    while (packet_receive(packet))
    {
        // Packet received successfully.
        // Do not print every packet during this test.
    }
    // Print statistics every 1 second
    static unsigned long lastPrint = 0;

    if (millis() - lastPrint >= 1000)
    {

        Serial.println("\n--- DATA STATISTICS ---");

        Serial.printf("Generated : %lu\n", (unsigned long)generatedCount);
        Serial.printf("Sent      : %lu\n", (unsigned long)sentCount);
        Serial.printf("Received  : %lu\n", (unsigned long)receivedCount);
        Serial.printf("Dropped   : %lu\n", (unsigned long)droppedCount);

        Serial.println("-----------------------");

        lastPrint = millis();
    }

    vTaskDelay(10 / portTICK_PERIOD_MS);
}
