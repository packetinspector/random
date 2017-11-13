// Quick use of DHT and FastLED
// In production

//Includes
#include <dht.h>
#include "FastLED.h"
FASTLED_USING_NAMESPACE

//Make a DHT object
dht DHT;

//Setup Stuff
#define DHT22_PIN 5
#define NUM_LEDS 1
#define DATA_PIN 6
#define LED_TYPE    WS2812
#define COLOR_ORDER RGB

CRGB leds[NUM_LEDS];

struct
{
    uint32_t total;
    uint32_t ok;
    uint32_t crc_error;
    uint32_t time_out;
    uint32_t connect;
    uint32_t ack_l;
    uint32_t ack_h;
    uint32_t unknown;
} stat = { 0,0,0,0,0,0,0,0};

float ideal_temp = 72;

float high_temp = ideal_temp + 1.5;
float low_temp = ideal_temp - 1.5;

void setup()
{
    Serial.begin(115200);
    Serial.println("dht22_test.ino");
    Serial.print("LIBRARY VERSION: ");
    Serial.println(DHT_LIB_VERSION);
    Serial.println();
    Serial.println("Type,\tstatus,\tHumidity (%),\tTemperature (C)\tTime (us)");
    // initialize digital pin LED_BUILTIN as an output.
    FastLED.addLeds<LED_TYPE,DATA_PIN,COLOR_ORDER>(leds, NUM_LEDS);
    long unsigned int colors[] = {CRGB::Red, CRGB::Green, CRGB::Blue};
    for (int i=0; i <= 2; i++) {
        leds[0] = colors[i];
        //Fancy fade color for boot
        for (int j=0; j <= 255; j += 5) {
          FastLED.setBrightness(j);
          FastLED.show();
          delay(10);
        }
    }
    //Turn it off
    FastLED.clear();
}

void loop()
{
    // READ DATA
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.print("DHT22 \t");
    int chk = DHT.read22(DHT22_PIN);

    stat.total++;
    switch (chk)
    {
    case DHTLIB_OK:
        stat.ok++;
        Serial.print("OK,\t");
        break;
    case DHTLIB_ERROR_CHECKSUM:
        stat.crc_error++;
        Serial.print("Checksum error,\t");
        break;
    case DHTLIB_ERROR_TIMEOUT:
        stat.time_out++;
        Serial.print("Time out error,\t");
        break;
    default:
        stat.unknown++;
        Serial.print("Unknown error,\t");
        break;
    }
    Serial.println();
    float temp = DHT.temperature*1.8 + 32;

    if (stat.total % 20 == 0)
    {
        Serial.println("\nTOT\tOK\tCRC\tTO\tUNK");
        Serial.print(stat.total);
        Serial.print("\t");
        Serial.print(stat.ok);
        Serial.print("\t");
        Serial.print(stat.crc_error);
        Serial.print("\t");
        Serial.print(stat.time_out);
        Serial.print("\t");
        Serial.print(stat.connect);
        Serial.print("\t");
        Serial.print(stat.ack_l);
        Serial.print("\t");
        Serial.print(stat.ack_h);
        Serial.print("\t");
        Serial.print(stat.unknown);
        Serial.println("\n");
    }
    // Do Led Stuff
    digitalWrite(LED_BUILTIN, LOW);

    //Calculate Brightness
    // 50 - 255
    float diff = abs(ideal_temp - temp);
    float bright = 0 + (diff * 50);
    if (bright >= 250) {
        bright = 255;
    } else if (bright < 50) {
        bright = 50;
    }


    if (temp > high_temp) {
        leds[0] = CRGB::Red;
    } else if (temp < low_temp) {
        leds[0] = CRGB::Blue;
    } else {
        leds[0] = CRGB::Green;
    }
    FastLED.setBrightness(bright);
    FastLED.show();

    // Print Status
    Serial.print(" Humidity: ");
    Serial.print(DHT.humidity, 1);
    Serial.print("\% Temp: ");
    Serial.print(temp, 1);
    Serial.print("F Diff: ");
    Serial.print(diff, 1);
    Serial.print(" Brightness: ");
    Serial.print(bright);
    Serial.println();

    delay(4000);

}
//
// END OF FILE
//
