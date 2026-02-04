import sqlite3
import os

class PasswordDatabase:
    def __init__(self, db_file='passwords.db'):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.create_table()
    
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            group_name TEXT DEFAULT '未分组',
            note TEXT DEFAULT ''
        )
        ''')
        
        # 检查是否需要迁移（添加note列）
        cursor.execute("PRAGMA table_info(passwords)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'note' not in columns:
            cursor.execute("ALTER TABLE passwords ADD COLUMN note TEXT DEFAULT ''")
        
        # 创建独立的普通分组表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        ''')
        
        # 确保默认分组存在
        cursor.execute("INSERT OR IGNORE INTO groups (name) VALUES ('未分组')")
        
        # 迁移：将现有的所有不同分组同步到 create groups 表中
        cursor.execute('SELECT DISTINCT group_name FROM passwords')
        existing_groups = [row[0] for row in cursor.fetchall()]
        for grp in existing_groups:
            if grp:
                cursor.execute("INSERT OR IGNORE INTO groups (name) VALUES (?)", (grp,))
        
        self.conn.commit()
    
    def add_password(self, name, username, password, group_name='未分组', note=''):
        cursor = self.conn.cursor()
        cursor.execute('SELECT MIN(t1.id + 1) FROM passwords t1 LEFT JOIN passwords t2 ON t1.id + 1 = t2.id WHERE t2.id IS NULL')
        next_id = cursor.fetchone()[0]
        if next_id is None:
            next_id = 1
            
        cursor.execute(
            'INSERT INTO passwords (id, name, username, password, group_name, note) VALUES (?, ?, ?, ?, ?, ?)',
            (next_id, name, username, password, group_name, note)
        )
        self.conn.commit()
        return next_id
    
    def update_password(self, password_id, name, username, password, group_name='未分组', note=''):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE passwords SET name=?, username=?, password=?, group_name=?, note=? WHERE id=?',
            (name, username, password, group_name, note, password_id)
        )
        self.conn.commit()
    
    def update_note(self, password_id, note):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE passwords SET note=? WHERE id=?',
            (note, password_id)
        )
        self.conn.commit()

    def get_all_groups(self):
        """获取所有分组（包括空分组）"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT name FROM groups ORDER BY name')
        return [row[0] for row in cursor.fetchall()]
    
    def add_group(self, group_name):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO groups (name) VALUES (?)", (group_name,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # 分组已存在

    def delete_group(self, group_name):
        """删除分组。注意：如果有密码属于该分组，需要决定如何处理。目前策略是仅删除分组定义，不影响密码（虽然UI上可能会有显示问题，建议UI层限制）"""
        # 这里我们简单地删除分组记录。如果密码表里还有这个引用，它在get_all_groups里就不见了，
        # 但在密码列表里可能还能看到（如果不一致）。
        # 更好的做法可能是检查是否为空。
        cursor = self.conn.cursor()
        # 检查是否有关联密码
        cursor.execute('SELECT COUNT(*) FROM passwords WHERE group_name = ?', (group_name,))
        count = cursor.fetchone()[0]
        if count > 0:
            return False, f"分组'{group_name}'不为空，无法删除！"
            
        cursor.execute('DELETE FROM groups WHERE name = ?', (group_name,))
        self.conn.commit()
        return True, "删除成功"
    
    def get_passwords_by_group(self, group_name):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, name, username, password, note FROM passwords WHERE group_name = ?',
            (group_name,)
        )
        return cursor.fetchall()
    
    def get_all_passwords(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, username, password, group_name, note FROM passwords ORDER BY group_name, name')
        return cursor.fetchall()
    
    def get_password_by_id(self, password_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, name, username, password, group_name, note FROM passwords WHERE id = ?',
            (password_id,)
        )
        return cursor.fetchone()
    
    def delete_password(self, password_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM passwords WHERE id = ?', (password_id,))
        self.conn.commit()
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()
            
    def check_name_exists(self, name, group_name, exclude_id=None):
        cursor = self.conn.cursor()
        if exclude_id is None:
            # 新增时检查
            cursor.execute(
                'SELECT COUNT(*) FROM passwords WHERE name = ? AND group_name = ?',
                (name, group_name)
            )
        else:
            # 更新时检查，排除当前记录
            cursor.execute(
                'SELECT COUNT(*) FROM passwords WHERE name = ? AND group_name = ? AND id != ?',
                (name, group_name, exclude_id)
            )
        return cursor.fetchone()[0] > 0