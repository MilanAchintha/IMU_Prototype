
#include "imu_data.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

#include "esp_system.h"

// Configuration
#define IMU_SAMPLE_INTERVAL   2
#define IMU_QUEUE_LENGTH      1000
#define IMU_TASK_STACK_SIZE   4096
#define IMU_TASK_PRIORITY    5

// Queue handle
static QueueHandle_t imu_queue = NULL;

// Message ID counter (4 bytes)
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
static void imu_generate_data(IMU_Data_t* data)
{
    // Message ID (full 32-bit range)
    data->message_id = next_message_id;

    next_message_id++;


    // Temperature
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


// FreeRTOS task: generate IMU samples
static void imu_generation_task(void* parameter)
{
    IMU_Data_t imu_data;

    TickType_t last_wake_time = xTaskGetTickCount();

    while (1)
    {
        // Generate new sample
        imu_generate_data(&imu_data);


        // Send sample to queue without waiting
        if (xQueueSend(imu_queue, &imu_data, 0) != pdPASS)
        {
            // Queue is full: sample is dropped
        }


        // Wait for next sampling interval
        vTaskDelayUntil(
            &last_wake_time,
            pdMS_TO_TICKS(IMU_SAMPLE_INTERVAL)
        );
    }
}


// Initialize queue and generation task
bool imu_data_init()
{
    // Create queue
    imu_queue = xQueueCreate(
        IMU_QUEUE_LENGTH,
        sizeof(IMU_Data_t)
    );

    if (imu_queue == NULL)
    {
        return false;
    }


    // Create FreeRTOS task
    BaseType_t result = xTaskCreate(
        imu_generation_task,
        "IMU_Generation",
        IMU_TASK_STACK_SIZE,
        NULL,
        IMU_TASK_PRIORITY,
        NULL
    );


    if (result != pdPASS)
    {
        vQueueDelete(imu_queue);

        imu_queue = NULL;

        return false;
    }

    return true;
}


// Receive one sample from queue
bool imu_data_receive(IMU_Data_t* data)
{
    if (imu_queue == NULL || data == NULL)
    {
        return false;
    }

    return xQueueReceive(
        imu_queue,
        data,
        0
    ) == pdPASS;
}
