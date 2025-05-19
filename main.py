import sys
from PyQt5.QtWidgets import QApplication
from password_manager import PasswordManagerWindow
from hotkey_manager import HotkeyManager

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口后应用继续运行
    
    # 创建密码管理窗口
    password_manager = PasswordManagerWindow()
    password_manager.show()
    
    # 创建全局快捷键管理器
    hotkey_manager = HotkeyManager(password_manager)
    
    # 保持对hotkey_manager的引用，防止被垃圾回收
    app.hotkey_manager = hotkey_manager
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()