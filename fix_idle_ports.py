import sqlite3
import os
from datetime import datetime

def fix_idle_ports():
    """修复空闲端口的连接类型数据"""
    
    # 备份数据库
    backup_path = f"database_backups/asset_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    os.makedirs('database_backups', exist_ok=True)
    
    # 复制数据库文件作为备份
    import shutil
    shutil.copy2('database/asset.db', backup_path)
    print(f"数据库已备份到: {backup_path}")
    
    # 连接数据库
    conn = sqlite3.connect('database/asset.db')
    cursor = conn.cursor()
    
    try:
        # 查找设备名称为'nan'的设备ID
        cursor.execute("SELECT id FROM devices WHERE name = 'nan'")
        nan_device_ids = [row[0] for row in cursor.fetchall()]
        print(f"找到占位符设备(nan): {nan_device_ids}")
        
        # 查找需要修复的连接记录：A端设备和B端设备都是同一个'nan'设备的记录
        idle_connections = []
        for device_id in nan_device_ids:
            cursor.execute("""
                SELECT id, source_device_id, target_device_id, connection_type
                FROM connections 
                WHERE source_device_id = ? AND target_device_id = ?
            """, (device_id, device_id))
            
            results = cursor.fetchall()
            idle_connections.extend(results)
        
        print(f"\n找到需要修复的空闲端口连接记录: {len(idle_connections)}")
        for conn_record in idle_connections:
            print(f"ID:{conn_record[0]}, A端:{conn_record[1]}, B端:{conn_record[2]}, 当前类型:{conn_record[3]}")
        
        if idle_connections:
            # 将这些连接的connection_type设置为NULL
            connection_ids = [conn_record[0] for conn_record in idle_connections]
            placeholders = ','.join(['?' for _ in connection_ids])
            
            cursor.execute(f"""
                UPDATE connections 
                SET connection_type = NULL 
                WHERE id IN ({placeholders})
            """, connection_ids)
            
            print(f"\n已将 {len(connection_ids)} 条空闲端口记录的连接类型设置为NULL")
            
            # 验证修复结果
            cursor.execute(f"""
                SELECT id, connection_type 
                FROM connections 
                WHERE id IN ({placeholders})
            """, connection_ids)
            
            print("\n修复后的记录:")
            for record in cursor.fetchall():
                print(f"ID:{record[0]}, 连接类型:{record[1]}")
        
        # 提交更改
        conn.commit()
        print("\n数据修复完成！")
        
        # 统计修复后的情况
        cursor.execute("SELECT COUNT(*) FROM connections WHERE connection_type IS NULL")
        null_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM connections WHERE connection_type = 'cable'")
        cable_count = cursor.fetchone()[0]
        
        print(f"\n修复后统计:")
        print(f"连接类型为NULL的记录数: {null_count}")
        print(f"连接类型为cable的记录数: {cable_count}")
        
    except Exception as e:
        print(f"修复过程中出现错误: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    fix_idle_ports()