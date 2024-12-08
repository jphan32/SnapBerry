import serial
import time
from PIL import Image
import numpy as np


class CSNA2Printer:
    def __init__(self, port="/dev/ttyS0", baudrate=9600):
        """Initialize printer with TTL serial connection
        
        Args:
            port (str): Serial port name
            baudrate (int): Baud rate for serial communication (default 115200)
        """
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE
        )
        time.sleep(2)  # Wait for printer to initialize
        
    def reset(self):
        """Initialize printer"""
        self.serial.write(bytes([0x1B, 0x40]))  # ESC @
        time.sleep(0.1)
        
    def set_print_mode(self, mode=0):
        """Set print mode
        Args:
            mode (int): Print mode bitmask
                Bit 0: Font selection (0: Font A, 1: Font B)
                Bit 1: Undefined
                Bit 2: Emphasized
                Bit 3: Double height
                Bit 4: Double width
                Bit 5: Undefined
                Bit 6: Strike
                Bit 7: Undefined
        """
        self.serial.write(bytes([0x1B, 0x21, mode]))
        
    def set_line_spacing(self, dots=30):
        """Set line spacing in dots
        Args:
            dots (int): Line spacing (0-255)
        """
        self.serial.write(bytes([0x1B, 0x33, dots]))
        
    def print_text(self, text):
        """Print text
        
        Args:
            text (str): Text to print (can include newlines)
        """
        # Split text into lines and process each line
        lines = text.split('\n')
        for line in lines:
            # Send the text line
            self.serial.write(line.encode('ascii', 'replace'))
            # Send CR/LF
            self.serial.write(bytes([0x0D, 0x0A]))  # CR LF
            time.sleep(0.01)
    
    def print_bitmap(self, image):
        """Print image using 'Print raster bit image' command in Normal Mode"""
        # Ensure image is in mode 1 (binary)
        if image.mode != '1':
            img = image.convert('1')
        else:
            img = image.copy()

        # Determine printer dimensions
        printer_width = 384  # Fixed printer width in pixels
        max_height = 2000    # Set a reasonable max height (adjust as needed)

        # Calculate scale ratio to fit within printer width and max height
        scale_width_ratio = printer_width / float(img.size[0])
        new_height = int(float(img.size[1]) * scale_width_ratio)
        
        # If the scaled height exceeds max height, scale down further
        if new_height > max_height:
            scale_height_ratio = max_height / float(new_height)
            new_width = int(printer_width * scale_height_ratio)
            img = img.resize((new_width, max_height), Image.LANCZOS)
        else:
            img = img.resize((printer_width, new_height), Image.LANCZOS)

        # Convert image to binary array
        img_bin = np.array(img, dtype=np.uint8)

        # Set raster bit image parameters
        bytes_per_row = img.width // 8
        xL = bytes_per_row & 0xFF
        xH = (bytes_per_row >> 8) & 0xFF
        yL = img.height & 0xFF
        yH = (img.height >> 8) & 0xFF

        # Send GS v 0 m xL xH yL yH command (Normal mode: m=0)
        self.serial.write(bytes([0x1D, 0x76, 0x30, 0x00, xL, xH, yL, yH]))

        # Process image row by row
        for y in range(img.height):
            row_data = []
            for x in range(bytes_per_row):
                byte = 0
                for bit in range(8):
                    pixel_x = x * 8 + bit
                    if pixel_x < img.width and img_bin[y, pixel_x] == 0:  # Black pixel
                        byte |= (1 << (7 - bit))
                row_data.append(byte)

            # Send row data
            self.serial.write(bytes(row_data))

        # Line feed after the image
        self.serial.write(bytes([0x0A]))
        time.sleep(0.1)

    def set_text_size(self, width=0, height=0):
        """Set text size
        Args:
            width (int): 0-7 for width multiplier
            height (int): 0-7 for height multiplier
        """
        size = (width & 0x0F) << 4 | (height & 0x0F)
        self.serial.write(bytes([0x1D, 0x21, size]))
        
    def feed(self, lines=1):
        """Feed paper
        Args:
            lines (int): Number of lines to feed
        """
        for _ in range(lines):
            self.serial.write(bytes([0x0A]))  # LF
            time.sleep(0.01)
        
    def cut_paper(self):
        """Full cut paper"""
        self.serial.write(bytes([0x1B, 0x69]))  # ESC i
        time.sleep(0.1)
        
    def close(self):
        """Close serial connection"""
        self.serial.close()

