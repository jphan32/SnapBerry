import RPi.GPIO as GPIO
import time

# GPIO 설정
BUTTON_PIN = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    이전_상태 = GPIO.input(BUTTON_PIN)
    print("버튼 테스트를 시작합니다. Ctrl+C로 종료할 수 있습니다.")
    
    while True:
        현재_상태 = GPIO.input(BUTTON_PIN)
        
        # 버튼 상태가 변경되었을 때만 출력
        if 현재_상태 != 이전_상태:
            if 현재_상태 == GPIO.HIGH:
                print("버튼이 떨어졌습니다")
            else:
                print("버튼이 눌렸습니다")
            이전_상태 = 현재_상태
        
        time.sleep(0.1)  # CPU 사용량을 줄이기 위한 짧은 대기 시간

except KeyboardInterrupt:
    print("\n프로그램을 종료합니다.")
finally:
    GPIO.cleanup()  # GPIO 설정 초기화

