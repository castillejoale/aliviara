int thumb = A1;
int index = A2;
int middle = A3;
int ring = A4;
int pinky = A5;
int thumbVal;
int indexVal;
int middleVal;
int ringVal;
int pinkyVal;

void setup() {
  // put your setup code here, to run once:
  pinMode(thumb, INPUT);
  pinMode(index, INPUT);
  pinMode(middle, INPUT);
  pinMode(ring, INPUT);
  pinMode(pinky, INPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  thumbVal = analogRead(thumb);
  indexVal = analogRead(index);
  middleVal = analogRead(middle);
  ringVal = analogRead(ring);
  pinkyVal = analogRead(pinky);
//  thumb = map(thumbVal, 600, 900, 0, 180);
  Serial.print("Thumb: ");
  Serial.println(thumbVal);
  Serial.print("Index: ");
  Serial.println(indexVal);
  Serial.print("Middle: ");
  Serial.println(middleVal);
  Serial.print("Ring: ");
  Serial.println(ringVal);
  Serial.print("Pinky: ");
  Serial.println(pinkyVal);
  Serial.println("-----------------------");
  delay(500);
  
}
