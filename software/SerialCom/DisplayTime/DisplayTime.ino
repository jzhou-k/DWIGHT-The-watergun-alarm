/**************************************************************************
  This is an example for our Monochrome OLEDs based on SSD1306 drivers

  Pick one up today in the adafruit shop!
  ------> http://www.adafruit.com/category/63_98

  This example is for a 128x64 pixel display using I2C to communicate
  3 pins are required to interface (two I2C and one reset).

  Adafruit invests time and resources providing this open
  source code, please support Adafruit and open-source
  hardware by purchasing products from Adafruit!

  Written by Limor Fried/Ladyada for Adafruit Industries,
  with contributions from the open source community.
  BSD license, check license.txt for more information
  All text above, and the splash screen below must be
  included in any redistribution.
 **************************************************************************/

#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

// Declaration for an SSD1306 display connected to I2C (SDA, SCL pins)
// The pins for I2C are defined by the Wire-library.
// On an arduino UNO:       A4(SDA), A5(SCL)
// On an arduino MEGA 2560: 20(SDA), 21(SCL)
// On an arduino LEONARDO:   2(SDA),  3(SCL), ...



#define OLED_SDA 21
#define OLED_SCL 22
#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

//global variable is caca
String hour = "g";
String minute = "a";
String second = "y";
String alarmHour = "haha";
String alarmMinute = "I'm dying inside";
String timeInfo = "";
bool alarmMode = false;


static const unsigned char PROGMEM logo_bmp[] =
{ 0b00000000, 0b11000000,
  0b00000001, 0b11000000,
  0b00000001, 0b11000000,
  0b00000011, 0b11100000,
  0b11110011, 0b11100000,
  0b11111110, 0b11111000,
  0b01111110, 0b11111111,
  0b00110011, 0b10011111,
  0b00011111, 0b11111100,
  0b00001101, 0b01110000,
  0b00011011, 0b10100000,
  0b00111111, 0b11100000,
  0b00111111, 0b11110000,
  0b01111100, 0b11110000,
  0b01110000, 0b01110000,
  0b00000000, 0b00110000
};

void setup() {
  Serial.begin(115200);

  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;); // Don't proceed, loop forever
  }

  // Show initial display buffer contents on the screen --
  // the library initializes this with an Adafruit splash screen.
  display.display();
  delay(2000); // Pause for 2 seconds

  // Clear the buffer
  display.clearDisplay();

  // Draw a single pixel in white
  display.drawPixel(10, 10, SSD1306_BLACK);

  // Show the display buffer on the screen. You MUST call display() after
  // drawing commands to make them visible on screen!
  display.display();
  delay(2000);


  // Invert and restore display, pausing in-between
  display.invertDisplay(true);
  delay(1000);
  display.invertDisplay(false);
  delay(1000);
}

void loop() {

  readSerial();

  //get alarm time once, since there will be a delay between sending alarm and current time


  displayTime();

  delay(1);

}


void displayTime()
{
  display.clearDisplay();

  display.setTextSize(2);      // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE); // Draw white text
  display.setCursor(0, 0);     // Start at top-left corner
  display.cp437(true);         // Use full 256 char 'Code Page 437' font

  // Not all the characters will fit on the display. This is normal.
  // Library will draw what it can and the rest will be clipped.
  display.println(F("TIME:"));
  display.print(hour + ":");
  display.print(minute + ":");
  display.print(second);
  display.println("");

  display.println(F("AlarmTime:"));
  display.print(alarmHour + ":");
  display.print(alarmMinute + ":)");

  display.display();
  delay(10);
}



//18:20:11#
void parseTimeHour(String data)
{
  data.remove(data.indexOf(":"));
  hour = data;
}

void parseTimeMinute(String data)
{
  data.remove(0, data.indexOf(":") + 1); //removes 18:
  data.remove(data.indexOf(":"));
  minute = data;
}


void parseTimeSecond(String data)
{
  //myString.remove(index, count)
  data.remove(0, data.indexOf(":") + 1); //removes 18:
  data.remove(0, data.indexOf(":") + 1); //removes 18:
  data.remove(data.indexOf("T"));
  second = data;
}


void readSerial()
{
  if (Serial.available() > 0)
  {
    char data = Serial.read();
    timeInfo += data;
    // Serial.println(data);

    //Serial.println(Serial.available());
    if (data == 'T')
    {
      parseTimeHour(timeInfo);
      parseTimeMinute(timeInfo);
      parseTimeSecond(timeInfo);
      timeInfo = "";


      if (!alarm)
      {
        //registers the first time string as alarm time
        alarmHour = hour;
        alarmMinute = minute;
        alarm = true;
      }

    }



  }
}
