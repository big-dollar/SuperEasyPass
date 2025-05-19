from PyQt5.QtWidgets import QMenu, QAction, QApplication
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPalette, QColor
from database import PasswordDatabase
import pyautogui
import time

class PasswordMenu(QMenu):
    def __init__(self, position, passwords):
        super().__init__()
        self.position = position
        self.passwords = passwords
        
        # 设置窗口标志和样式
        self.setup_window()
        # 初始化菜单
        self.init_menu()
    
    def init_menu(self):
        # 按分组整理密码
        password_groups = {}
        for id, name, username, password, group_name in self.passwords:
            if group_name not in password_groups:
                password_groups[group_name] = []
            password_groups[group_name].append((id, name, username, password))
        
        # 为每个分组创建子菜单
        for group_name, group_passwords in password_groups.items():
            group_menu = QMenu(group_name, self)
            
            # 为每个密码创建子菜单
            for id, name, username, password in group_passwords:
                password_menu = QMenu(name, group_menu)
                
                oneclick_action = QAction("OneClick", password_menu)
                username_action = QAction("Username", password_menu)
                password_action = QAction("Password", password_menu)
                
                oneclick_action.triggered.connect(
                    lambda checked, u=username, p=password: self.oneclick_action(u, p))
                username_action.triggered.connect(
                    lambda checked, u=username: self.username_action(u))
                password_action.triggered.connect(
                    lambda checked, p=password: self.password_action(p))
                
                password_menu.addAction(oneclick_action)
                password_menu.addAction(username_action)
                password_menu.addAction(password_action)
                
                group_menu.addMenu(password_menu)
            
            self.addMenu(group_menu)
    
    def setup_window(self):
        # 设置窗口标志
        self.setWindowFlags(
            Qt.Popup |
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint
        )
        
        # 设置样式表
        self.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #e1e4e8;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
                margin: 2px 4px;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
                color: #2196f3;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e1e4e8;
                margin: 4px 8px;
            }
            /* 子菜单样式 */
            QMenu QMenu {
                background-color: #ffffff;
                border: 1px solid #e1e4e8;
                border-radius: 8px;
            }
            /* 斑马纹效果 */
            QMenu QMenu::item:!selected:nth-child(odd) {
                background-color: #f8f9fa;
            }
            /* 箭头样式 */
            QMenu::right-arrow {
                width: 12px;
                height: 12px;
                margin-right: 4px;
            }
        """)
        
        # 设置属性
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WA_DeleteOnClose)
    
    def oneclick_action(self, username, password):
        # 关闭菜单
        self.close()
        
        # 等待一小段时间，让菜单完全关闭
        time.sleep(0.1)
        
        # 模拟键盘输入：用户名 -> Tab -> 密码 -> Enter
        pyautogui.write(username)
        pyautogui.press('tab')
        pyautogui.write(password)
        pyautogui.press('enter')
    
    def username_action(self, username):
        self.close()
        time.sleep(0.1)
        pyautogui.write(username)
    
    def password_action(self, password):
        self.close()
        time.sleep(0.1)
        pyautogui.write(password)