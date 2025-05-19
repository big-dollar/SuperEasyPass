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
            group_name TEXT DEFAULT '未分组'
        )
        ''')
        self.conn.commit()
    
    def add_password(self, name, username, password, group_name='未分组'):
        cursor = self.conn.cursor()
        cursor.execute('SELECT MIN(t1.id + 1) FROM passwords t1 LEFT JOIN passwords t2 ON t1.id + 1 = t2.id WHERE t2.id IS NULL')
        next_id = cursor.fetchone()[0]
        if next_id is None:
            next_id = 1
            
        cursor.execute(
            'INSERT INTO passwords (id, name, username, password, group_name) VALUES (?, ?, ?, ?, ?)',
            (next_id, name, username, password, group_name)
        )
        self.conn.commit()
        return next_id
    
    def update_password(self, password_id, name, username, password, group_name='未分组'):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE passwords SET name=?, username=?, password=?, group_name=? WHERE id=?',
            (name, username, password, group_name, password_id)
        )
        self.conn.commit()
    
    def get_all_groups(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT group_name FROM passwords ORDER BY group_name')
        return [row[0] for row in cursor.fetchall()]
    
    def get_passwords_by_group(self, group_name):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, name, username, password FROM passwords WHERE group_name = ?',
            (group_name,)
        )
        return cursor.fetchall()
    
    def get_all_passwords(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, username, password, group_name FROM passwords ORDER BY group_name, name')
        return cursor.fetchall()
    
    def get_password_by_id(self, password_id):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, name, username, password, group_name FROM passwords WHERE id = ?',
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