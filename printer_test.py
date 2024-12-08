from CSNA2Printer import CSNA2Printer
from PIL import Image
import time

def main():
    # 프린터 초기화 
    printer = CSNA2Printer("/dev/ttyS0")  # Raspberry Pi GPIO UART
    
    try:
        # 프린터 리셋
        printer.reset()
        
        # 텍스트 출력 테스트
        printer.set_print_mode(0)  # 기본 폰트
        printer.print_text("Hello World!\n")
        
        printer.feed(1)  # 1줄 띄우기
        
        # 이미지 출력 테스트
        image = Image.open("test_image.jpg")  # 테스트 이미지 파일
        printer.print_bitmap(image)
        
        printer.feed(3)  # 여유 공간
        printer.cut_paper()  # 용지 컷팅
        
    finally:
        printer.close()

if __name__ == "__main__":
    main()

