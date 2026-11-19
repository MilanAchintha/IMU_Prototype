
#include "tcp_client.h"
#include <WiFi.h>

static WiFiClient client;

bool tcp_client_connect(const char* ip, uint16_t port)
{
    client.stop();

    Serial.println("Connecting to TCP Server...");

    if (client.connect(ip, port))
    {
        Serial.println("TCP Server Connected!");
        return true;
    }

    Serial.println("TCP Connection Failed!");
    return false;
}

bool tcp_client_is_connected()
{
    return client.connected();
}

bool tcp_client_send(const char* message)
{
    if (!client.connected())
    {
        return false;
    }

    return client.println(message) > 0;
}
