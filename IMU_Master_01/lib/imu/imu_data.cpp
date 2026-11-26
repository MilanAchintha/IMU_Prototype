
#include "imu_data.h"
#include "packet.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

#include "esp_system.h"

// Configuration
#define IMU_SAMPLE_INTERVAL 2
#define IMU_QUEUE_LENGTH 3000
#define IMU_TASK_STACK_SIZE 4096
#define IMU_TASK_PRIORITY 5

volatile uint32_t generatedCount = 0;
volatile uint32_t sentCount = 0;
volatile uint32_t receivedCount = 0;
volatile uint32_t droppedCount = 0;

// Queue handle
static QueueHandle_t packet_queue = NULL;

// Message ID counter
static uint32_t next_message_id = 0;

// Generate random signed 16-bit sensor value
static int16_t random_sensor_value()
{
    int32_t value = esp_random() % 20001;

    value -= 10000;

    return (int16_t)value;
}

// Generate random temperature from 20 to 35 degrees Celsius
static int8_t random_temperature()
{
    return (int8_t)(20 + (esp_random() % 16));
}

// Generate one complete IMU sample
static void imu_generate_data(IMU_Data_t *data)
{
    data->message_id = next_message_id;
    next_message_id++;

    data->temperature = random_temperature();

    // Accelerometer
    data->accel_x = random_sensor_value();
    data->accel_y = random_sensor_value();
    data->accel_z = random_sensor_value();

    // Gyroscope
    data->gyro_x = random_sensor_value();
    data->gyro_y = random_sensor_value();
    data->gyro_z = random_sensor_value();

    // Magnetometer
    data->mag_x = random_sensor_value();
    data->mag_y = random_sensor_value();
    data->mag_z = random_sensor_value();
}

// FreeRTOS task: generate and queue IMU packets
static void imu_generation_task(void *parameter)
{
    IMU_Data_t imu_data;
    uint8_t packet[PACKET_SIZE];

    TickType_t last_wake_time = xTaskGetTickCount();

    while (1)
    {
        // Generate IMU data
        imu_generate_data(&imu_data);
        generatedCount++;

        // Convert IMU data into a 24-byte packet
        packet_create(&imu_data, packet);

        // Send packet to queue without waiting
        if (xQueueSend(packet_queue, packet, 0) == pdPASS)
        {
            sentCount++;
        }
        else
        {
            droppedCount++;
        }
        // Wait for next sampling interval
        vTaskDelayUntil(
            &last_wake_time,
            pdMS_TO_TICKS(IMU_SAMPLE_INTERVAL));
    }
}

// Initialize packet queue and generation task
bool imu_data_init()
{
    // Create queue: each item is PACKET_SIZE bytes
    packet_queue = xQueueCreate(
        IMU_QUEUE_LENGTH,
        PACKET_SIZE);

    // Create FreeRTOS task on Core 1
    BaseType_t result = xTaskCreatePinnedToCore(
        imu_generation_task, // Task function
        "IMU_Generation",    // Task name
        IMU_TASK_STACK_SIZE, // Stack size
        NULL,                // Parameters
        IMU_TASK_PRIORITY,   // Priority
        NULL,                // Task handle
        1                    // Core 1
    );

    return true;
}

bool packet_receive(uint8_t *packet)
{
    if (xQueueReceive(packet_queue, packet, 0) == pdPASS)
    {
        receivedCount++;
        return true;
    }

    return false;
}
