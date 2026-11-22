#ifndef WEBSOCKET_CLIENT_H
#define WEBSOCKET_CLIENT_H

#include <Arduino.h>

void websocket_init(const char* server_ip, uint16_t server_port);

void websocket_loop();

bool websocket_is_connected();

void websocket_send(const char* message);

// Send binary data
void websocket_send_binary(uint8_t* data, size_t length);

#endif