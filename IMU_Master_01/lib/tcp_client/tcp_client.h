
#ifndef TCP_CLIENT_H
#define TCP_CLIENT_H

#include <Arduino.h>

bool tcp_client_connect(const char* ip, uint16_t port);

bool tcp_client_is_connected();

bool tcp_client_send(const char* message);

#endif
