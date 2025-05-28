import datetime
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QScrollArea, QDialog, QFormLayout,QGridLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QTextEdit, QHBoxLayout, QMessageBox, QTextBrowser
)
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QDialogButtonBox
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import gnupg


class PGPTab(QWidget):
    def __init__(self):
        super().__init__()
        self.gpg_instance = gnupg.GPG()  # สร้าง GPG instance เดียว
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        rsa_group = QGroupBox("การเข้ารหัส RSA")
        rsa_layout = QVBoxLayout()

        self.rsa_message_input = QLineEdit()
        self.rsa_message_input.setPlaceholderText("ข้อความที่ต้องการเข้ารหัสด้วย RSA")

        main_split_layout = QHBoxLayout()
        self.rsa_result_output = QTextEdit()
        self.rsa_result_output.setReadOnly(True)
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

        keys_layout = QVBoxLayout()
        self.rsa_public_key_input = QTextEdit()
        self.rsa_public_key_input.setPlaceholderText("กุญแจสาธารณะ (Public Key)")
        self.rsa_private_key_input = QTextEdit()
        self.rsa_private_key_input.setPlaceholderText("กุญแจส่วนตัว (Private Key)")
        self.signature_input = QTextEdit()
        self.signature_input.setPlaceholderText("ลายเซ็นดิจิทัล (Digital Signature)")

        keys_layout.addWidget(QLabel("Public Key"))
        keys_layout.addWidget(self.rsa_public_key_input)
        keys_layout.addWidget(QLabel("Private Key"))
        keys_layout.addWidget(self.rsa_private_key_input)
        keys_layout.addWidget(QLabel("Digital Signature"))
        keys_layout.addWidget(self.signature_input)

        main_split_layout.addWidget(self.rsa_result_output)
        main_split_layout.addLayout(keys_layout)

        btn_layout = QHBoxLayout()
        self.rsa_generate_keys_button = QPushButton("สร้างคู่กุญแจ")
        self.rsa_generate_keys_button.clicked.connect(self.generate_rsa_keys)
        self.rsa_encrypt_button = QPushButton("เข้ารหัสด้วย RSA")
        self.rsa_decrypt_button = QPushButton("ถอดรหัสด้วย RSA")
        self.show_keys_button = QPushButton("แสดงคีย์ทั้งหมด")
        self.show_keys_button.clicked.connect(self.list_all_keys)

        btn_layout.addWidget(self.rsa_generate_keys_button)
        btn_layout.addWidget(self.rsa_encrypt_button)
        btn_layout.addWidget(self.rsa_decrypt_button)
        btn_layout.addWidget(self.show_keys_button)

        rsa_layout.addWidget(QLabel("ข้อความที่ต้องการเข้ารหัส/ถอดรหัส:"))
        rsa_layout.addWidget(self.rsa_message_input)
        rsa_layout.addLayout(main_split_layout)
        rsa_layout.addLayout(btn_layout)
        rsa_group.setLayout(rsa_layout)
        main_layout.addWidget(rsa_group)
        self.setLayout(main_layout)

    def generate_rsa_keys(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("กรอกข้อมูลเพื่อสร้างคู่กุญแจ RSA")
        form_layout = QFormLayout(dialog)

        name_email_input = QLineEdit(dialog)
        form_layout.addRow("อีเมล:", name_email_input)

        name_real_input = QLineEdit(dialog)
        form_layout.addRow("ชื่อเต็ม:", name_real_input)

        passphrase_input = QLineEdit(dialog)
        passphrase_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("รหัสผ่านสำหรับกุญแจส่วนตัว:", passphrase_input)

        expire_date_input = QComboBox(dialog)
        expire_date_input.addItems(["1w", "1m", "3m", "1y", "2y"])
        form_layout.addRow("ระยะเวลาหมดอายุของกุญแจ:", expire_date_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        form_layout.addWidget(button_box)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            name_email = name_email_input.text()
            name_real = name_real_input.text()
            passphrase = passphrase_input.text()
            expire_date = expire_date_input.currentText()

            try:
                input_data = self.gpg_instance.gen_key_input(
                    name_email=name_email,
                    name_real=name_real,
                    passphrase=passphrase,
                    key_type="RSA",
                    key_length=2048,
                    expire_date=expire_date,
                )

                key = self.gpg_instance.gen_key(input_data)
                fingerprint = key.fingerprint
                print(f"Key created: {fingerprint}")

                key_dir = "key"
                if not os.path.exists(key_dir):
                    os.makedirs(key_dir)

                public_key = self.gpg_instance.export_keys(fingerprint)
                private_key = self.gpg_instance.export_keys(fingerprint, secret=True, passphrase=passphrase)

                with open(os.path.join(key_dir, "public_key.asc"), "w") as pub_file:
                    pub_file.write(public_key)
                with open(os.path.join(key_dir, "private_key.asc"), "w") as priv_file:
                    priv_file.write(private_key)

                self.rsa_public_key_input.setPlainText(public_key)
                self.rsa_private_key_input.setPlainText(private_key)
                self.rsa_result_output.append("<font color='green'>สร้างคู่กุญแจและบันทึกไฟล์สำเร็จ</font>")

            except Exception as e:
                self.rsa_result_output.append(f"<font color='red'>เกิดข้อผิดพลาด: {str(e)}</font>")












    def list_all_keys(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("🔑 รายการ Public & Private Keys")
        main_width = self.width()
        main_height = self.height()
        dialog.setFixedWidth(int(main_width * 0.8))
        dialog.setFixedHeight(int(main_height * 0.8))

        text_browser = QTextBrowser(dialog)
        text_browser.setOpenExternalLinks(True)

        gpg = gnupg.GPG()  # ใช้ GPG instance เดียว

        def update_text_browser():
            text_browser.clear()
            public_keys = gpg.list_keys()
            private_keys = gpg.list_keys(secret=True)

            key_map = {}
            for key in public_keys:
                fp = key['fingerprint']
                key_map[fp] = {
                    "uids": key['uids'],
                    "date": key['date'],
                    "expires": key.get('expires'),
                    "public": True,
                    "private": False
                }
            for key in private_keys:
                fp = key['fingerprint']
                if fp in key_map:
                    key_map[fp]['private'] = True
                else:
                    key_map[fp] = {
                        "uids": key['uids'],
                        "date": key['date'],
                        "expires": key.get('expires'),
                        "public": False,
                        "private": True
                    }

            if not key_map:
                text_browser.append("<p style='text-align:center;color:red;'>❌ ไม่มีคีย์</p>")
                return

            for fp, info in key_map.items():
                uids = ', '.join(info["uids"])
                created = datetime.datetime.utcfromtimestamp(int(info["date"])).strftime('%Y-%m-%d')
                expires = info["expires"]
                exp_str = ""
                if expires:
                    exp_dt = datetime.datetime.utcfromtimestamp(int(expires)).strftime('%Y-%m-%d')
                    now = datetime.datetime.now()
                    delta = datetime.datetime.utcfromtimestamp(int(expires)) - now
                    days_left = delta.days
                    if days_left < 0:
                        exp_str = "<span style='color:red;font-weight:bold;'>หมดอายุแล้ว</span>"
                    else:
                        exp_str = f"{exp_dt} (เหลือ {days_left} วัน)"
                else:
                    exp_str = "ไม่มีวันหมดอายุ"

                key_html = f"""
                <div style="margin-bottom: 10px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                    <b>Fingerprint:</b> {fp}<br>
                    <b>User:</b> {uids}<br>
                    <b>Created:</b> {created}<br>
                    <b>Expires:</b> {exp_str}<br>
                    <b>Type:</b> {('Public & Private' if info['public'] and info['private'] else 'Public' if info['public'] else 'Private')}
                </div>
                """
                text_browser.append(key_html)

        def delete_key(fingerprint):
            confirm = QMessageBox.question(
                dialog,
                "ยืนยันการลบ",
                f"คุณแน่ใจหรือไม่ที่จะลบ Key นี้?\nFingerprint: {fingerprint}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                try:
                    result = gpg.delete_keys(fingerprint, secret=True, expect_passphrase=False)
                    print(f"Delete result: {result}")
                    QMessageBox.information(dialog, "สำเร็จ", f"ลบ Key เรียบร้อยแล้ว: {fingerprint}")
                    update_text_browser()
                except Exception as e:
                    QMessageBox.critical(dialog, "เกิดข้อผิดพลาด", f"ไม่สามารถลบ Key ได้\n{str(e)}")

        def delete_all_keys():
            confirm = QMessageBox.question(
                dialog,
                "⚠️ ยืนยันการลบทั้งหมด",
                "คุณแน่ใจหรือไม่ที่จะลบ keys ทั้งหมด? การกระทำนี้ไม่สามารถย้อนกลับได้!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                try:
                    public_fingerprints = [key['fingerprint'] for key in gpg.list_keys()]
                    private_fingerprints = [key['fingerprint'] for key in gpg.list_keys(secret=True)]
                    all_fingerprints = set(public_fingerprints + private_fingerprints)

                    for fp in all_fingerprints:
                        gpg.delete_keys(fp, secret=True, expect_passphrase=False)
                        gpg.delete_keys(fp)

                    QMessageBox.information(dialog, "สำเร็จ", "ลบ keys ทั้งหมดเรียบร้อยแล้ว")
                    update_text_browser()
                except Exception as e:
                    QMessageBox.critical(dialog, "เกิดข้อผิดพลาด", f"ไม่สามารถลบ keys ทั้งหมดได้\n{str(e)}")

        def refresh_delete_buttons():
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            delete_all_btn = QPushButton("⚠️ ลบ keys ทั้งหมด")
            delete_all_btn.setStyleSheet("""
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
            delete_all_btn.clicked.connect(delete_all_keys)

            button_layout.addWidget(delete_all_btn)
            button_layout.addStretch()

            main_layout.addLayout(button_layout)

        main_layout = QVBoxLayout(dialog)
        main_layout.addWidget(text_browser)

        update_text_browser()
        refresh_delete_buttons()
        dialog.exec_()         
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                