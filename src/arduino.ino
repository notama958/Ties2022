#include <Adafruit_NeoPixel.h>
#define Pixel_num 12 // number of NeoPixels
#define Pixel_pin 13 // output pin for led strip

int BLUE = 0;
int GREEN = 1;
int RED = 2;
int WHITE = 3;
int SOLENOID = 4;

// used solenoids pins
int sole[] = {3, 4, 5, 6, 7, 8, 9, 10, 11, 12};

// declare the led strip object
Adafruit_NeoPixel strip(Pixel_num, Pixel_pin, NEO_GRB + NEO_KHZ800);

void setup()
{
    Serial.begin(9600);
    strip.begin(); // Init Neopixel strip object
    strip.setBrightness(50);
    /************SET LED OFF*********************/
    for (uint16_t i = 0; i < strip.numPixels(); i++)
    {
        strip.setPixelColor(i, 0, 0, 0); // initially off
        if (i >= 0 && i <= 2)
            strip.setPixelColor(i, 255, 255, 255);
        if (i >= 9 && i <= 11)
            strip.setPixelColor(i, 255, 255, 255);
    }

    strip.show();
    for (int i = 3; i <= 12; i++)
    {
        pinMode(sole[i], OUTPUT);
    }
}

uint32_t pink_neon = strip.Color(255, 49, 49);
uint32_t green_neon = strip.Color(0, 250, 120);
uint32_t dark_cyan = strip.Color(240, 240, 245);
uint32_t white = strip.Color(255, 255, 255);
uint32_t off = strip.Color(0, 0, 0);

int current_mode = WHITE;  // current mode
int current_color = WHITE; // current color
const int time_wait = 100; // in ms

int index;    // iterator
char buf[40]; // buffer for character read from serial line

// serial read function
void serial_read()
{

    while (Serial.available() > 0)
    {
        char t = Serial.read();

        if (t > 13)
        {
            buf[index] = t;
            index++;
        }

        if (t == 10) // check if end of message LF
        {
            buf[index] = 0; // end of string
            index = 0;
        }

    } // end of while serial available

    Serial.print("You sent me: ");
    Serial.println(buf);
    if (strlen(buf) > 0)
    {
        if ((int)buf[0] - '0' >= 0 && (int)buf[0] - '0' <= 3)
        {
            // Serial.println((int)buf[0] - '0');
            current_color = (int)buf[0] - '0';
            current_mode = (int)buf[0] - '0';
        }
        else if ((int)buf[0] - '0' == 4)
        {
            current_mode = SOLENOID;
        }
        else
        {
            current_mode = current_color;
        }
    }

} // end of func

//////////////////////////////END OF MAIN FUCNTION/////////////////////////////////

int step = 5;
// breathing effect LED script
void breathingStrip()
{

    for (int i = 0; i <= 51; i = i + step)
    {
        for (int j = 3; j <= 8; j++)
        {
            if (current_color == RED)
                strip.setPixelColor(j, i, 0, 0);
            else if (current_color == GREEN)
                strip.setPixelColor(j, 0, i, 0);
            else if (current_color == BLUE)
                strip.setPixelColor(j, 0, 0, i);
            else
                strip.setPixelColor(j, i, i, i);
            strip.show();
        }
        delay(time_wait);
    }

    for (int i = 51; i >= 0; i = i - step)
    {
        for (int j = 3; j <= 8; j++)
        {
            if (current_color == RED)
                strip.setPixelColor(j, i, 0, 0);
            else if (current_color == BLUE)
                strip.setPixelColor(j, 0, i, 0);
            else if (current_color == GREEN)
                strip.setPixelColor(j, 0, 0, i);
            else
                strip.setPixelColor(j, i, i, i);
            strip.show();
        }
        delay(time_wait);
    }
}

void colorWipe()
{
    for (int j = 0; j < strip.numPixels(); j++)
    {
        if (current_color == RED)
            strip.setPixelColor(j, 255, 0, 0);
        else if (current_color == BLUE)
            strip.setPixelColor(j, 0, 255, 0);
        else if (current_color == GREEN)
            strip.setPixelColor(j, 0, 0, 255);
        else
            strip.setPixelColor(j, 255, 255, 255);
    }
    strip.show();
}

// solenoid control
void solenoid()
{
    Serial.println("Run solenoid");
    for (int i = 0; i < (sizeof(sole) / sizeof(*sole)); i += 2)
    {
        patternOut(sole[i + 1], sole[i]);
        delay(50);
    }
    delay(500);
    for (int i = 0; i < (sizeof(sole) / sizeof(*sole)); i += 2)
    {
        patternIn(sole[i + 1], sole[i]);
        delay(50);
    }
    current_mode = current_color;
    Serial.println(current_mode);
}

void patternIn(int dire, int pwm)
{
    digitalWrite(dire, HIGH);
    digitalWrite(pwm, 1);
    delay(25);
    digitalWrite(dire, HIGH);
    digitalWrite(pwm, 0);
}
void patternOut(int dire, int pwm)
{
    digitalWrite(dire, LOW);
    digitalWrite(pwm, 1);
    delay(25);
    digitalWrite(dire, LOW);
    digitalWrite(pwm, 0);
}

void loop()
{

    serial_read();

    // breathingStrip();
    colorWipe();

    if (current_mode == SOLENOID)
    {
        solenoid();
    }
}
