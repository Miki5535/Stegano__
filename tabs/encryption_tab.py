from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLineEdit, QComboBox, QPushButton, QLabel, QTextEdit
)
from PyQt5.QtCore import Qt
from cryptography.fernet import Fernet
from Crypto.Cipher import AES, Blowfish, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
import base64


class EncryptionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        encrypt_group = QGroupBox("การเข้ารหัส")
        encrypt_layout = QVBoxLayout()
        
        # Dropdown for selecting encryption method
        self.encryption_combo = QComboBox()
        self.encryption_combo.addItems(["AES", "RSA", "Blowfish", "Fernet"])
        
        # Input for message and key
        self.encryption_message_input = QLineEdit()
        self.encryption_message_input.setPlaceholderText("ข้อความที่ต้องการเข้ารหัส")
        
        self.encryption_key_input = QLineEdit()
        self.encryption_key_input.setPlaceholderText("คีย์สำหรับเข้ารหัส (ถ้าจำเป็น)")
        
        # Output area for encrypted/decrypted message
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Consolas', monospace;
            }
        """)
        
        # Button for encryption
        self.encrypt_button = QPushButton("เข้ารหัส")
        self.encrypt_button.clicked.connect(self.encrypt_message)
        self.encrypt_button.setStyleSheet("background-color: green; color: white;")
        
        # Button for decryption
        self.decrypt_button = QPushButton("ถอดรหัส")
        self.decrypt_button.clicked.connect(self.decrypt_message)
        self.decrypt_button.setStyleSheet("background-color: orange; color: white;")
        
        # Add widgets to layout
        encrypt_layout.addWidget(QLabel("เลือกวิธีการเข้ารหัส:"))
        encrypt_layout.addWidget(self.encryption_combo)
        encrypt_layout.addWidget(self.encryption_message_input)
        encrypt_layout.addWidget(self.encryption_key_input)
        encrypt_layout.addWidget(self.encrypt_button)
        encrypt_layout.addWidget(self.decrypt_button)
        encrypt_layout.addWidget(QLabel("ผลลัพธ์:"))
        encrypt_layout.addWidget(self.result_output)
        
        encrypt_group.setLayout(encrypt_layout)
        layout.addWidget(encrypt_group)
        
        self.setLayout(layout)

    def encrypt_message(self):
        message = self.encryption_message_input.text()
        key = self.encryption_key_input.text()
        encryption_type = self.encryption_combo.currentText()

        if not message:
            self.result_output.append("<font color='red'>กรุณาใส่ข้อความที่ต้องการเข้ารหัส</font>")
            return

        try:
            if encryption_type == "AES":
                if not key:
                    self.result_output.append("<font color='red'>กรุณาใส่คีย์สำหรับ AES</font>")
                    return
                cipher = AES.new(pad(key.encode('utf-8'), AES.block_size), AES.MODE_ECB)
                encrypted = base64.b64encode(cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))).decode('utf-8')
                self.result_output.append(f"<b>ผลลัพธ์ (AES):</b> {encrypted}")
            
            elif encryption_type == "RSA":
                rsa_key = RSA.generate(2048)
                public_key = rsa_key.publickey().export_key()
                private_key = rsa_key.export_key()
                cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
                encrypted = base64.b64encode(cipher.encrypt(message.encode('utf-8'))).decode('utf-8')
                self.result_output.append(f"<b>ผลลัพธ์ (RSA):</b> {encrypted}")
                self.result_output.append(f"<b>Public Key:</b> {public_key.decode('utf-8')}")
                self.result_output.append(f"<b>Private Key:</b> {private_key.decode('utf-8')}")
            
            elif encryption_type == "Blowfish":
                if not key:
                    self.result_output.append("<font color='red'>กรุณาใส่คีย์สำหรับ Blowfish</font>")
                    return
                cipher = Blowfish.new(pad(key.encode('utf-8'), Blowfish.block_size), Blowfish.MODE_ECB)
                encrypted = base64.b64encode(cipher.encrypt(pad(message.encode('utf-8'), Blowfish.block_size))).decode('utf-8')
                self.result_output.append(f"<b>ผลลัพธ์ (Blowfish):</b> {encrypted}")
            
            elif encryption_type == "Fernet":
                fernet_key = Fernet.generate_key()
                cipher = Fernet(fernet_key)
                encrypted = cipher.encrypt(message.encode('utf-8')).decode('utf-8')
                self.result_output.append(f"<b>ผลลัพธ์ (Fernet):</b> {encrypted}")
                self.result_output.append(f"<b>Key:</b> {fernet_key.decode('utf-8')}")
        
        except Exception as e:
            self.result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")

    def decrypt_message(self):
        encrypted_message = self.encryption_message_input.text()
        key = self.encryption_key_input.text()
        encryption_type = self.encryption_combo.currentText()

        if not encrypted_message:
            self.result_output.append("<font color='red'>กรุณาใส่ข้อความที่ต้องการถอดรหัส</font>")
            return

        try:
            if encryption_type == "AES":
                if not key:
                    self.result_output.append("<font color='red'>กรุณาใส่คีย์สำหรับ AES</font>")
                    return
                cipher = AES.new(pad(key.encode('utf-8'), AES.block_size), AES.MODE_ECB)
                decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted_message)), AES.block_size).decode('utf-8')
                self.result_output.append(f"<b>ผลลัพธ์ถอดรหัส (AES):</b> {decrypted}")
            
            elif encryption_type == "Blowfish":
                if not key:
                    self.result_output.append("<font color='red'>กรุณาใส่คีย์สำหรับ Blowfish</font>")
                    return
                cipher = Blowfish.new(pad(key.encode('utf-8'), Blowfish.block_size), Blowfish.MODE_ECB)
                decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted_message)), Blowfish.block_size).decode('utf-8')
                self.result_output.append(f"<b>ผลลัพธ์ถอดรหัส (Blowfish):</b> {decrypted}")
            
            elif encryption_type == "Fernet":
                cipher = Fernet(key.encode('utf-8'))
                decrypted = cipher.decrypt(encrypted_message.encode('utf-8')).decode('utf-8')
                self.result_output.append(f"<b>ผลลัพธ์ถอดรหัส (Fernet):</b> {decrypted}")
        
        except Exception as e:
            self.result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")
