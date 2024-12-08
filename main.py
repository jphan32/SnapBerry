import tkinter as tk
from PIL import Image, ImageTk
from picamera2 import Picamera2
import RPi.GPIO as GPIO  # GPIO 제어를 위한 라이브러리 추가
from CSNA2Printer import CSNA2Printer  # 프린터 클래스 import 추가

# GPIO 설정
BUTTON_PIN = 5  # GPIO 5번 핀 사용 (물리적 핀 번호 29번)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # 풀업 저항 설정

# GUI 창 생성 및 설정
root = tk.Tk()
root.title("My GUI")
root.geometry("800x480")
# root.attributes('-fullscreen', True)  # 전체화면 모드 설정

# ESC 키를 눌렀을 때 전체화면 종료
def exit_fullscreen(event):
    root.attributes('-fullscreen', False)
    root.geometry('800x480')

root.bind('<Escape>', exit_fullscreen)  # ESC 키 바인딩

# Picamera2 객체 생성 및 시작
picam2 = Picamera2()
picam2.start()

# 카메라 이미지를 표시할 레이블 생성
camara_place_label = tk.Label(root)
camara_place_label.pack(anchor=tk.NW)

# 카메라 업데이트 제어를 위한 플래그
is_previewing = True

# GPIO 버튼 이벤트 처리 함수
def button_callback(channel):
    if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # 버튼이 눌렸을 때
        take_photo()

# GPIO 이벤트 감지 설정
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

# 사진 촬영 함수
def take_photo():
    global is_previewing

    if is_previewing:  # 프리뷰 모드일 때 - 사진 촬영
        is_previewing = False
        frame = picam2.capture_array()
        color_img = Image.fromarray(frame)

        # 흑백 변환 및 이미지 처리
        gray_img = color_img.convert('1')   # 이진 흑백으로 변환
        gray_img = gray_img.resize((512, 384))
        # gray_img = gray_img.point(lambda x: 0 if x < 64 else 255)

        # 처리된 이미지 표시
        camera_image = ImageTk.PhotoImage(image=gray_img)
        camara_place_label.config(image=camera_image)
        camara_place_label.image = camera_image

        # "출력중" 메시지 표시
        take_photo_button.config(text="Printing...", state=tk.DISABLED)
        
        # 프린터로 이미지 출력
        try:
            printer = CSNA2Printer("/dev/ttyS0")
            printer.reset()
            printer.print_bitmap(gray_img)
            printer.feed(6)
            printer.cut_paper()
            printer.close()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            take_photo_button.config(text="Take Photo", state=tk.NORMAL)

    else:  # 촬영된 상태일 때 - 프리뷰 모드로 복귀
        is_previewing = True
        take_photo_button.config(text="Take Photo")

# 촬영 버튼 생성 및 우측 하단 배치
take_photo_button = tk.Button(root, text="Take Photo", command=take_photo)
take_photo_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)


# 카메라 이미지를 업데이트하는 함수
def update_image():
    if is_previewing:
        frame = picam2.capture_array()
        color_img = Image.fromarray(frame)
        color_img = color_img.resize((512, 384))
        camera_image = ImageTk.PhotoImage(image=color_img)
        camara_place_label.config(image=camera_image)
        camara_place_label.image = camera_image
    root.after(50, update_image)

update_image()  # 이미지 업데이트 시작

# 프로그램 종료 시 GPIO 정리
def on_closing():
    GPIO.cleanup()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()  # GUI 루프 시작
