## [v1.0.0] - 2026-11-20 [Feature/IMU_data_packet_create(fixed_imu)]

### Added

- Confirm No data Loss when generated data put to queue and read that queue

## [v1.0.0] - 2026-11-20 [Feature/IMU_data_packet_create(fixed_imu)]

### Added

- Sucessfuuly done packet creation
- Build and Flash Sucsesfull
- fixed value with check packet creation in main.cpp
- Create seperate module for packet create.

- Decided Change Architecture

- decided to put queue read into the while loop
- when queue check in "if" condition and loop delay(1) is data loss even samplin time and queue read time equal or less than read time to the quesend time
- Read queue 
- Create a Task for generate random imu value and send it to queue
- Created Struct for Data Store
- Make new module for IMU random data generate

## [v1.0.0] - Considerations

### Consider
