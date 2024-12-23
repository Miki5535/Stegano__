from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLineEdit, QComboBox, QPushButton, QLabel, QTextEdit,QHBoxLayout
)
from cryptography.fernet import Fernet
from Crypto.Cipher import AES, Blowfish, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
import base64
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
 
import base64
import random
import string

class EncryptionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.rsa_keys = None

    def initUI(self):
        layout = QVBoxLayout()
        
        encrypt_group = QGroupBox("การเข้ารหัส")
        encrypt_layout = QVBoxLayout()
        
        # Dropdown for selecting encryption method
        self.encryption_combo = QComboBox()
        self.encryption_combo.addItems(["AES-ECB", "AES-CBC", "AES-CFB", "AES-OFB", "AES-GCM", "RSA", "Blowfish", "Fernet"])
        
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
        
        # Button for generating random key
        self.generate_key_button = QPushButton("สุ่มคีย์")
        self.generate_key_button.clicked.connect(self.generate_random_key)
        self.generate_key_button.setStyleSheet("background-color: blue; color: white;")

        # Button for encryption
        self.encrypt_button = QPushButton("เข้ารหัส")
        self.encrypt_button.clicked.connect(self.encrypt_message)
        self.encrypt_button.setStyleSheet("background-color: green; color: white;")
        
        # Button for decryption
        self.decrypt_button = QPushButton("ถอดรหัส")
        self.decrypt_button.clicked.connect(self.decrypt_message)
        self.decrypt_button.setStyleSheet("background-color: orange; color: white;")
        
        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.generate_key_button)
        button_layout.addWidget(self.encrypt_button)
        button_layout.addWidget(self.decrypt_button)
        
        # Add widgets to layout
        encrypt_layout.addWidget(QLabel("เลือกวิธีการเข้ารหัส:"))
        encrypt_layout.addWidget(self.encryption_combo)
        encrypt_layout.addWidget(self.encryption_message_input)
        encrypt_layout.addWidget(self.encryption_key_input)
        encrypt_layout.addLayout(button_layout)  # Add the horizontal layout
        encrypt_layout.addWidget(QLabel("ผลลัพธ์:"))
        encrypt_layout.addWidget(self.result_output)
        
        encrypt_group.setLayout(encrypt_layout)
        layout.addWidget(encrypt_group)
        
        self.setLayout(layout)
 
    def generate_random_key(self):
    # กำหนดความยาวของข้อความที่จะสุ่ม
        key_lengths = [16, 24, 32]
        generated_keys = {}

        for length in key_lengths:
            # สุ่มข้อความด้วยตัวอักษรและตัวเลข
            key = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
            generated_keys[length] = key
        
        # แสดงผลลัพธ์
        self.result_output.append("=========================================================")
        self.result_output.append("<b>ข้อความที่สุ่มได้:</b>")
        for length, key in generated_keys.items():
            # print(f"<b>Key {length} Characters:</b> {key}")
            self.result_output.append(f"<b>Key {length} Characters:</b> <span style='color:blue;'>{key}</span>")
        self.result_output.append("=========================================================")

    def encrypt_message(self):
        message = self.encryption_message_input.text()
        key = self.encryption_key_input.text()
        encryption_type = self.encryption_combo.currentText()

        if not message:
            self.result_output.append("<font color='red'>กรุณาใส่ข้อความที่ต้องการเข้ารหัส</font>")
            return

        try:
            if encryption_type.startswith("AES"):
                if not key:
                    self.result_output.append("<font color='red'>กรุณาใส่คีย์สำหรับ AES</font>")
                    return

                # ตรวจสอบความยาวของคีย์ (16, 24, หรือ 32 ไบต์)
                key_length = len(key.encode('utf-8'))
                if key_length not in [16, 24, 32]:
                    self.result_output.append("<font color='red'>คีย์ต้องมีความยาว 16, 24, หรือ 32 ไบต์</font>")
                    return
                
                # ตรวจสอบ IV สำหรับโหมดที่ต้องการ (CBC, CFB, OFB)
                iv = get_random_bytes(16)  # IV ต้องมีขนาด 16 ไบต์
                if encryption_type in ["AES-CBC", "AES-CFB", "AES-OFB"]:
                    if len(iv) != 16:
                        self.result_output.append("<font color='red'>IV ต้องมีความยาว 16 ไบต์</font>")
                        return

                # เริ่มกระบวนการเข้ารหัส
                if encryption_type == "AES-ECB":
                    cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
                    encrypted = base64.b64encode(cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))).decode('utf-8')
                elif encryption_type == "AES-CBC":
                    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
                    encrypted = base64.b64encode(iv + cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))).decode('utf-8')
                elif encryption_type == "AES-CFB":
                    cipher = AES.new(key.encode('utf-8'), AES.MODE_CFB, iv)
                    encrypted = base64.b64encode(iv + cipher.encrypt(message.encode('utf-8'))).decode('utf-8')
                elif encryption_type == "AES-OFB":
                    cipher = AES.new(key.encode('utf-8'), AES.MODE_OFB, iv)
                    encrypted = base64.b64encode(iv + cipher.encrypt(message.encode('utf-8'))).decode('utf-8')
                elif encryption_type == "AES-GCM":
                    cipher = AES.new(key.encode('utf-8'), AES.MODE_GCM)
                    ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
                    encrypted = base64.b64encode(cipher.nonce + ciphertext + tag).decode('utf-8')
                

                # แสดงผลลัพธ์ที่เข้ารหัส
                self.result_output.append(f"<b>ผลลัพธ์ ({encryption_type}):</b> <font color='deeppink'>{encrypted}")

            else:
                # Handle other encryption methods here (RSA, Blowfish, Fernet)
                # self.result_output.append("<font color='red'>ยังไม่รองรับการเข้ารหัสในรูปแบบนี้</font>")
                key_length = len(key.encode('utf-8'))
                if key_length not in [16, 24, 32]:
                    self.result_output.append("<font color='red'>คีย์ต้องมีความยาว 16, 24, หรือ 32 ไบต์</font>")
                    return
                try:
                    if encryption_type == "RSA":
                        if not self.rsa_keys:
                            self.rsa_keys = RSA.generate(2048)
                        public_key = self.rsa_keys.publickey()
                        cipher = PKCS1_OAEP.new(public_key)
                        encrypted = base64.b64encode(cipher.encrypt(message.encode('utf-8'))).decode('utf-8')
                        private_key = self.rsa_keys.export_key().decode('utf-8')
                        public_key_pem = public_key.export_key().decode('utf-8')

                        self.result_output.append(f"<b>ผลลัพธ์ (RSA):</b> <font color='deeppink'>{encrypted}")
                        self.result_output.append(f"<b>Private Key:</b>\n<font color='purple'>{private_key}")
                        self.result_output.append(f"<b>Public Key:</b>\n<font color='brown'>{public_key_pem}")

                    elif encryption_type == "Blowfish":
                        if not key:
                            self.result_output.append("<font color='red'>กรุณาใส่คีย์สำหรับ Blowfish</font>")
                            return
                        cipher = Blowfish.new(pad(key.encode('utf-8'), Blowfish.block_size), Blowfish.MODE_ECB)
                        encrypted = base64.b64encode(cipher.encrypt(pad(message.encode('utf-8'), Blowfish.block_size))).decode('utf-8')
                        self.result_output.append(f"<b>ผลลัพธ์ (Blowfish):</b> <font color='deeppink'>{encrypted}")

                    elif encryption_type == "Fernet":
                        if not key:
                            key = Fernet.generate_key().decode('utf-8')  # สร้างคีย์ใหม่
                            self.encryption_key_input.setText(key)
                        cipher = Fernet(key.encode('utf-8'))
                        encrypted = cipher.encrypt(message.encode('utf-8')).decode('utf-8')
                        self.result_output.append(f"<b>ผลลัพธ์ (Fernet):</b> {encrypted}")
                        self.result_output.append(f"<b>Key:</b> {key}")


                except Exception as e:
                    self.result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")

        except Exception as e:
            self.result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")



    def decrypt_rsa(self, encrypted_data=None):
        if encrypted_data is None:
            encrypted_message = self.encryption_message_input.text()
            try:
                encrypted_data = base64.b64decode(encrypted_message)
            except Exception:
                self.result_output.append("<font color='red'>รูปแบบข้อความเข้ารหัสไม่ถูกต้อง</font>")
                return None

        private_key_text = self.encryption_key_input.text()
        if not private_key_text:
            return None

        try:
            # พยายามนำเข้า Private Key หลายวิธี
            try_methods = [
                lambda: RSA.import_key(private_key_text),
                lambda: RSA.import_key(private_key_text.encode('utf-8')),
                lambda: RSA.import_key(base64.b64decode(private_key_text)),
                lambda: RSA.import_key(base64.b64decode(private_key_text.encode('utf-8')))
            ]

            private_key = None
            for method in try_methods:
                try:
                    private_key = method()
                    break
                except Exception:
                    continue

            if not private_key:
                # self.result_output.append("<font color='red'>ไม่สามารถแปลง Private Key</font>")
                return None

            cipher = PKCS1_OAEP.new(private_key)
            decrypted_text = cipher.decrypt(encrypted_data).decode('utf-8')
            
            # self.result_output.append(f"<font color='green'><b>ผลลัพธ์ถอดรหัส (RSA):</b> {decrypted_text}</font>")
            return decrypted_text

        except Exception as e:
            # เงียบข้อผิดพลาด RSA เพื่อให้ลองโหมดอื่น
            return None

    def decrypt_message(self):
        encrypted_message = self.encryption_message_input.text()
        key = self.encryption_key_input.text()

        if not encrypted_message or not key:
            self.result_output.append("<font color='red'>กรุณาใส่ข้อความและคีย์</font>")
            return

        # เก็บผลลัพธ์เพื่อป้องกันการแสดงซ้ำ
        successful_decryptions = set()

        try:
            encrypted_data = base64.b64decode(encrypted_message)
            key_bytes = key.encode('utf-8')

            # ตรวจสอบและปรับขนาดคีย์
            if len(key_bytes) not in [16, 24, 32]:
                key_bytes = key_bytes.ljust(16, b'\0')

            # โหมดการถอดรหัสที่ต้องการทดสอบ
            modes = {
                "RSA": self.decrypt_rsa,  
                "Blowfish": lambda: self.decrypt_blowfish(encrypted_data, key),  
                "AES-ECB": lambda: unpad(AES.new(key_bytes, AES.MODE_ECB).decrypt(encrypted_data), AES.block_size).decode('utf-8'),
                "AES-CBC": lambda: self.decrypt_aes_mode(encrypted_data, key_bytes, AES.MODE_CBC),
                "AES-CFB": lambda: self.decrypt_aes_mode(encrypted_data, key_bytes, AES.MODE_CFB),
                "AES-OFB": lambda: self.decrypt_aes_mode(encrypted_data, key_bytes, AES.MODE_OFB),
                "AES-GCM": lambda: self.decrypt_aes_gcm(encrypted_data, key_bytes)
            }

            for mode_name, decrypt_func in modes.items():
                try:
                    decrypted = decrypt_func()
                    
                    # กรองข้อความซ้ำ
                    if decrypted and decrypted not in successful_decryptions:
                        successful_decryptions.add(decrypted)
                        self.result_output.append(f"<font color='green'><b>ผลลัพธ์ถอดรหัส ({mode_name}):</b> {decrypted}</font>")
                        
                        # หยุดการทำงานหลังจากถอดรหัสสำเร็จ
                        return

                except Exception as e:
                    print(f"Error in {mode_name}: {e}")
                    continue

            # หากไม่สามารถถอดรหัสได้
            self.result_output.append("<font color='red'>ไม่สามารถถอดรหัสได้</font>")

        except Exception as e:
            self.result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")

    def decrypt_aes_mode(self, encrypted_data, key_bytes, mode):
        # แยก IV (16 ไบต์แรก) และข้อมูลที่เข้ารหัส
        iv, data = encrypted_data[:16], encrypted_data[16:]
        cipher = AES.new(key_bytes, mode, iv)
        
        decrypted_data = cipher.decrypt(data)
        
        # ใช้ unpad เฉพาะโหมด CBC
        if mode == AES.MODE_CBC:
            decrypted_data = unpad(decrypted_data, AES.block_size)
        
        return decrypted_data.decode('utf-8')

    def decrypt_aes_gcm(self, encrypted_data, key_bytes):
        # แยก nonce (16 ไบต์แรก), ciphertext, และ tag
        nonce, ciphertext, tag = encrypted_data[:16], encrypted_data[16:-16], encrypted_data[-16:]
        cipher = AES.new(key_bytes, AES.MODE_GCM, nonce=nonce)
        
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')

    def decrypt_blowfish(self, encrypted_data, key):
        if not key:
            raise ValueError("กรุณาใส่คีย์สำหรับ Blowfish")
        key_padded = pad(key.encode('utf-8'), Blowfish.block_size)
        cipher = Blowfish.new(key_padded, Blowfish.MODE_ECB)
        decrypted_data = cipher.decrypt(encrypted_data)
        return unpad(decrypted_data, Blowfish.block_size).decode('utf-8')


