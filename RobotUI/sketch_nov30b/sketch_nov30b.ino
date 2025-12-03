// 핀 정의
const int ledPins[4] = {12, 10, 8, 6};
const int buttonPins[4] = {13, 11, 9, 7};

// 버튼에 대응하는 메시지 정의
const char* onMsgs[4] = {"button1_on", "button2_on", "button3_on", "button4_on"};
const char* offMsgs[4] = {"button1_off", "button2_off", "button3_off", "button4_off"};

int prevButtonStates[4] = {HIGH, HIGH, HIGH, HIGH};
bool isActive[4] = {false, false, false, false};

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < 4; i++) {
    pinMode(ledPins[i], OUTPUT);
    pinMode(buttonPins[i], INPUT_PULLUP);
  }
}

void loop() {

  // ---------------------------------------------------------
  // 1) 버튼 입력 처리 (기존 기능 유지)
  // ---------------------------------------------------------
  for (int i = 0; i < 4; i++) {
    int current = digitalRead(buttonPins[i]);

    if (current == LOW && prevButtonStates[i] == HIGH) {
      isActive[i] = !isActive[i];

      if (isActive[i]) {
        digitalWrite(ledPins[i], HIGH);
        Serial.println(onMsgs[i]);
      } else {
        digitalWrite(ledPins[i], LOW);
        Serial.println(offMsgs[i]);
      }
      delay(200);
    }

    prevButtonStates[i] = current;
  }

  // ---------------------------------------------------------
  // 2) PC → Arduino Serial 명령 처리 (신규 기능)
  // ---------------------------------------------------------
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    // button1_on_pc ~ button4_on_pc
    if      (cmd == "button1_on_pc")  digitalWrite(ledPins[0], HIGH);
    else if (cmd == "button1_off_pc") digitalWrite(ledPins[0], LOW);

    else if (cmd == "button2_on_pc")  digitalWrite(ledPins[1], HIGH);
    else if (cmd == "button2_off_pc") digitalWrite(ledPins[1], LOW);

    else if (cmd == "button3_on_pc")  digitalWrite(ledPins[2], HIGH);
    else if (cmd == "button3_off_pc") digitalWrite(ledPins[2], LOW);

    else if (cmd == "button4_on_pc")  digitalWrite(ledPins[3], HIGH);
    else if (cmd == "button4_off_pc") digitalWrite(ledPins[3], LOW);

    // 필요하면 ack 보낼 수도 있음:
    // Serial.println("ack");
  }
}
