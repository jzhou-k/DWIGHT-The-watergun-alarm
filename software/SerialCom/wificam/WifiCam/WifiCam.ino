#include "WifiCam.hpp"
#include <WiFi.h>
#include <Servo.h>

//declarations for oled display
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

#define OLED_SDA 21
#define OLED_SCL 22
#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32

String hour = "g";
String minute = "a";
String second = "y";
String alarmHour = "haha";
String alarmMinute = "I'm dying inside";
String timeInfo = "";
bool myAlarm = false;

float x_angle = 90;
float y_angle = 90;
float rawx_angle = 90;
float rawy_angle = 90;
int triggerInfo = 0;
int sweepInfo = 0;
String angle_info = "";


Servo xservo;
Servo yservo;
Servo triggerServo;
static const int yServoPin = 32;
static const int xServoPin = 33;
static const int triggerServoPin = 12; //to be determined

boolean data_received = false ;
bool alarm_data_received = false; 
boolean start_sweep = false;

void calibrateXangle();
void calibrateYangle();
float parseXinfo(String data);
float parseYinfo(String data);
int parseSinfo(String data);
void serialEvent();
void trigger();
void initalizeGun();
void sweep(int y, int xStart, int xEnd);
void displayTime();
void parseTimeHour(String data);
void parseTimeMinute(String data);
void parseTimeSecond(String data);


static const char* WIFI_SSID = "BELL011";
static const char* WIFI_PASS = "69D19EFEA96F";
esp32cam::Resolution initialResolution;


WebServer server(80);

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

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

void setup()
{
  Serial.begin(115200);
  Serial.println();
  delay(2000);

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;); // Don't proceed, loop forever
  }

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

 
  yservo.attach(
    yServoPin,
    Servo::CHANNEL_NOT_ATTACHED,
    50,
    250
  );
  xservo.attach(
    xServoPin,
    Servo::CHANNEL_NOT_ATTACHED,
    50,
    250

  );

  triggerServo.attach(
    triggerServoPin,
    Servo::CHANNEL_NOT_ATTACHED,
    //100, 200 no go
    //15, 100 kinda??
    15,
    200
  );

  // triggerServo.write(0);
  initalizeGun();


  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  if (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("WiFi failure");
    delay(5000);
    ESP.restart();
  }
  Serial.println("WiFi connected");

  {
    using namespace esp32cam;

    initialResolution = Resolution::find(1024, 768);

    Config cfg;
    cfg.setPins(pins::FreeNove);
    cfg.setResolution(initialResolution);
    cfg.setJpeg(80);

    bool ok = Camera.begin(cfg);
    if (!ok) {
      Serial.println("camera initialize failure");
      delay(5000);
      ESP.restart();
    }
    Serial.println("camera initialize success");
  }

  Serial.println("camera starting");
  Serial.print("http://");
  Serial.println(WiFi.localIP());

  addRequestHandlers();
  server.begin();
}
//***********************************************************
void loop()
{
  server.handleClient();

  serialEvent();
  displayTime(); 
  if (data_received)
  {

    if (sweepInfo == 1 && !start_sweep)
    {
      sweep(87, 105, 115);
      start_sweep = true;
    }
    else
    {
      sweepInfo = 0;
      start_sweep = false;
      xservo.write(x_angle);
      yservo.write(y_angle);

      if (triggerInfo == 1)
      {
        trigger();
      }

    }


  }


  triggerInfo = 0;
  //calibrateEvery();

  delay(1);

}
//***********************************************************

void initalizeGun()
{

  delay(1000);
  for (int i = 90; i > 10; i -= 10)
  {
    yservo.write(i);
    delay(10);
  }


}

void calibrateEvery()
{
  calibrateYangle();
  delay(1000);
  calibrateZangle();
  delay(1000);
  calibrateXangle();
}


void calibrateZangle()
{
  delay(100);
  triggerServo.write(45);
  delay(200);
  triggerServo.write(20);
  delay(500);
}

void calibrateXangle()
{
  delay(5000);
  xservo.write(45);
  delay(5000);
  xservo.write(90);
  delay(5000);
  xservo.write(135);
  delay(5000);
  xservo.write(90);

}


void calibrateYangle()
{
  delay(5000);
  yservo.write(85);
  delay(5000);
  yservo.write(90);
  delay(5000);
  yservo.write(95);
  delay(5000);
  yservo.write(90);
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
  Serial.println("display");
  delay(10);
}



void serialEvent()
{
  if (Serial.available() > 0)
  {
    char data = Serial.read();
    angle_info += data;
    // Serial.println(data);

    //Serial.println(Serial.available());
    if (data == '#')
    {

      x_angle =  parseXinfo(angle_info);
      y_angle = parseYinfo(angle_info);
      triggerInfo = parseZinfo(angle_info);
      sweepInfo = parseSinfo(angle_info);
      data_received = true;
      angle_info = "";
    } 
    else
    {
      data_received = false;
    }

    if(data == 'T')
    {
      parseTimeHour(timeInfo);
      parseTimeMinute(timeInfo);
      parseTimeSecond(timeInfo);
      timeInfo = "";
      alarm_data_received = true;
      if (!myAlarm)
      {
        //registers the first time string as alarm time
        alarmHour = hour;
        alarmMinute = minute;
        myAlarm = true;
      }
    }else 
    {
      alarm_data_received = false; 
    }


  }

}

float parseXinfo(String data)
{
  // X25Y25Z0#
  data.remove(data.indexOf("Y")); //removes Y25 since remove() gets rid of everything to the end of the string
  data.remove(data.indexOf("X"), 1); //removes X

  return data.toFloat();
}

float parseYinfo(String data)
{
  data.remove(data.indexOf("X"), data.indexOf("Y") + 1);
  data.remove(data.indexOf("Z"));
  return data.toFloat();
}

int parseZinfo(String data)
{
  // 1 to shoot 0 to not shoot
  data.remove(data.indexOf("X"), data.indexOf("Z") + 1);
  data.remove(data.indexOf("S"));
  return data.toInt();
}

int parseSinfo(String data)
{
  // 1 to shoot 0 to not shoot
  data.remove(data.indexOf("X"), data.indexOf("S") + 1);
  data.remove(data.indexOf("#"));
  return data.toInt();
}

void trigger()
{

  //manual control mode
  delay(100);
  triggerServo.write(55);
  delay(200);
  triggerServo.write(20);
  delay(100);

}

//pass in angle
void sweep(int y, int xStart, int xEnd)
{
  int iter = int((xEnd - xStart) / 5);
  yservo.write(y);
  for (int i = xStart; i < xEnd; i += iter)
  {
    xservo.write(i);
    delay(1500);
    trigger();
    delay(300);
  }

  delay(1000);
  xservo.write(90);
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


//initial calibration of watergun -> lean back the watergun
//if trigger = true -> shooot
//if face stay in place for 5 sec (with tolerace) shoot
