
#include "wifi_manager.h"
#include <WiFi.h>

static const char* WIFI_SSID = "SLT-Fiber-2.4G_2880";
static const char* WIFI_PASSWORD = "coin6657";
/*const char* ssid = "SLT-Fiber-2.4G_2880";
const char* password = "coin6657";*/
void wifi_init()
{
    WiFi.mode(WIFI_STA);

    Serial.println("Connecting to WiFi...");

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWiFi Connected!");
}

bool wifi_is_connected()
{
    return WiFi.status() == WL_CONNECTED;
}

void wifi_print_ip()
{
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP());
}
