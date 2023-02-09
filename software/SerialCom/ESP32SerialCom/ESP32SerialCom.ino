/**********************************************************************
* Filename    : Blink
* Description : Make an led blinking.
* Auther      : www.freenove.com
* Modification: 2020/07/11
**********************************************************************/
#define LED_BUILTIN  2
// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200); 
  // Serial.println("HELLO FROM ESP32 YA GAY FUCK"); 
}

// the loop function runs over and over again forever
void loop() {
  if(Serial.available() > 0) 
  {
    char data = Serial.read(); 
    Serial.println(data); 
  }
  // Serial.println("HELLO FROM ESP32 YA GAY FUCK"); 
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  delay(1000);                       // wait for a second
}
