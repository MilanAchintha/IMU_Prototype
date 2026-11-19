
#include "wifi_manager.h"
#include <WiFi.h>

static const char* WIFI_SSID = "MAB";
static const char* WIFI_PASSWORD = "1234567890";

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
