#!/usr/bin/env python3
"""
测试数据库连接的脚本
"""

import psycopg2
import sys
from datetime import datetime

# 开发环境数据库配置
DEV_DB_CONFIG = {
    'host': '192.168.31.237',
    'port': 5446,
    'database': 'stock_analysis',
    'user': 'postgres',
    'password': 'qidianspacetime'
}

# 生产环境数据库配置
PROD_DB_CONFIG = {
    'host': '192.168.16.4',
    'port': 5432,
    'database': 'stock_analysis',
    'user': 'postgres',
    'password': 'qidianspacetime$91'
}

def test_connection(db_config, name):
    """测试数据库连接"""
    try:
        print(f"🔍 测试 {name} 数据库连接...")
        print(f"   主机: {db_config['host']}:{db_config['port']}")
        print(f"   数据库: {db_config['database']}")
        print(f"   用户: {db_config['user']}")
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # 检查stock_news表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'stock_news'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        print(f"   stock_news表存在: {'✅' if table_exists else '❌'}")
        
        if table_exists:
            # 检查表结构
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'stock_news'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"   表结构 ({len(columns)} 列):")
            for col in columns:
                print(f"     {col[0]}: {col[1]} (nullable: {col[1] == 'YES'}, default: {col[3]})")
            
            # 检查id字段的序列
            cursor.execute("""
                SELECT pg_get_serial_sequence('stock_news', 'id');
            """)
            
            sequence = cursor.fetchone()
            if sequence and sequence[0]:
                print(f"   id字段序列: ✅ {sequence[0]}")
                
                # 检查序列状态
                cursor.execute("""
                    SELECT last_value, is_called 
                    FROM stock_news_id_seq;
                """)
                
                seq_info = cursor.fetchone()
                if seq_info:
                    print(f"   序列状态: 当前值={seq_info[0]}, 已调用={seq_info[1]}")
            else:
                print(f"   id字段序列: ❌ 未关联序列")
            
            # 检查表中的数据量
            cursor.execute("SELECT COUNT(*) FROM stock_news")
            count = cursor.fetchone()[0]
            print(f"   数据量: {count} 条记录")
        
        cursor.close()
        conn.close()
        print(f"   ✅ {name} 数据库连接成功")
        return True
        
    except Exception as e:
        print(f"   ❌ {name} 数据库连接失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始测试数据库连接...")
    print("=" * 60)
    
    # 测试开发环境数据库
    dev_success = test_connection(DEV_DB_CONFIG, "开发环境")
    
    print()
    
    # 测试生产环境数据库
    prod_success = test_connection(PROD_DB_CONFIG, "生产环境")
    
    print()
    print("=" * 60)
    
    if dev_success:
        print("✅ 开发环境数据库可用，可以使用此数据库进行修复")
        print("   建议：在开发环境修复序列问题，然后迁移到生产环境")
    elif prod_success:
        print("✅ 生产环境数据库可用，可以直接在生产环境修复")
    else:
        print("❌ 两个数据库都无法连接，请检查网络和配置")
    
    return dev_success or prod_success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 程序异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
