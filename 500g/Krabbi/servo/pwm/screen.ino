#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

#define OLED_RESET -1  // Reset pin not used for most I2C modules
#define SCREEN_ADDRESS 0x3C  // Common I2C address (sometimes 0x3D)

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
  Serial.begin(9600);

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("SSD1306 allocation failed");
    while (1);
  }

  display.clearDisplay();

  display.setTextSize(2);       // 1 = small, 2 = medium, etc.
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);

  display.println("Hello Ali");
  display.println("SSD1306!");

  display.display();  // Push buffer to screen
}

void loop() {
  // Nothing needed here
}