
#ifndef IMU_DATA_H
#define IMU_DATA_H

#include <Arduino.h>

typedef struct
{
    // Message ID (4 bytes)
    uint32_t message_id;

    // Temperature (1 byte)
    int8_t temperature;

    // Accelerometer (X, Y, Z)
    int16_t accel_x;
    int16_t accel_y;
    int16_t accel_z;

    // Gyroscope (X, Y, Z)
    int16_t gyro_x;
    int16_t gyro_y;
    int16_t gyro_z;

    // Magnetometer (X, Y, Z)
    int16_t mag_x;
    int16_t mag_y;
    int16_t mag_z;

} IMU_Data_t;


// Initialize queue and generation task
bool imu_data_init();

// Receive one sample from queue
bool packet_receive(uint8_t* packet);

#endif
