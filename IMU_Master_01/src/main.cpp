
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
#include "imu_data.h"

void setup()
{
    Serial.begin(115200);

    delay(1000);

    Serial.println();
    Serial.println("================================");
    Serial.println("     IMU DATA GENERATOR");
    Serial.println("================================");

    // Initialize IMU queue and generation task
    if (!imu_data_init())
    {
        Serial.println("ERROR: IMU initialization failed!");

        while (1)
        {
            delay(1000);
        }
    }

    Serial.println("IMU queue initialized successfully!");
    Serial.println("Waiting for IMU samples...");

    // Temporary packet creation test
    IMU_Data_t test_data = {};

    test_data.message_id = 0x12345678;
    test_data.temperature = 25;

    test_data.accel_x = 1000;
    test_data.accel_y = -1000;
    test_data.accel_z = 2000;

    test_data.gyro_x = 3000;
    test_data.gyro_y = -3000;
    test_data.gyro_z = 4000;

    test_data.mag_x = 5000;
    test_data.mag_y = -5000;
    test_data.mag_z = 6000;

    // Create 24-byte packet
    uint8_t packet[PACKET_SIZE];

    packet_create(&test_data, packet);

    // Print packet bytes
    Serial.println("----- PACKET TEST -----");

    for (int i = 0; i < PACKET_SIZE; i++)
    {
        Serial.printf("%02X ", packet[i]);
    }

    Serial.println();
    Serial.println("-----------------------");
}

void loop()
{
    // IMU_Data_t imu_data;

    // Receive one sample from the queue
    // if (imu_data_receive(&imu_data))
    // {
    //     Serial.println();
    //     Serial.println("---------- IMU DATA ----------");

    //     // Message ID
    //     Serial.print("Message ID: ");
    //     Serial.println(imu_data.message_id);

        // // Temperature
        // Serial.print("Temperature: ");
        // Serial.print(imu_data.temperature);
        // Serial.println(" C");

        // // Accelerometer
        // Serial.println();
        // Serial.println("Accelerometer:");

        // Serial.print("X: ");
        // Serial.println(imu_data.accel_x);

        // Serial.print("Y: ");
        // Serial.println(imu_data.accel_y);

        // Serial.print("Z: ");
        // Serial.println(imu_data.accel_z);

        // // Gyroscope
        // Serial.println();
        // Serial.println("Gyroscope:");

        // Serial.print("X: ");
        // Serial.println(imu_data.gyro_x);

        // Serial.print("Y: ");
        // Serial.println(imu_data.gyro_y);

        // Serial.print("Z: ");
        // Serial.println(imu_data.gyro_z);

        // // Magnetometer
        // Serial.println();
        // Serial.println("Magnetometer:");

        // Serial.print("X: ");
        // Serial.println(imu_data.mag_x);

        // Serial.print("Y: ");
        // Serial.println(imu_data.mag_y);

        // Serial.print("Z: ");
        // Serial.println(imu_data.mag_z);

        // Serial.println("------------------------------");
    // }

    // Small delay to prevent continuous empty queue checking
    // delay(1);
}
