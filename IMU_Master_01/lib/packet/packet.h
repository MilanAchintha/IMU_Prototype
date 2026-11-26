#ifndef PACKET_H
#define PACKET_H

#include <Arduino.h>
#include "imu_data.h"

#define DEVICE_ID 2
#define PACKET_SIZE 24

void packet_create(const IMU_Data_t* imu_data, uint8_t* packet);

#endif