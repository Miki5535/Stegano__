import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                          
                            QTabWidget)
from PyQt5.QtGui import  QIcon
import tabs.image_tab as image_tab
import tabs.audio_tab as audio_tab
import tabs.file_info_tab as info_tab
import tabs.encryption_tab as encryption_tab
import tabs.file_and_FILE as file_and_FILE





class EnhancedSteganographyApp(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Steganography and Encryption App")
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowIcon(QIcon("myicon.ico"))
        self.setFixedSize(1000, 800) 
        self.current_file_path = None
        self.setup_styles()  
        self.initUI()
        
        
        
    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Segoe UI', Arial;
            }
            QGroupBox {
                border: 2px solid #2196F3;
                border-radius: 8px;
                margin-top: 1em;
                padding: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                color: #2196F3;
                font-weight: bold;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                min-height: 30px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 2px solid #BBDEFB;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QLabel {
                color: #424242;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #BBDEFB;
                background: white;
            }
            QTabBar::tab {
                background: #BBDEFB;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #2196F3;
                color: white;
            }
        """)


           


    def initUI(self):
        main_layout = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        self.image_tab = image_tab.ImageTab()
        tabs.addTab(self.image_tab, "การซ่อนข้อความในรูปภาพ")
        
        self.audio_tab = audio_tab.AudioTab()
        tabs.addTab(self.audio_tab, "การซ่อนข้อความในไฟล์เสียง")
        
        self.info_tab = info_tab.FileInfoTab()
        tabs.addTab(self.info_tab, "การซ่อนใน Meta Tag")
        
        self.file_tab = file_and_FILE.FileAndFileTab()
        tabs.addTab(self.file_tab, "ไฟล์ต่อไฟล์")
        
        self.encryption_tab = encryption_tab.EncryptionTab()
        tabs.addTab(self.encryption_tab, "การเข้ารหัส")

        
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EnhancedSteganographyApp()
    window.show()
    sys.exit(app.exec_())