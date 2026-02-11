import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from password_manager import PasswordManagerWindow, DatabaseSetupDialog, StartupLoginDialog
from hotkey_manager import HotkeyManager
from config_manager import ConfigManager
from database import PasswordDatabase

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口后应用继续运行
    
    # 1. 加载配置
    config_mgr = ConfigManager()
    db_path = config_mgr.get_db_path()
    
    # 自动尝试检测默认数据库（如果配置不存在）
    if not db_path:
        default_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'passwords.db')
        if os.path.exists(default_db):
            db_path = default_db
            config_mgr.set_db_path(db_path) # 自动保存回去
    
    # 2. 检查数据库路径有效性
    while True:
        path_valid = False
        if db_path and os.path.exists(db_path):
            try:
                # 简单验证
                PasswordDatabase(db_path)
                path_valid = True
            except Exception:
                path_valid = False
        
        if path_valid:
            break
            
        # 路径无效或未设置，弹出设置窗口
        dialog = DatabaseSetupDialog()
        if dialog.exec_() == DatabaseSetupDialog.Accepted:
            db_path = os.path.abspath(dialog.db_path) # 确保转换为绝对路径
            # 如果是创建模式且设置了密码，需要写入数据库
            if dialog.is_create_mode:
                try:
                    # 注意：这里我们明确使用通过Dialog获取的路径，避免使用默认值
                    temp_db = PasswordDatabase(db_path)
                    if dialog.startup_password:
                        temp_db.set_startup_password(dialog.startup_password)
                    # 确保显式关闭连接（尽管GC会处理，但在循环中显式更好）
                    del temp_db 
                except Exception as e:
                    QMessageBox.critical(None, "错误", f"无法初始化数据库: {str(e)}")
                    continue
            
            # 保存配置
            config_mgr.set_db_path(db_path)
        else:
            # 用户取消设置，退出程序
            sys.exit(0)

            
    # 3. 检查启动密码
    try:
        # 这里需要保持连接直到传递给主窗口，或者只是检查密码
        # 主窗口会自己创建连接，所以这里检查完就关闭也没事，或者传递DB对象
        # 现在的架构是主窗口自己创建PasswordDatabase实例，所以我们把path传给它
        
        # 先临时连接检查密码
        check_db = PasswordDatabase(db_path)
        startup_pwd = check_db.get_startup_password()
        del check_db # 关闭连接
        
        if startup_pwd:
            login = StartupLoginDialog(startup_pwd)
            if login.exec_() != StartupLoginDialog.Accepted:
                # 登录失败或取消
                sys.exit(0)
                
    except Exception as e:
        QMessageBox.critical(None, "严重错误", f"读取数据库失败: {str(e)}")
        sys.exit(1)

    # 4. 启动主程序
    password_manager = PasswordManagerWindow(db_path)
    password_manager.show()
    
    # 创建全局快捷键管理器
    hotkey_manager = HotkeyManager(password_manager)
    
    # 保持对hotkey_manager的引用，防止被垃圾回收
    app.hotkey_manager = hotkey_manager
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
