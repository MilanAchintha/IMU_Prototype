
#include <WiFi.h>
#include <esp_wifi.h>

// Wi-Fi credentials
const char* ssid = "MAB";
const char* password = "1234567890";

String receivedCommand = "";

void readTSF()
{
    uint64_t tsf_time = esp_wifi_get_tsf_time(WIFI_IF_STA);

    Serial.println("--------- TSF TIME ---------");

    Serial.print("TSF: ");
    Serial.print((unsigned long long)tsf_time);
    Serial.println(" us");

    Serial.println("----------------------------");
}

void setup()
{
    Serial.begin(115200);

    // Connect to Wi-Fi
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);

    Serial.print("Connecting to WiFi");

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("WiFi Connected");

    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());

    Serial.println("Waiting for START command...");
}

void loop()
{
    // Check for incoming Serial data
    if (Serial.available())
    {
        receivedCommand = Serial.readStringUntil('\n');
        receivedCommand.trim();

        if (receivedCommand == "START")
        {
            Serial.println("START command received!");

            readTSF();
        }
    }
}
