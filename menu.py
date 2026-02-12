from PyQt5.QtWidgets import QMenu, QAction, QApplication
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPalette, QColor, QIcon, QPixmap, QPainter, QFont
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
    
    def create_color_icon(self, color_str, shape='circle'):
        """创建简单的颜色图标"""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        color = QColor(color_str)
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        
        if shape == 'circle':
            painter.drawEllipse(2, 2, 12, 12)
        else:
            painter.drawRect(2, 2, 12, 12)
            
        painter.end()
        return QIcon(pixmap)

    def init_menu(self):
        # 按分组整理密码
        password_groups = {}
        # get_all_passwords returns (id, name, username, password, group_name, note)
        for id, name, username, password, group_name, _ in self.passwords:
            if group_name not in password_groups:
                password_groups[group_name] = []
            password_groups[group_name].append((id, name, username, password))
        
        # 定义颜色
        COLOR_GROUP = "#0366d6"  # 蓝色
        COLOR_ITEM = "#2ea44f"   # 绿色
        COLOR_ONECLICK = "#6f42c1" # 紫色

        # 为每个分组创建子菜单
        bg_keys = list(password_groups.keys())
        for i, group_name in enumerate(bg_keys):
            group_passwords = password_groups[group_name]
            
            # 添加文件夹Emoji
            group_menu = QMenu(f"📂 {group_name}", self)
            group_menu.setIcon(self.create_color_icon(COLOR_GROUP, 'rect'))
            
            # 为每个密码创建子菜单
            for j, (id, name, username, password) in enumerate(group_passwords):
                # 添加钥匙Emoji
                password_menu = QMenu(f"🔑 {name}", group_menu)
                password_menu.setIcon(self.create_color_icon(COLOR_ITEM, 'circle'))
                
                # 添加火箭Emoji
                oneclick_action = QAction("🚀 OneClick (一键输入)", password_menu)
                oneclick_action.setIcon(self.create_color_icon(COLOR_ONECLICK, 'circle'))
                
                # 设置字体加粗
                font = oneclick_action.font()
                font.setBold(True)
                oneclick_action.setFont(font)
                
                # 添加用户Emoji
                username_action = QAction(f"👤 User: {username}", password_menu)
                # 添加剪贴板Emoji
                password_action = QAction("📋 Password", password_menu)
                
                oneclick_action.triggered.connect(
                    lambda checked, u=username, p=password: self.oneclick_action(u, p))
                username_action.triggered.connect(
                    lambda checked, u=username: self.username_action(u))
                password_action.triggered.connect(
                    lambda checked, p=password: self.password_action(p))
                
                password_menu.addAction(oneclick_action)
                password_menu.addSeparator() # 分割线区分OneClick
                password_menu.addAction(username_action)
                password_menu.addAction(password_action)
                
                group_menu.addMenu(password_menu)
                
                # 在名称之间添加分割线（除了最后一个）
                if j < len(group_passwords) - 1:
                    group_menu.addSeparator()
            
            self.addMenu(group_menu)
            
            # 在组之间添加分割线（除了最后一个）
            if i < len(bg_keys) - 1:
                self.addSeparator()
    
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
                padding: 6px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
            QMenu::item {
                padding: 8px 32px 8px 12px;
                border-radius: 6px;
                margin: 2px 0px;
                font-size: 14px;
                color: #24292e;
            }
            QMenu::item:selected {
                background-color: #f0f7ff;
                color: #0366d6;
            }
            QMenu::separator {
                height: 1px;
                background-color: #eaecef;
                margin: 4px 10px;
            }
            /* 子菜单样式 - 嵌套时保持一致 */
            QMenu QMenu {
                border: 1px solid #d1d5da;
            }
            /* 箭头样式 */
            QMenu::right-arrow {
                image: none;
                border-left: 2px solid #6a737d;
                border-top: 2px solid transparent;
                border-bottom: 2px solid transparent;
                width: 0px;
                height: 0px;
                margin-right: 8px;
            }
            QMenu::right-arrow:selected {
                border-left: 2px solid #0366d6;
            }
        """)
        
        # 设置属性
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WA_DeleteOnClose)
    
    def oneclick_action(self, username, password):
        # 关闭菜单
        self.close()
        
        # 允许短暂的时间切换焦点，但尽量缩短
        time.sleep(0.05) 
        
        # 模拟键盘输入：用户名 -> Tab -> 密码 -> Enter
        # explicit interval=0 ensures fastest typing
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