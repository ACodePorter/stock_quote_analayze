"""
为采集日志表添加 collect_source 字段的初始化脚本
"""
from sqlalchemy import text
from backend_api.database import SessionLocal

def add_collect_source_field():
    """为采集日志表添加 collect_source 字段"""
    session = SessionLocal()
    try:
        # 为 historical_collect_operation_logs 表添加字段
        session.execute(text('''
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='historical_collect_operation_logs' 
                               AND column_name='collect_source') THEN
                    ALTER TABLE historical_collect_operation_logs 
                    ADD COLUMN collect_source TEXT DEFAULT 'akshare';
                    RAISE NOTICE '已为 historical_collect_operation_logs 表添加 collect_source 字段';
                ELSE
                    RAISE NOTICE 'historical_collect_operation_logs 表已存在 collect_source 字段';
                END IF;
            END
            $$;
        '''))
        
        # 为 realtime_collect_operation_logs 表添加字段
        session.execute(text('''
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name='realtime_collect_operation_logs' 
                               AND column_name='collect_source') THEN
                    ALTER TABLE realtime_collect_operation_logs 
                    ADD COLUMN collect_source TEXT DEFAULT 'akshare';
                    RAISE NOTICE '已为 realtime_collect_operation_logs 表添加 collect_source 字段';
                ELSE
                    RAISE NOTICE 'realtime_collect_operation_logs 表已存在 collect_source 字段';
                END IF;
            END
            $$;
        '''))
        
        session.commit()
        print("✅ 成功为采集日志表添加 collect_source 字段")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 添加字段失败: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    add_collect_source_field()

