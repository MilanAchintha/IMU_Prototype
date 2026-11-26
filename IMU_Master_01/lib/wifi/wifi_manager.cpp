
#include "wifi_manager.h"
#include <WiFi.h>

// const char* WIFI_SSID = "Dialog 4G 856";
// const char* WIFI_PASSWORD = "9ac026F1";

// const char* WIFI_SSID = "MAB";
// const char* WIFI_PASSWORD = "1234567890";

const char* WIFI_SSID = "SLT-Fiber-2.4G_2880";
const char* WIFI_PASSWORD = "coin6657";



void wifi_init()
{
    WiFi.mode(WIFI_STA);

    WiFi.setSleep(false); // Normally, ESP32 Wi-Fi can enter a power-saving mode during periods of inactivity.
    WiFi.setTxPower(WIFI_POWER_19_5dBm);     // maximum transmit power Controls how strongly the ESP32 transmits its Wi-Fi radio signal.
    WiFi.setAutoReconnect(true);


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
