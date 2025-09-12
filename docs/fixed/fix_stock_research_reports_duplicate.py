#!/usr/bin/env python3
"""
修复生产环境stock_research_reports表重复数据问题的脚本
"""
import psycopg2
import sys
import traceback
from datetime import datetime

# 生产环境数据库配置
DB_CONFIG = {
    'host': '192.168.16.4',
    'port': 8432,
    'database': 'stock_analysis',
    'user': 'postgres',
    'password': 'qidianspacetime$91'
}

def test_connection():
    """测试数据库连接"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ 生产环境数据库连接成功")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 生产环境数据库连接失败: {e}")
        print("💡 请检查：")
        print("   1. 生产环境数据库服务是否运行")
        print("   2. 网络连接是否正常")
        print("   3. 防火墙设置是否正确")
        print("   4. 数据库配置是否正确")
        return False

def check_table_structure():
    """检查stock_research_reports表结构"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("📋 检查stock_research_reports表结构...")
        
        # 检查表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'stock_research_reports'
            );
        """)
        
        if not cursor.fetchone()[0]:
            print("❌ stock_research_reports表不存在")
            return False
        
        # 检查表结构
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'stock_research_reports'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"✅ 表结构检查完成，共 {len(columns)} 列")
        
        # 检查唯一约束
        cursor.execute("""
            SELECT conname, contype, pg_get_constraintdef(oid) as constraint_def
            FROM pg_constraint 
            WHERE conrelid = 'stock_research_reports'::regclass;
        """)
        
        constraints = cursor.fetchall()
        print(f"✅ 约束检查完成，共 {len(constraints)} 个约束")
        for constraint in constraints:
            print(f"   约束名: {constraint[0]}, 类型: {constraint[1]}, 定义: {constraint[2]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查表结构失败: {e}")
        traceback.print_exc()
        return False

def backup_table():
    """备份stock_research_reports表"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("💾 备份stock_research_reports表...")
        
        # 创建备份表
        backup_table_name = f"stock_research_reports_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cursor.execute(f"""
            CREATE TABLE {backup_table_name} AS 
            SELECT * FROM stock_research_reports;
        """)
        
        # 获取备份记录数
        cursor.execute(f"SELECT COUNT(*) FROM {backup_table_name}")
        backup_count = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ 备份完成，表名: {backup_table_name}，记录数: {backup_count}")
        return backup_table_name
        
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        traceback.print_exc()
        return None

def find_duplicate_records():
    """查找重复记录"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔍 查找重复记录...")
        
        # 查找重复的记录
        cursor.execute("""
            SELECT stock_code, stock_name, report_name, report_date, COUNT(*) as count
            FROM stock_research_reports
            GROUP BY stock_code, stock_name, report_name, report_date
            HAVING COUNT(*) > 1
            ORDER BY count DESC, stock_code, report_date;
        """)
        
        duplicates = cursor.fetchall()
        print(f"✅ 发现 {len(duplicates)} 组重复记录")
        
        if duplicates:
            print("重复记录详情:")
            for dup in duplicates:
                print(f"   股票代码: {dup[0]}, 股票名称: {dup[1]}")
                print(f"   报告名称: {dup[2]}")
                print(f"   报告日期: {dup[3]}, 重复次数: {dup[4]}")
                print("   " + "-" * 50)
        
        cursor.close()
        conn.close()
        return duplicates
        
    except Exception as e:
        print(f"❌ 查找重复记录失败: {e}")
        traceback.print_exc()
        return []

def remove_duplicates():
    """移除重复记录，保留最新的一条"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🧹 开始移除重复记录...")
        
        # 使用窗口函数找出重复记录，保留最新的一条
        cursor.execute("""
            DELETE FROM stock_research_reports 
            WHERE id IN (
                SELECT id FROM (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY stock_code, stock_name, report_name, report_date
                               ORDER BY updated_at DESC, id DESC
                           ) as rn
                    FROM stock_research_reports
                ) t
                WHERE t.rn > 1
            );
        """)
        
        deleted_count = cursor.rowcount
        print(f"✅ 删除了 {deleted_count} 条重复记录")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return deleted_count
        
    except Exception as e:
        print(f"❌ 移除重复记录失败: {e}")
        traceback.print_exc()
        return 0

def verify_fix():
    """验证修复结果"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔍 验证修复结果...")
        
        # 检查是否还有重复记录
        cursor.execute("""
            SELECT stock_code, stock_name, report_name, report_date, COUNT(*) as count
            FROM stock_research_reports
            GROUP BY stock_code, stock_name, report_name, report_date
            HAVING COUNT(*) > 1;
        """)
        
        remaining_duplicates = cursor.fetchall()
        
        if not remaining_duplicates:
            print("✅ 验证成功：没有重复记录")
            
            # 显示总记录数
            cursor.execute("SELECT COUNT(*) FROM stock_research_reports")
            total_count = cursor.fetchone()[0]
            print(f"✅ 当前表中共有 {total_count} 条记录")
            
            return True
        else:
            print(f"❌ 仍有 {len(remaining_duplicates)} 组重复记录")
            return False
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        traceback.print_exc()
        return False

def add_unique_constraint():
    """添加唯一约束防止未来重复"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔒 添加唯一约束...")
        
        # 检查是否已存在唯一约束
        cursor.execute("""
            SELECT conname, contype, pg_get_constraintdef(oid) as constraint_def
            FROM pg_constraint 
            WHERE conrelid = 'stock_research_reports'::regclass
            AND contype = 'u';
        """)
        
        existing_constraints = cursor.fetchall()
        
        if existing_constraints:
            print("✅ 已存在唯一约束:")
            for constraint in existing_constraints:
                print(f"   {constraint[0]}: {constraint[2]}")
        else:
            # 添加唯一约束
            cursor.execute("""
                ALTER TABLE stock_research_reports 
                ADD CONSTRAINT uk_stock_research_reports_unique 
                UNIQUE (stock_code, report_name, report_date);
            """)
            print("✅ 成功添加唯一约束: uk_stock_research_reports_unique")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 添加唯一约束失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始修复生产环境stock_research_reports表重复数据问题...")
    print("=" * 60)
    print("⚠️  警告：此脚本将在生产环境执行，请确保：")
    print("   1. 已备份重要数据")
    print("   2. 在维护窗口期间执行")
    print("   3. 有回滚方案")
    print("=" * 60)
    
    # 1. 测试连接
    if not test_connection():
        return False
    
    print()
    
    # 2. 检查表结构
    if not check_table_structure():
        return False
    
    print()
    
    # 3. 备份表（可选）
    backup_table_name = backup_table()
    if not backup_table_name:
        print("⚠️  备份失败，但继续执行修复...")
    
    print()
    
    # 4. 查找重复记录
    duplicates = find_duplicate_records()
    if not duplicates:
        print("✅ 没有发现重复记录，无需修复")
        return True
    
    print()
    
    # 5. 移除重复记录
    deleted_count = remove_duplicates()
    if deleted_count == 0:
        print("⚠️  没有删除任何记录")
    
    print()
    
    # 6. 验证修复
    if not verify_fix():
        return False
    
    print()
    
    # 7. 添加唯一约束
    if not add_unique_constraint():
        print("⚠️  添加唯一约束失败，但数据已修复")
    
    print()
    print("🎉 生产环境修复完成！stock_research_reports表现在应该可以正常工作了。")
    if backup_table_name:
        print(f"💾 备份表: {backup_table_name}")
        print("💡 建议：确认系统正常运行后，可以删除备份表")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 程序异常: {e}")
        traceback.print_exc()
        sys.exit(1)
