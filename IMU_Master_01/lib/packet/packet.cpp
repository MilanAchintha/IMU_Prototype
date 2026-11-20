#include "packet.h"

void packet_create(const IMU_Data_t *imu_data, uint8_t *packet)
{
    uint8_t index = 0;

    // Device ID (1 byte)
    packet[index++] = DEVICE_ID;

    // Message ID (4 bytes)
    packet[index++] = (uint8_t)(imu_data->message_id);
    packet[index++] = (uint8_t)(imu_data->message_id >> 8);
    packet[index++] = (uint8_t)(imu_data->message_id >> 16);
    packet[index++] = (uint8_t)(imu_data->message_id >> 24);

    // Temperature (1 byte)
    packet[index++] = (uint8_t)imu_data->temperature;

    // Accelerometer (6 bytes)
    packet[index++] = (uint8_t)(imu_data->accel_x);
    packet[index++] = (uint8_t)(imu_data->accel_x >> 8);

    packet[index++] = (uint8_t)(imu_data->accel_y);
    packet[index++] = (uint8_t)(imu_data->accel_y >> 8);

    packet[index++] = (uint8_t)(imu_data->accel_z);
    packet[index++] = (uint8_t)(imu_data->accel_z >> 8);

    // Gyroscope (6 bytes)
    packet[index++] = (uint8_t)(imu_data->gyro_x);
    packet[index++] = (uint8_t)(imu_data->gyro_x >> 8);

    packet[index++] = (uint8_t)(imu_data->gyro_y);
    packet[index++] = (uint8_t)(imu_data->gyro_y >> 8);

    packet[index++] = (uint8_t)(imu_data->gyro_z);
    packet[index++] = (uint8_t)(imu_data->gyro_z >> 8);

    // Magnetometer (6 bytes)
    packet[index++] = (uint8_t)(imu_data->mag_x);
    packet[index++] = (uint8_t)(imu_data->mag_x >> 8);

    packet[index++] = (uint8_t)(imu_data->mag_y);
    packet[index++] = (uint8_t)(imu_data->mag_y >> 8);

    packet[index++] = (uint8_t)(imu_data->mag_z);
    packet[index++] = (uint8_t)(imu_data->mag_z >> 8);
}