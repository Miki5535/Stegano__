from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QPushButton, QLabel, QLineEdit, 
    QTextEdit, QComboBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
import os
import random
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import cv2
import numpy as np
from PIL import Image
import wave
import struct

class SteganographyHelper:
    @staticmethod
    def hide_in_image_lsb(image_path, message):
        img = cv2.imread(image_path)
        binary_message = ''.join(format(ord(i), '08b') for i in message)
        data_index = 0
        
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                for k in range(3):
                    if data_index < len(binary_message):
                        img[i, j, k] = (img[i, j, k] & 254) | int(binary_message[data_index])
                        data_index += 1
        
        return img

    @staticmethod
    def hide_in_audio_meta(audio_path, message):
        with wave.open(audio_path, 'rb') as audio_file:
            frames = audio_file.readframes(audio_file.getnframes())
            params = audio_file.getparams()
        
        # Add message to metadata
        with wave.open(audio_path + '_hidden.wav', 'wb') as output:
            output.setparams(params)
            output.writeframes(frames)
            # Add custom metadata (simplified)
            output._file.write(message.encode())
        
        return audio_path + '_hidden.wav'

class EncryptionHelper:
    @staticmethod
    def aes_encrypt(message, key, mode='ECB'):
        # Pad key to 32 bytes
        key = key.ljust(32)[:32].encode()
        message = message.encode()
        
        if mode == 'ECB':
            cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=default_backend())
        elif mode == 'CBC':
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        elif mode == 'CFB':
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
        
        encryptor = cipher.encryptor()
        # Pad message to be multiple of 16
        padded_message = message + b' ' * (16 - len(message) % 16)
        return encryptor.update(padded_message) + encryptor.finalize()

class IntegrationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.steganography_helper = SteganographyHelper()
        self.encryption_helper = EncryptionHelper()

    def initUI(self):
        layout = QVBoxLayout()

        # Integration Mode Group
        integration_group = QGroupBox("โหมดบูรณาการ")
        integration_layout = QVBoxLayout()

        # Message Input
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("ข้อความที่ต้องการซ่อน")
        self.message_input.setMaximumHeight(100)

        # File Selection
        self.file_select_button = QPushButton("เลือกไฟล์ที่จะซ่อนข้อมูล")
        self.file_select_button.clicked.connect(self.select_file)
        self.selected_file_label = QLabel("ยังไม่ได้เลือกไฟล์")

        # Hiding Mode Selection
        self.hide_mode_selector = QComboBox()
        self.hide_mode_selector.addItems([
            "LSB ในรูปภาพ",
            "Palette-based ในรูปภาพ",
            "ซ่อนในเมตาดาต้าของเสียง",
            "ซ่อนในเมตาดาต้าของวิดีโอ"
        ])

        # Encryption Mode Selection
        self.encryption_selector = QComboBox()
        self.encryption_selector.addItems([
            "ไม่เข้ารหัส",
            "AES-ECB",
            "AES-CBC",
            "AES-CFB",
            "AES-OFB",
            "AES-GCM"
        ])

        # Encryption Key
        self.encryption_key_input = QLineEdit()
        self.encryption_key_input.setPlaceholderText("คีย์สำหรับการเข้ารหัส")

        # Start Button
        self.start_button = QPushButton("เริ่มกระบวนการซ่อนข้อมูล")
        self.start_button.clicked.connect(self.start_integration)
        self.start_button.setStyleSheet("background-color: #4CAF50; color: white;")

        # Result Output
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Courier New', monospace;
            }
        """)

        # Add widgets to layout
        integration_layout.addWidget(QLabel("ข้อความ:"))
        integration_layout.addWidget(self.message_input)
        integration_layout.addWidget(self.file_select_button)
        integration_layout.addWidget(self.selected_file_label)
        integration_layout.addWidget(QLabel("วิธีการซ่อน:"))
        integration_layout.addWidget(self.hide_mode_selector)
        integration_layout.addWidget(QLabel("วิธีการเข้ารหัส:"))
        integration_layout.addWidget(self.encryption_selector)
        integration_layout.addWidget(QLabel("คีย์เข้ารหัส:"))
        integration_layout.addWidget(self.encryption_key_input)
        integration_layout.addWidget(self.start_button)

        integration_group.setLayout(integration_layout)
        layout.addWidget(integration_group)
        layout.addWidget(QLabel("ผลลัพธ์:"))
        layout.addWidget(self.result_output)
        
        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "เลือกไฟล์",
            "",
            "Images (*.png *.jpg);;Audio (*.wav);;Video (*.mp4)"
        )
        if file_path:
            self.selected_file_label.setText(file_path)

    def start_integration(self):
        message = self.message_input.toPlainText()
        hide_mode = self.hide_mode_selector.currentText()
        encryption_mode = self.encryption_selector.currentText()
        encryption_key = self.encryption_key_input.text()
        file_path = self.selected_file_label.text()

        if not message:
            QMessageBox.warning(self, "คำเตือน", "กรุณากรอกข้อความที่ต้องการซ่อน")
            return

        if file_path == "ยังไม่ได้เลือกไฟล์":
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกไฟล์ที่จะซ่อนข้อมูล")
            return

        try:
            # Encryption step
            if encryption_mode != "ไม่เข้ารหัส":
                self.result_output.append(f"กำลังเข้ารหัสด้วย {encryption_mode}...")
                encrypted_message = self.encryption_helper.aes_encrypt(
                    message,
                    encryption_key,
                    encryption_mode.split('-')[1] if '-' in encryption_mode else 'ECB'
                )
                message = encrypted_message.hex()

            # Hiding step
            self.result_output.append(f"กำลังซ่อนข้อมูลด้วยวิธี {hide_mode}...")
            
            if "LSB" in hide_mode:
                output_image = self.steganography_helper.hide_in_image_lsb(file_path, message)
                cv2.imwrite('output.png', output_image)
                self.result_output.append("บันทึกไฟล์ที่ซ่อนข้อมูลแล้วเป็น 'output.png'")
            
            elif "เสียง" in hide_mode:
                output_path = self.steganography_helper.hide_in_audio_meta(file_path, message)
                self.result_output.append(f"บันทึกไฟล์เสียงที่ซ่อนข้อมูลแล้วเป็น '{output_path}'")
            
            self.result_output.append("การซ่อนข้อมูลเสร็จสมบูรณ์!")

        except Exception as e:
            self.result_output.append(f"เกิดข้อผิดพลาด: {str(e)}")
            QMessageBox.critical(self, "ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการทำงาน: {str(e)}")

    def extract_data(self):
        # Implementation for data extraction (to be added)
        pass