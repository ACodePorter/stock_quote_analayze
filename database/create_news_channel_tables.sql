-- 资讯频道数据库扩展脚本
-- 创建时间: 2025-09-08

-- 1. 创建资讯分类表
CREATE TABLE IF NOT EXISTS news_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认分类
INSERT INTO news_categories (name, description, sort_order) VALUES
('全部', '所有资讯', 1),
('市场动态', '市场行情、指数变化等', 2),
('政策解读', '政策法规、监管动态等', 3),
('公司资讯', '上市公司公告、财报等', 4),
('国际财经', '国际市场、汇率等', 5),
('分析研判', '专业分析、投资建议等', 6)
ON CONFLICT (name) DO NOTHING;

-- 2. 为stock_news表添加新字段
ALTER TABLE stock_news ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES news_categories(id);
ALTER TABLE stock_news ADD COLUMN IF NOT EXISTS read_count INTEGER DEFAULT 0;
ALTER TABLE stock_news ADD COLUMN IF NOT EXISTS is_hot BOOLEAN DEFAULT FALSE;
ALTER TABLE stock_news ADD COLUMN IF NOT EXISTS tags TEXT[];
ALTER TABLE stock_news ADD COLUMN IF NOT EXISTS summary TEXT;
ALTER TABLE stock_news ADD COLUMN IF NOT EXISTS image_url TEXT;

-- 3. 创建索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_stock_news_category_id ON stock_news(category_id);
CREATE INDEX IF NOT EXISTS idx_stock_news_read_count ON stock_news(read_count);
CREATE INDEX IF NOT EXISTS idx_stock_news_is_hot ON stock_news(is_hot);
CREATE INDEX IF NOT EXISTS idx_stock_news_publish_time ON stock_news(publish_time);

-- 4. 更新现有数据的分类
UPDATE stock_news SET category_id = 2 WHERE category_id IS NULL;

-- 5. 创建视图：热门资讯
CREATE OR REPLACE VIEW hot_news_view AS
SELECT 
    id,
    title,
    summary,
    publish_time,
    source,
    read_count,
    is_hot,
    tags,
    image_url
FROM stock_news 
WHERE is_hot = TRUE 
ORDER BY read_count DESC;

-- 6. 创建函数：更新热门资讯标记
CREATE OR REPLACE FUNCTION update_hot_news_mark()
RETURNS VOID AS $$
BEGIN
    -- 清除所有热门标记
    UPDATE stock_news SET is_hot = FALSE;
    
    -- 将阅读量前10的新闻标记为热门
    UPDATE stock_news SET is_hot = TRUE 
    WHERE id IN (
        SELECT id FROM stock_news 
        ORDER BY read_count DESC 
        LIMIT 10
    );
END;
$$ LANGUAGE plpgsql;

-- 7. 创建触发器：自动更新摘要
CREATE OR REPLACE FUNCTION update_news_summary()
RETURNS TRIGGER AS $$
BEGIN
    -- 如果没有摘要，自动生成
    IF NEW.summary IS NULL OR NEW.summary = '' THEN
        IF LENGTH(NEW.content) > 200 THEN
            NEW.summary := LEFT(NEW.content, 200) || '...';
        ELSE
            NEW.summary := NEW.content;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_news_summary
    BEFORE INSERT OR UPDATE ON stock_news
    FOR EACH ROW
    EXECUTE FUNCTION update_news_summary();

-- 8. 创建统计表：资讯统计
CREATE TABLE IF NOT EXISTS news_statistics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    total_news INTEGER DEFAULT 0,
    hot_news_count INTEGER DEFAULT 0,
    total_reads INTEGER DEFAULT 0,
    category_stats JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

-- 9. 插入一些示例数据（可选）
INSERT INTO stock_news (title, content, publish_time, source, category_id, summary, tags, read_count, is_hot)
VALUES 
('A股三大指数集体收涨 科技板块领涨', 
 '今日A股市场表现强劲，上证指数上涨0.8%，深证成指上涨1.2%，创业板指上涨1.5%。科技股、新能源汽车、AI概念等板块表现突出，市场情绪明显回暖。',
 NOW() - INTERVAL '2 hours',
 '财经日报',
 2,
 '今日A股市场表现强劲，上证指数上涨0.8%，深证成指上涨1.2%，创业板指上涨1.5%...',
 ARRAY['科技', 'AI', '新能源'],
 12000,
 TRUE),
('央行降准0.5个百分点释放长期流动性约1万亿元',
 '中国人民银行决定下调金融机构存款准备金率0.5个百分点，释放长期流动性约1万亿元，以支持实体经济发展。',
 NOW() - INTERVAL '30 minutes',
 '央行官网',
 3,
 '中国人民银行决定下调金融机构存款准备金率0.5个百分点，释放长期流动性约1万亿元...',
 ARRAY['政策', '央行', '流动性'],
 58000,
 TRUE),
('比亚迪发布2024年业绩预告净利润同比增长28%',
 '比亚迪发布2024年业绩预告，预计实现净利润30-35亿元，同比增长28%。主要受益于新能源汽车销量大幅增长。',
 NOW() - INTERVAL '1 hour',
 '上交所',
 4,
 '比亚迪发布2024年业绩预告，预计实现净利润30-35亿元，同比增长28%...',
 ARRAY['比亚迪', '新能源', '业绩'],
 32000,
 FALSE)
ON CONFLICT DO NOTHING;

-- 10. 创建权限（如果需要）
-- GRANT SELECT, INSERT, UPDATE ON news_categories TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE ON stock_news TO your_app_user;
-- GRANT USAGE ON SEQUENCE news_categories_id_seq TO your_app_user;
-- GRANT USAGE ON SEQUENCE stock_news_id_seq TO your_app_user;

COMMENT ON TABLE news_categories IS '资讯分类表';
COMMENT ON TABLE news_statistics IS '资讯统计表';
COMMENT ON VIEW hot_news_view IS '热门资讯视图';
COMMENT ON FUNCTION update_hot_news_mark() IS '更新热门资讯标记函数';
COMMENT ON FUNCTION update_news_summary() IS '自动更新新闻摘要函数';
