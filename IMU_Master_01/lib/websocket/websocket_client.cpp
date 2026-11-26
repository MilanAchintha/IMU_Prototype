
#include "websocket_client.h"
#include <WiFi.h>
#include <WebSocketsClient.h>

static WebSocketsClient ws;

static void websocket_event(
    WStype_t type,
    uint8_t* payload,
    size_t length
)
{
    switch (type)
    {
        case WStype_CONNECTED:
            Serial.println("WebSocket Connected!");
            break;

        case WStype_DISCONNECTED:
            Serial.println("WebSocket Disconnected!");
            break;

        case WStype_TEXT:
            Serial.print("Message from Python: ");
            Serial.write(payload, length);
            Serial.println();
            break;

        default:
            break;
    }
}

void websocket_init(
    const char* server_ip,
    uint16_t server_port
)
{
    ws.begin(server_ip, server_port, "/");
    // ws.enableHeartbeat(15000, 3000, 2);

    ws.onEvent(websocket_event);

    ws.setReconnectInterval(1000);

    Serial.println("WebSocket client initialized");
}

void websocket_loop()
{
    ws.loop();
}

bool websocket_is_connected()
{
    return ws.isConnected();
}

void websocket_send(const char* message)
{
    if (ws.isConnected())
    {
        ws.sendTXT(message);
    }
}

// void websocket_send_binary(uint8_t* data, size_t length)
// {
//     if (ws.isConnected())
//     {
//         ws.sendBIN(data, length);
//     }
// }

bool websocket_send_binary(uint8_t* data, size_t length)
{
    if (ws.isConnected())
    {
        return ws.sendBIN(data, length); // retirn true if the data was sent successfully, false otherwise
    }

    return false;
}