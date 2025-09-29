#define ENA 5 
#define ENB 6 
#define IN1 7 
#define IN2 8 
#define IN3 9
#define IN4 11 
int data1 = 0; 
void setup() { 
pinMode(IN1, OUTPUT); 
pinMode(IN2, OUTPUT); 
pinMode(IN3, OUTPUT); 
pinMode(IN4, OUTPUT); 
pinMode(ENA, OUTPUT); 
pinMode(ENB, OUTPUT); 
Serial.begin(115200); 
 
} 
void loop() {
 if (Serial.available() > 0) 
{ 
char c = Serial.read(); 
 data1 = c - '0'; 
Serial.print("Received: "); 
Serial.println(data1); 
if (data1 == 1) { 
// Forward 
digitalWrite(ENA, HIGH); 
digitalWrite(ENB, HIGH); 
digitalWrite(IN1, HIGH); 
digitalWrite(IN2, LOW); 
digitalWrite(IN3, HIGH); 
digitalWrite(IN4, LOW);
 } 
else if (data1 == 2) {
// Backward 
digitalWrite(ENA, HIGH); 
digitalWrite(ENB, HIGH); 
digitalWrite(IN1, LOW); 
digitalWrite(IN2, HIGH); 
digitalWrite(IN3, LOW); 
digitalWrite(IN4, HIGH); 
} 
else if (data1 == 3) { 
// Stop
digitalWrite(ENA, LOW); 
digitalWrite(ENB, LOW); 
digitalWrite(IN1, LOW); 
digitalWrite(IN2, LOW); 
digitalWrite(IN3, LOW); 
digitalWrite(IN4, LOW); 
} 
else { // Unknown input -> stop 
digitalWrite(ENA, LOW); 
digitalWrite(ENB, LOW); 
digitalWrite(IN1, LOW); 
digitalWrite(IN2, LOW); 
digitalWrite(IN3, LOW); 
digitalWrite(IN4, LOW); 
} 
} 
}
