import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox,QScrollArea,QDialog,QDialogButtonBox,QFormLayout, QLineEdit, QComboBox, QPushButton, QLabel, QTextEdit, QHBoxLayout
)
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from Crypto.PublicKey import RSA
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
from PyQt5.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QTextEdit, QPushButton, QLineEdit, QGroupBox, QFrame
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser

class PGPTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.rsa_keys = None



 
    def initUI(self):
        main_layout = QVBoxLayout()

        # กล่อง RSA
        rsa_group = QGroupBox("การเข้ารหัส RSA")
        rsa_layout = QVBoxLayout()

        # ช่องข้อความสำหรับการเข้ารหัส
        self.rsa_message_input = QLineEdit()
        self.rsa_message_input.setPlaceholderText("ข้อความที่ต้องการเข้ารหัสด้วย RSA")

        # Layout หลักที่แบ่งเป็นซ้าย-ขวา
        main_split_layout = QHBoxLayout()

        # ฝั่งซ้าย: พื้นที่แสดงผลลัพธ์
        self.rsa_result_output = QTextEdit()
        self.rsa_result_output.setReadOnly(True)
        self.rsa_result_output.setPlaceholderText("ผลลัพธ์การเข้ารหัส/ถอดรหัส")
        self.rsa_result_output.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                min-width: 300px;
                min-height: 300px;
            }
        """)

        # ฝั่งขวา: กุญแจและลายเซ็น
        keys_layout = QVBoxLayout()

        self.rsa_public_key_input = QTextEdit()
        self.rsa_public_key_input.setPlaceholderText("กุญแจสาธารณะ (Public Key)")

        self.rsa_private_key_input = QTextEdit()
        self.rsa_private_key_input.setPlaceholderText("กุญแจส่วนตัว (Private Key)")

        self.signature_input = QTextEdit()
        self.signature_input.setPlaceholderText("ลายเซ็นดิจิทัล (Digital Signature)")

        # เพิ่ม Labels เพื่อความชัดเจน
        keys_layout.addWidget(QLabel("Public Key"))
        keys_layout.addWidget(self.rsa_public_key_input)
        keys_layout.addWidget(QLabel("Private Key"))
        keys_layout.addWidget(self.rsa_private_key_input)
        keys_layout.addWidget(QLabel("Digital Signature"))
        keys_layout.addWidget(self.signature_input)

        # ใส่ Layout ซ้าย-ขวา
        main_split_layout.addWidget(self.rsa_result_output)  # ฝั่งซ้าย
        main_split_layout.addLayout(keys_layout)  # ฝั่งขวา

        # ปุ่มต่างๆ
        btn_layout = QHBoxLayout()
        self.rsa_generate_keys_button = QPushButton("สร้างคู่กุญแจ")
        self.rsa_generate_keys_button.clicked.connect(self.generate_rsa_keys)
        self.rsa_encrypt_button = QPushButton("เข้ารหัสด้วย RSA")
        self.rsa_decrypt_button = QPushButton("ถอดรหัสด้วย RSA")

        btn_layout.addWidget(self.rsa_generate_keys_button)
        btn_layout.addWidget(self.rsa_encrypt_button)
        btn_layout.addWidget(self.rsa_decrypt_button)
        
        self.show_keys_button = QPushButton("แสดงคีย์ทั้งหมด")
        self.show_keys_button.clicked.connect(self.list_all_keys)
        btn_layout.addWidget(self.show_keys_button)



        # ใส่ทุกอย่างเข้าไปใน Layout หลัก
        rsa_layout.addWidget(QLabel("ข้อความที่ต้องการเข้ารหัส/ถอดรหัส:"))
        rsa_layout.addWidget(self.rsa_message_input)
        rsa_layout.addLayout(main_split_layout)  # เพิ่ม Layout แบ่ง ซ้าย-ขวา
        rsa_layout.addLayout(btn_layout)

        rsa_group.setLayout(rsa_layout)
        main_layout.addWidget(rsa_group)

        self.setLayout(main_layout)








 
    
    

   


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



    def generate_rsa_keys(self):
        # เปิดฟอร์มให้กรอกข้อมูล
        dialog = QDialog(self)
        dialog.setWindowTitle("กรอกข้อมูลเพื่อสร้างคู่กุญแจ RSA")
        
        # สร้างฟอร์มเพื่อกรอกข้อมูล
        form_layout = QFormLayout(dialog)
        
        # ฟิลด์สำหรับอีเมล
        name_email_input = QLineEdit(dialog)
        form_layout.addRow("อีเมล:", name_email_input)
        
        # ฟิลด์สำหรับชื่อ
        name_real_input = QLineEdit(dialog)
        form_layout.addRow("ชื่อเต็ม:", name_real_input)
        
        # ฟิลด์สำหรับ passphrase
        passphrase_input = QLineEdit(dialog)
        passphrase_input.setEchoMode(QLineEdit.Password)  # ซ่อนการพิมพ์
        form_layout.addRow("รหัสผ่านสำหรับกุญแจส่วนตัว:", passphrase_input)
        
        # ฟิลด์สำหรับเลือกวันหมดอายุ
        expire_date_input = QComboBox(dialog)
        expire_date_input.addItems(["1w", "1m", "3m", "1y", "2y"])  # สามารถเพิ่มตัวเลือกอื่นๆ ได้
        form_layout.addRow("ระยะเวลาหมดอายุของกุญแจ:", expire_date_input)
        
        
        
        # สร้างปุ่มตกลงและยกเลิก
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        form_layout.addWidget(button_box)

        # เชื่อมต่อปุ่ม
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # ตรวจสอบว่าผู้ใช้กดตกลง
        if dialog.exec_() == QDialog.Accepted:
            # รับข้อมูลจากฟอร์ม
            name_email = name_email_input.text()
            name_real = name_real_input.text()
            passphrase = passphrase_input.text()
            expire_date = expire_date_input.currentText()
            
            # สร้างอินสแตนซ์ GPG
            gpg = gnupg.GPG()

            # สร้างข้อมูลที่ใช้สำหรับการสร้าง key pair
            input_data = gpg.gen_key_input(
                name_email=name_email,
                name_real=name_real,
                passphrase=passphrase,
                key_type="RSA",
                key_length=2048,
                expire_date=expire_date,
            )

            # สร้าง key โดยใช้ข้อมูลที่กำหนด
            key = gpg.gen_key(input_data)
            fingerprint = key.fingerprint
            print(f"Key created: {fingerprint}")



            if not os.path.exists("key"):
                os.makedirs("key")

            # บันทึกกุญแจส่วนตัวและกุญแจสาธารณะ
            public_key = gpg.export_keys(fingerprint)
            with open("public_key.asc", "w") as pub_file:
                pub_file.write(public_key)
            print("Public key saved as 'public_key.asc'")

            # Export Private Key (ต้องระบุ passphrase)
            private_key = gpg.export_keys(fingerprint, secret=True, passphrase=passphrase)
            with open("private_key.asc", "w") as priv_file:
                priv_file.write(private_key)
            print("Private key saved as 'private_key.asc'")

            # แสดงใน Text Box (UI components)
            self.rsa_private_key_input.setPlainText(private_key)  # ใช้ private_key ที่เป็น str
            self.rsa_public_key_input.setPlainText(public_key)  # ใช้ public_key ที่เป็น str

            # แจ้งผู้ใช้ว่าการสร้างสำเร็จ
            self.rsa_result_output.append("<font color='green'>สร้างคู่กุญแจและบันทึกไฟล์สำเร็จ</font>")









    def list_all_keys(self):
        gpg = gnupg.GPG()  # สร้างอินสแตนซ์ GPG

        # เคลียร์ผลลัพธ์เก่าก่อนแสดงผลใหม่
        self.rsa_result_output.clear()

        # 📌 ดึงทั้ง Public และ Private Keys
        public_keys = gpg.list_keys()
        private_keys = gpg.list_keys(secret=True)

        # 🗂 สร้าง Dictionary สำหรับรวม Public & Private Keys ตาม Fingerprint
        key_map = {}

        for key in public_keys:
            fingerprint = key['fingerprint']
            key_map[fingerprint] = {
                "fingerprint": fingerprint,
                "uids": key['uids'],
                "creation_date": datetime.datetime.utcfromtimestamp(int(key['date'])).strftime('%Y-%m-%d'),
                "expires": key.get('expires'),
                "public_key": key['keyid'],
                "private_key": None  # ตั้งค่าเริ่มต้นเป็น None
            }

        for key in private_keys:
            fingerprint = key['fingerprint']
            if fingerprint in key_map:
                key_map[fingerprint]["private_key"] = key['keyid']
            else:
                key_map[fingerprint] = {
                    "fingerprint": fingerprint,
                    "uids": key['uids'],
                    "creation_date": datetime.datetime.utcfromtimestamp(int(key['date'])).strftime('%Y-%m-%d'),
                    "expires": key.get('expires'),
                    "public_key": None,
                    "private_key": key['keyid']
                }

        # สร้างหน้าต่างป๊อปอัปใหม่
        dialog = QDialog(self)
        dialog.setWindowTitle("🔑 รายการ Public & Private Keys")
        
        # กำหนดขนาดหน้าต่างเป็น 80% ของทั้งความกว้างและความสูงของหน้าหลัก
        main_width = self.width()  # ดึงความกว้างของหน้าต่างหลัก
        main_height = self.height()  # ดึงความสูงของหน้าต่างหลัก
        dialog.setFixedWidth(int(main_width * 0.8))  # ตั้งค่าความกว้างเป็น 80% ของหน้าหลัก
        dialog.setFixedHeight(int(main_height * 0.8))  # ตั้งค่าความสูงเป็น 80% ของหน้าหลัก

        # ใช้ QTextBrowser สำหรับแสดงผลลัพธ์
        text_browser = QTextBrowser(dialog)
        text_browser.setOpenExternalLinks(True)  # อนุญาตให้คลิกลิงก์ได้

        # เคลียร์ผลลัพธ์ก่อนแสดงใหม่
        text_browser.clear()

        # ฟังก์ชันสำหรับอัปเดตการแสดงผลใน QTextBrowser
        def update_text_browser():
            text_browser.clear()
            # ดึงข้อมูล keys ใหม่เพื่อให้แสดงข้อมูลที่อัปเดตล่าสุด
            updated_public_keys = gpg.list_keys()
            updated_private_keys = gpg.list_keys(secret=True)
            
            # สร้าง key_map ใหม่
            key_map.clear()
            
            for key in updated_public_keys:
                fingerprint = key['fingerprint']
                key_map[fingerprint] = {
                    "fingerprint": fingerprint,
                    "uids": key['uids'],
                    "creation_date": datetime.datetime.utcfromtimestamp(int(key['date'])).strftime('%Y-%m-%d'),
                    "expires": key.get('expires'),
                    "public_key": key['keyid'],
                    "private_key": None
                }

            for key in updated_private_keys:
                fingerprint = key['fingerprint']
                if fingerprint in key_map:
                    key_map[fingerprint]["private_key"] = key['keyid']
                else:
                    key_map[fingerprint] = {
                        "fingerprint": fingerprint,
                        "uids": key['uids'],
                        "creation_date": datetime.datetime.utcfromtimestamp(int(key['date'])).strftime('%Y-%m-%d'),
                        "expires": key.get('expires'),
                        "public_key": None,
                        "private_key": key['keyid']
                    }
                    
            if key_map:
                for key_info in key_map.values():
                    # คำนวณวันและเวลาที่เหลือถ้ามีวันหมดอายุ
                    now = datetime.datetime.now()
                    time_remaining = ""
                    expiry_warning = ""
                    
                    if key_info['expires']:
                        # แปลงวันหมดอายุเป็น datetime object
                        expiry_datetime = datetime.datetime.utcfromtimestamp(int(key_info['expires']))
                        expiration_date_str = expiry_datetime.strftime('%Y-%m-%d')
                        
                        # คำนวณเวลาที่เหลือ
                        remaining = expiry_datetime - now
                        
                        if remaining.total_seconds() < 0:
                            # key หมดอายุแล้ว
                            time_remaining = f"<span style='color: red; font-weight: bold;'>หมดอายุแล้ว!</span>"
                            expiry_warning = "<span style='color: red; font-size: 12px;'>⚠️ Key นี้ไม่สามารถใช้งานได้แล้ว</span>"
                        else:
                            # คำนวณวัน ชั่วโมง และนาทีที่เหลือ
                            days_left = remaining.days
                            hours_left = remaining.seconds // 3600
                            minutes_left = (remaining.seconds % 3600) // 60
                            
                            time_remaining = f"เหลือเวลา: {days_left} วัน {hours_left} ชั่วโมง {minutes_left} นาที"
                            
                            # เพิ่มคำเตือนถ้าใกล้หมดอายุ
                            if days_left < 30:
                                expiry_warning = f"<span style='color: orange; font-size: 12px;'>⚠️ Key นี้จะหมดอายุในอีก {days_left} วัน</span>"
                            
                    else:
                        expiration_date_str = "No expiration"

                    key_details = f"""
                        <div style="margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                            <b>Type:</b> {'<span style="color: green;">Public & Private</span>' if key_info['public_key'] and key_info['private_key'] else '<span style="color: blue;">Public</span>' if key_info['public_key'] else '<span style="color: red;">Private</span>'} Key<br>
                            <b>Fingerprint:</b> {key_info['fingerprint']}<br>
                            <b>User:</b> {', '.join(key_info['uids'])}<br>
                            <b>Public Key:</b> {key_info['public_key'] or '-'}<br>
                            <b>Private Key:</b> {key_info['private_key'] or '-'}<br>
                            <b>Created:</b> {key_info['creation_date']}<br>
                            <b>Expires:</b> {expiration_date_str} <br>{time_remaining}<br>
                            {expiry_warning}
                        </div>
                    """
                    text_browser.append(key_details)
            else:
                text_browser.append("<div style='color: red; text-align: center; margin-top: 20px; font-size: 14px;'>❌ No Public or Private Keys found.</div>")
                    
            # อัปเดตปุ่มลบ keys
            refresh_delete_buttons()

        # จริงๆแล้วลบ key ออกจากระบบ
        def delete_key(fingerprint):
            try:
                # แสดงกล่องข้อความยืนยันการลบ
                confirm = QMessageBox.question(
                    dialog,
                    "ยืนยันการลบ",
                    f"คุณแน่ใจหรือไม่ที่จะลบ key นี้?\nFingerprint: {fingerprint}",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if confirm == QMessageBox.Yes:
                    # ดำเนินการลบ key
                    result = gpg.delete_keys(fingerprint, secret=True, expect_passphrase=False)
                    # หากมี public key ด้วย ให้ลบ
                    gpg.delete_keys(fingerprint)
                    
                    QMessageBox.information(dialog, "สำเร็จ", f"ลบ key เรียบร้อยแล้ว")
                    
                    # อัปเดตการแสดงผล
                    update_text_browser()
            except Exception as e:
                QMessageBox.critical(dialog, "เกิดข้อผิดพลาด", f"ไม่สามารถลบ key ได้: {str(e)}")

        # ลบ keys ทั้งหมด
        def delete_all_keys():
            try:
                # แสดงกล่องข้อความยืนยันการลบ
                confirm = QMessageBox.question(
                    dialog,
                    "⚠️ คำเตือน: ยืนยันการลบทั้งหมด",
                    "คุณแน่ใจหรือไม่ที่จะลบ keys ทั้งหมด?\nการกระทำนี้ไม่สามารถเรียกคืนได้!",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if confirm == QMessageBox.Yes:
                    # ลบ private keys ก่อน แล้วค่อยลบ public keys
                    for fingerprint in list(key_map.keys()):
                        if key_map[fingerprint]["private_key"]:
                            gpg.delete_keys(fingerprint, secret=True, expect_passphrase=False)
                        gpg.delete_keys(fingerprint)
                    
                    QMessageBox.information(dialog, "สำเร็จ", "ลบ keys ทั้งหมดเรียบร้อยแล้ว")
                    
                    # อัปเดตการแสดงผล
                    update_text_browser()
            except Exception as e:
                QMessageBox.critical(dialog, "เกิดข้อผิดพลาด", f"ไม่สามารถลบ keys ทั้งหมดได้: {str(e)}")

        # สร้าง Layout หลัก
        main_layout = QVBoxLayout(dialog)
        
        # เพิ่ม QTextBrowser สำหรับแสดงรายการ keys
        main_layout.addWidget(text_browser, 1)
        
        # สร้าง scroll area สำหรับปุ่มลบ keys
        buttons_scroll_area = QScrollArea(dialog)
        buttons_scroll_area.setWidgetResizable(True)
        buttons_container = QWidget()
        buttons_layout = QGridLayout(buttons_container)
        buttons_scroll_area.setWidget(buttons_container)
        buttons_scroll_area.setMaximumHeight(120)  # จำกัดความสูงของพื้นที่ปุ่ม
        
        # ฟังก์ชันสำหรับสร้างปุ่มลบแต่ละ key
        def create_delete_button(fingerprint, user_id):
            # ใช้ชื่อผู้ใช้ถ้ามี หรือใช้ fingerprint บางส่วนถ้าไม่มี
            display_name = user_id.split('<')[0].strip() if user_id else fingerprint[:8]
            
            delete_button = QPushButton(f"🗑️ ลบ: {display_name}", dialog)
            delete_button.setToolTip(f"ลบ key: {fingerprint}")
            delete_button.clicked.connect(lambda: delete_key(fingerprint))
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                    border-radius: 4px;
                    padding: 6px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #f1b0b7;
                    border: 1px solid #ef9a9a;
                }
            """)
            return delete_button
        
        # สร้างปุ่มลบทั้งหมด
        delete_all_button = QPushButton("⚠️ ลบ keys ทั้งหมด", dialog)
        delete_all_button.clicked.connect(delete_all_keys)
        delete_all_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        # ฟังก์ชันสำหรับรีเฟรชปุ่มลบ keys
        def refresh_delete_buttons():
            # ลบปุ่มเก่าทั้งหมด
            while buttons_layout.count():
                item = buttons_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                    
            # เพิ่มปุ่มใหม่
            row, col = 0, 0
            max_cols = 3  # จำนวนคอลัมน์สูงสุด
            
            for fingerprint, key_info in key_map.items():
                # ใช้ uid แรกเป็นชื่อแสดงผล
                user_id = key_info['uids'][0] if key_info['uids'] else None
                delete_button = create_delete_button(fingerprint, user_id)
                
                buttons_layout.addWidget(delete_button, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            
            # เพิ่มปุ่มลบทั้งหมดที่ด้านล่าง
            bottom_layout = QHBoxLayout()
            bottom_layout.addStretch()
            bottom_layout.addWidget(delete_all_button)
            bottom_layout.addStretch()
            
            # เคลียร์ layout เก่าก่อนเพิ่มใหม่
            if main_layout.count() > 2:
                main_layout.takeAt(main_layout.count() - 1)
                
            main_layout.addLayout(bottom_layout)
        
        # เพิ่ม scroll area เข้าไปใน main layout
        main_layout.addWidget(buttons_scroll_area)
        

        
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        main_layout.addLayout(close_layout)
        
        # แสดงข้อมูลเริ่มต้น
        update_text_browser()
        
        # แสดงหน้าต่าง
        dialog.exec_()













        
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
                self.rsa_result_output.append(f"ข้อความที่เข้ารหัส: <font color='blue'>{encoded_ciphertext}</font>")
        except Exception as e:
            self.rsa_result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")

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
            self.rsa_result_output.append(f"ข้อความที่ถอดรหัส: <font color='green'>{plaintext}</font>")
        except Exception as e:
            # แสดงข้อผิดพลาดหากมี
            self.rsa_result_output.append(f"<font color='red'>เกิดข้อผิดพลาดในการถอดรหัส: {str(e)}</font>")
            
        
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
            self.rsa_result_output.append("<font color='purple'>สร้างลายเซ็นดิจิทัลสำเร็จ</font>")
        except Exception as e:
            self.rsa_result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")

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
            self.rsa_result_output.append("<font color='green'>ลายเซ็นถูกต้อง</font>")
        except ValueError:
            self.rsa_result_output.append("<font color='red'>ลายเซ็นไม่ถูกต้อง</font>")
        except Exception as e:
            self.rsa_result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")

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