from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLineEdit, QComboBox, QPushButton, QLabel, QTextEdit, QHBoxLayout
)
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import gnupg

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
    load_pem_private_key,
    load_pem_public_key
)

import base64
import os
import random
import string


class EncryptionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.rsa_keys = None


    def initUI(self):
        layout = QHBoxLayout()

        # AES Encryption Group
        aes_group = QGroupBox("การเข้ารหัส AES")
        aes_layout = QVBoxLayout()

        # Dropdown for AES methods
        self.aes_combo = QComboBox()
        self.aes_combo.addItems(["AES-ECB", "AES-CBC", "AES-CFB", "AES-OFB", "AES-GCM"])

        # Inputs for AES message and key
        self.aes_message_input = QLineEdit()
        self.aes_message_input.setPlaceholderText("ข้อความที่ต้องการเข้ารหัสด้วย AES")
        self.aes_message_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")

        self.aes_key_input = QLineEdit()
        self.aes_key_input.setPlaceholderText("คีย์สำหรับเข้ารหัส AES")
        self.aes_key_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")

        # Output for AES
        self.aes_result_output = QTextEdit()
        self.aes_result_output.setReadOnly(True)
        self.aes_result_output.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
        """)

        # AES Buttons
        self.aes_random_key_button = QPushButton("สุ่ม Key AES")
        self.aes_random_key_button.clicked.connect(self.generate_random_key)
        self.aes_random_key_button.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; border-radius: 4px;")

        self.aes_encrypt_button = QPushButton("เข้ารหัสด้วย AES")
        self.aes_encrypt_button.clicked.connect(self.encrypt_aes)
        self.aes_encrypt_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 4px;")

        self.aes_decrypt_button = QPushButton("ถอดรหัสด้วย AES")
        self.aes_decrypt_button.clicked.connect(self.decrypt_aes)
        self.aes_decrypt_button.setStyleSheet("background-color: #FF9800; color: white; padding: 8px; border-radius: 4px;")

        # Add AES widgets to layout
        aes_layout.addWidget(QLabel("เลือกโหมด AES:"))
        aes_layout.addWidget(self.aes_combo)
        aes_layout.addWidget(self.aes_message_input)
        aes_layout.addWidget(self.aes_key_input)
        aes_layout.addWidget(self.aes_random_key_button)
        aes_layout.addWidget(self.aes_encrypt_button)
        aes_layout.addWidget(self.aes_decrypt_button)
        aes_layout.addWidget(QLabel("ผลลัพธ์:"))
        aes_layout.addWidget(self.aes_result_output)
        aes_group.setLayout(aes_layout)

        # RSA Encryption Group
        rsa_group = QGroupBox("การเข้ารหัส RSA")
        rsa_layout = QVBoxLayout()

        # Inputs for RSA message and keys
        self.rsa_message_input = QLineEdit()
        self.rsa_message_input.setPlaceholderText("ข้อความที่ต้องการเข้ารหัสด้วย RSA")
        self.rsa_message_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")

        self.rsa_public_key_input = QTextEdit()
        self.rsa_public_key_input.setPlaceholderText("กุญแจสาธารณะ (Public Key)")
        self.rsa_public_key_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")

        self.rsa_private_key_input = QTextEdit()
        self.rsa_private_key_input.setPlaceholderText("กุญแจส่วนตัว (Private Key)")
        self.rsa_private_key_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")


        self.signature_input = QTextEdit()
        self.signature_input.setPlaceholderText("ลายเซ็นดิจิทัล (Digital Signature)")
        self.signature_input.setStyleSheet("padding: 8px; border: 1px solid #ccc; border-radius: 4px;")
        
        # Output for RSA
        self.rsa_result_output = QTextEdit()
        self.rsa_result_output.setReadOnly(True)
        self.rsa_result_output.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
            }
        """)

        # RSA Buttons
        self.rsa_generate_keys_button = QPushButton("สร้างคู่กุญแจ")
        self.rsa_generate_keys_button.clicked.connect(self.generate_rsa_keys)
        self.rsa_generate_keys_button.setStyleSheet("background-color: #2196F3; color: white; padding: 8px; border-radius: 4px;")

       
        # RSA Buttons
        rsa_encrypt_and_decrypt_button = QHBoxLayout()
        self.rsa_encrypt_button = QPushButton("เข้ารหัสด้วย RSA")
        self.rsa_encrypt_button.clicked.connect(self.encrypt_rsa)
        self.rsa_encrypt_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; border-radius: 4px;")

        self.rsa_decrypt_button = QPushButton("ถอดรหัสด้วย RSA")
        self.rsa_decrypt_button.clicked.connect(self.decrypt_rsa)
        self.rsa_decrypt_button.setStyleSheet("background-color: #FF9800; color: white; padding: 8px; border-radius: 4px;")

        # RSA Sign and Verify Buttons
        rsa_sign_and_verify_layout = QHBoxLayout()

        self.rsa_sign_button = QPushButton("สร้างลายเซ็นดิจิทัล")
        self.rsa_sign_button.clicked.connect(self.sign_message_rsa)
        self.rsa_sign_button.setStyleSheet("background-color: #673AB7; color: white; padding: 8px; border-radius: 4px;")

        self.rsa_verify_button = QPushButton("ตรวจสอบลายเซ็น")
        self.rsa_verify_button.clicked.connect(self.verify_signature_rsa)
        self.rsa_verify_button.setStyleSheet("background-color: #009688; color: white; padding: 8px; border-radius: 4px;")

        self.output_folder_button = QPushButton("เปิดโฟลเดอร์ Key")
        self.output_folder_button.clicked.connect(self.open_output_folder)
        self.output_folder_button.setStyleSheet("background-color: back; color: white;")



        # Add RSA widgets to layout
        rsa_layout.addWidget(QLabel("ข้อความที่ต้องการเข้ารหัส/ถอดรหัส:"))
        rsa_layout.addWidget(self.rsa_message_input)
        rsa_layout.addWidget(QLabel("กุญแจสาธารณะ (Public Key):"))
        rsa_layout.addWidget(self.rsa_public_key_input)
        rsa_layout.addWidget(QLabel("กุญแจส่วนตัว (Private Key):"))
        rsa_layout.addWidget(self.rsa_private_key_input)
        rsa_layout.addWidget(QLabel("ลายเซ็นดิจิทัล (Digital Signature):"))
        rsa_layout.addWidget(self.signature_input)
        
 
        
        rsa_encrypt_and_decrypt_button.addWidget(self.rsa_generate_keys_button)
        rsa_encrypt_and_decrypt_button.addWidget(self.rsa_encrypt_button)
        rsa_encrypt_and_decrypt_button.addWidget(self.rsa_decrypt_button)

        # Wrap the QHBoxLayout inside a QWidget
        rsa_button_widget = QWidget()
        rsa_button_widget.setLayout(rsa_encrypt_and_decrypt_button)

        # Add the QWidget to the layout
        rsa_layout.addWidget(rsa_button_widget)
        
        
         # Output Folder button


        
        rsa_sign_and_verify_layout.addWidget(self.rsa_sign_button)
        rsa_sign_and_verify_layout.addWidget(self.rsa_verify_button)
        rsa_sign_and_verify_layout.addWidget(self.output_folder_button)

        # Wrap the QHBoxLayout inside a QWidget
        rsa_sign_and_verify_widget = QWidget()
        rsa_sign_and_verify_widget.setLayout(rsa_sign_and_verify_layout)

        # Add the QWidget to the layout
        rsa_layout.addWidget(rsa_sign_and_verify_widget)
        
        # rsa_layout.addWidget(self.rsa_sign_button)
        # rsa_layout.addWidget(self.rsa_verify_button)
        # rsa_layout.addWidget(QLabel("ผลลัพธ์:"))
        # rsa_layout.addWidget(self.rsa_result_output)
        rsa_group.setLayout(rsa_layout)

        layout.addWidget(rsa_group)
        self.setLayout(layout)
        

        # Add groups to main layout side by side
        layout.addWidget(aes_group)
        layout.addWidget(rsa_group)

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
        self.aes_result_output.append("=========================================================")
        self.aes_result_output.append("<b>ข้อความที่สุ่มได้:</b>")
        for length, key in generated_keys.items():
            # print(f"<b>Key {length} Characters:</b> {key}")
            self.aes_result_output.append(f"<b>Key {length} Characters:</b> <span style='color:blue;'>{key}</span>")
        self.aes_result_output.append("=========================================================")

    def encrypt_aes(self):
        message = self.aes_message_input.text()
        key = self.aes_key_input.text()
        encryption_type = self.aes_combo.currentText()

        if not message:
            self.aes_result_output.append("<font color='red'>กรุณาใส่ข้อความที่ต้องการเข้ารหัส</font>")
            return

        try:
            if encryption_type.startswith("AES"):
                if not key:
                    self.aes_result_output.append("<font color='red'>กรุณาใส่คีย์สำหรับ AES</font>")
                    return

                # ตรวจสอบความยาวของคีย์ (16, 24, หรือ 32 ไบต์)
                key_length = len(key.encode('utf-8'))
                if key_length not in [16, 24, 32]:
                    self.aes_result_output.append("<font color='red'>คีย์ต้องมีความยาว 16, 24, หรือ 32 ไบต์</font>")
                    return
                
                # ตรวจสอบ IV สำหรับโหมดที่ต้องการ (CBC, CFB, OFB)
                iv = get_random_bytes(16)  # IV ต้องมีขนาด 16 ไบต์
                if encryption_type in ["AES-CBC", "AES-CFB", "AES-OFB"]:
                    if len(iv) != 16:
                        self.aes_result_output.append("<font color='red'>IV ต้องมีความยาว 16 ไบต์</font>")
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
                self.aes_result_output.append(f"<b>ผลลัพธ์ ({encryption_type}):</b> <font color='deeppink'>{encrypted}")
        except Exception as e:
            self.aes_result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")

    def decrypt_aes(self):
        encrypted_message = self.aes_message_input.text()
        key = self.aes_key_input.text()

        if not encrypted_message or not key:
            self.aes_result_output.append("<font color='red'>กรุณาใส่ข้อความและคีย์</font>")
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
                        self.aes_result_output.append(f"<font color='green'><b>ผลลัพธ์ถอดรหัส ({mode_name}):</b> {decrypted}</font>")
                        
                        # หยุดการทำงานหลังจากถอดรหัสสำเร็จ
                        return

                except Exception as e:
                    # print(f"Error in {mode_name}: {e}")
                    continue

            # หากไม่สามารถถอดรหัสได้
            self.aes_result_output.append("<font color='red'>ไม่สามารถถอดรหัสได้</font>")

        except Exception as e:
            self.aes_result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")

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


    def open_output_folder(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        # เข้าถึงโฟลเดอร์ photoexample/output
        parent_directory = os.path.dirname(current_directory)  
        output_path = os.path.join(parent_directory, "key")
        
        # ตรวจสอบว่ามีโฟลเดอร์อยู่หรือไม่ ถ้าไม่มีก็สร้างขึ้น
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        # เปิดโฟลเดอร์ด้วย QDesktopServices
        QDesktopServices.openUrl(QUrl.fromLocalFile(output_path))

    # RSA Functions
    def generate_rsa_keys(self):
        # สร้างอินสแตนซ์ GPG
        gpg = gnupg.GPG()

        # สร้างข้อมูลที่ใช้สำหรับการสร้าง key pair
        input_data = gpg.gen_key_input(
            name_email="your_email@example.com",
            name_real="Your Name",
            passphrase="your_passphrase",  # ตั้งรหัสผ่านสำหรับ private key
            key_type="RSA",
            key_length=2048,
            expire_date="1y",  # ระบุว่า Key จะหมดอายุใน 1 ปี (สามารถตั้งค่าเช่น '1w', '1m', '2y' ได้)
        )

        # สร้าง key โดยใช้ข้อมูลที่กำหนด
        key = gpg.gen_key(input_data)
        fingerprint = key.fingerprint
        print(f"Key created: {fingerprint}")

        # กำหนดโฟลเดอร์สำหรับเก็บกุญแจ
        key_folder = "key"  # เปลี่ยนเป็นโฟลเดอร์ที่ต้องการบันทึก

        if not os.path.exists(key_folder):
            os.makedirs(key_folder)

        # บันทึกกุญแจส่วนตัวและกุญแจสาธารณะ
        public_key = gpg.export_keys(fingerprint)
        with open("public_key.asc", "w") as pub_file:
            pub_file.write(public_key)
        print("Public key saved as 'public_key.asc'")

        # Export Private Key (ต้องระบุ passphrase)
        private_key = gpg.export_keys(fingerprint, secret=True, passphrase="your_passphrase")
        with open("private_key.asc", "w") as priv_file:
            priv_file.write(private_key)
        print("Private key saved as 'private_key.asc'")



        # แสดงใน Text Box (UI components)
        self.rsa_private_key_input.setPlainText(private_key)  # ใช้ private_key ที่เป็น str
        self.rsa_public_key_input.setPlainText(public_key)  # ใช้ public_key ที่เป็น str

        # แจ้งผู้ใช้ว่าการสร้างสำเร็จ
        self.aes_result_output.append("<font color='green'>สร้างคู่กุญแจและบันทึกไฟล์สำเร็จ</font>")

        
    def encrypt_rsa(self):
        public_key = self.rsa_public_key_input.toPlainText()
        message = self.rsa_message_input.text()
        try:
                # แปลง public key จากข้อความเป็น RSA object
                from Crypto.PublicKey import RSA
                from Crypto.Cipher import PKCS1_OAEP
                
                public_key = RSA.import_key(public_key)
                cipher = PKCS1_OAEP.new(public_key)
                ciphertext = cipher.encrypt(message.encode('utf-8'))
                
                # แปลง ciphertext เป็น base64 เพื่อให้ง่ายต่อการแสดงผล
                import base64
                encoded_ciphertext = base64.b64encode(ciphertext).decode('utf-8')
                
                # แสดงผล
                self.aes_result_output.append(f"ข้อความที่เข้ารหัส: <font color='blue'>{encoded_ciphertext}</font>")
        except Exception as e:
            self.aes_result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")

    def decrypt_rsa(self):
        private_key = self.rsa_private_key_input.toPlainText()
        ciphertext = self.rsa_message_input.text()
        
        try:
            # แปลงข้อความคีย์ส่วนตัวเป็น RSA Key Object
            from Crypto.PublicKey import RSA
            from Crypto.Cipher import PKCS1_OAEP
            import base64

            # แปลงข้อความ ciphertext เป็น byte
            ciphertext_bytes = base64.b64decode(ciphertext.encode('utf-8'))

            # นำเข้า Private Key
            private_key = RSA.import_key(private_key)

            # สร้าง RSA Cipher สำหรับการถอดรหัส
            cipher = PKCS1_OAEP.new(private_key)

            # ถอดรหัสข้อความ
            plaintext = cipher.decrypt(ciphertext_bytes).decode('utf-8')

            # แสดงผลข้อความที่ถอดรหัส
            self.aes_result_output.append(f"ข้อความที่ถอดรหัส: <font color='green'>{plaintext}</font>")
        except Exception as e:
            # แสดงข้อผิดพลาดหากมี
            self.aes_result_output.append(f"<font color='red'>เกิดข้อผิดพลาดในการถอดรหัส: {str(e)}</font>")
            
        
    def sign_message_rsa(self):
        private_key = self.rsa_private_key_input.toPlainText()
        message = self.rsa_message_input.text()
        try:
            # แปลง private key จาก string เป็น RSA object
            private_key = RSA.import_key(private_key)

            # แปลงข้อความเป็น hash
            message_hash = SHA256.new(message.encode('utf-8'))

            # สร้างลายเซ็น
            signature = pkcs1_15.new(private_key).sign(message_hash)

            # แปลงลายเซ็นเป็น base64
            signature_base64 = base64.b64encode(signature).decode('utf-8')
            
            # บันทึกลายเซ็นในรูปแบบ base64
            self.signature_input.setPlainText(signature_base64)

            # แสดงสถานะ
            self.aes_result_output.append("<font color='purple'>สร้างลายเซ็นดิจิทัลสำเร็จ</font>")
        except Exception as e:
            self.aes_result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")

    def verify_signature_rsa(self):
        try:
            public_key_str = self.rsa_public_key_input.toPlainText()
            message = self.rsa_message_input.text()
            signature_base64 = self.signature_input.toPlainText()

            # แปลง public key เป็น RSA object
            public_key = RSA.import_key(public_key_str)
            
            # แปลงลายเซ็นจาก base64 กลับเป็น bytes
            signature = base64.b64decode(signature_base64)

            # สร้าง hash ของข้อความ
            message_hash = SHA256.new(message.encode('utf-8'))

            # ตรวจสอบลายเซ็น
            pkcs1_15.new(public_key).verify(message_hash, signature)
            self.aes_result_output.append("<font color='green'>ลายเซ็นถูกต้อง</font>")
        except ValueError:
            self.aes_result_output.append("<font color='red'>ลายเซ็นไม่ถูกต้อง</font>")
        except Exception as e:
            self.aes_result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")

# บันทึก Private Key ในรูปแบบ ASCII Armored
def save_private_key_asc(private_key, filename):
    pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption()
    )
    with open(filename, 'w') as key_file:
        key_file.write(pem.decode('utf-8'))  # เขียนเป็นข้อความ ASCII

# บันทึก Public Key ในรูปแบบ ASCII Armored
def save_public_key_asc(public_key, filename):
    pem = public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo
    )
    with open(filename, 'w') as key_file:
        key_file.write(pem.decode('utf-8'))  # เขียนเป็นข้อความ ASCII

# โหลด Private Key
def load_private_key(filename):
    with open(filename, 'rb') as key_file:
        pem_data = key_file.read()
    return load_pem_private_key(pem_data, password=None)

# โหลด Public Key
def load_public_key(filename):
    with open(filename, 'rb') as key_file:
        pem_data = key_file.read()
    return load_pem_public_key(pem_data)

# 1. สร้างคู่ Public และ Private Key
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key

# 2. ใช้ Public Key เข้ารหัสข้อความ
# def encrypt_message(public_key, message):
#     ciphertext = public_key.encrypt(
#         message.encode('utf-8'),
#         padding.OAEP(
#             mgf=padding.MGF1(algorithm=hashes.SHA256()),
#             algorithm=hashes.SHA256(),
#             label=None
#         )
#     )
#     return ciphertext

def encrypt_message(public_key, message):
    ciphertext = public_key.encrypt(
        message.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(ciphertext).decode('utf-8')  # เข้ารหัสข้อความเป็น Base64


# 3. ใช้ Private Key ถอดรหัสข้อความ
def decrypt_message(private_key, ciphertext):
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext.decode('utf-8')

# 4. ใช้ Private Key สร้างลายเซ็นดิจิทัล
def sign_message(private_key, message):
    signature = private_key.sign(
        message.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

# 5. ใช้ Public Key เพื่อตรวจสอบลายเซ็น
def verify_signature(public_key, message, signature):
    try:
        public_key.verify(
            signature,
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        return False