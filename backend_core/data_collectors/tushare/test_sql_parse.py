import re
import csv

def parse_sql_line_to_dict(sql_line):
    print(f"原始SQL: {sql_line}")
    matches = re.findall(r'\((.*?)\)', sql_line, re.DOTALL)
    if len(matches) < 2:
        print(f"SQL解析失败: {sql_line}")
        return None
    fields_raw = matches[0]
    values_raw = matches[1]
    print(f"原始字段串: {fields_raw}")
    print(f"原始值串: {values_raw}")
    fields = [f.replace('`','').strip() for f in fields_raw.split(',')]
    values = next(csv.reader([values_raw], quotechar="'", skipinitialspace=True))
    values = [v.strip() for v in values]
    print(f"分割后字段: {fields}")
    print(f"分割后值: {values}")
    if len(fields) != len(values):
        print(f"字段数与值数不一致，fields={fields}, values={values}, line={sql_line}")
        return None
    row = dict(zip(fields, values))
    print(f"最终解析row: {row}")
    return row

if __name__ == "__main__":
    sql_examples = """
    REPLACE INTO MKT_STK_BASICINFO (`ts_code`, `trade_date`, `close`, `open`, `high`, `low`, `pre_close`, `change`, `pct_change`, `vol`, `amount`) VALUES ('000001.SZ', '20250815', '12.08', '12.23', '12.23', '11.94', '12.2', '-0.12', '-0.9836', '1948502.95', '2344073.499');
    REPLACE INTO MKT_STK_BASICINFO (`ts_code`, `trade_date`, `close`, `open`, `high`, `low`, `pre_close`, `change`, `pct_change`, `vol`, `amount`) VALUES ('000002.SZ', '20250815', '13.08', '13.23', '13.23', '12.94', '13.2', '-0.22', '-1.6836', '2948502.95', '3344073.499');
    """
    sql_statements = [stmt.strip() for stmt in sql_examples.split(';') if stmt.strip().startswith('REPLACE INTO')]
    for stmt in sql_statements:
        parse_sql_line_to_dict(stmt)
