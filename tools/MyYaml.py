# 没有装PyYaml模块，自己写一个代替的
def dump(data:dict,indent=0) -> str:
    '''代替PyYaml模块中的dump函数，但只实现了将键和值为字符串、字典、列表的字典转化为文本'''
    yaml_str = ""
    space = "  " * indent  # 缩进量
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                yaml_str += f"{space}{key}:\n{dump(value, indent + 1)}"
            else:
                yaml_str += f"{space}{key}: {format_value(value)}\n"
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                yaml_str += f"{space}\n{dump(item, indent + 1)}"
            else:
                yaml_str += f"{space}{format_value(item)}\n"
    return yaml_str

def format_value(value):
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        return str(value)  # 字符串类型直接输出（未处理特殊字符）

# 示例用法
if __name__ == '__main__':
    import datetime
    data = {
        "name": "Alice",
        "age": 30,
        "skills": ["Python", "YAML"],
        "contact": {
            "email": "alice@example.com",
            "active": True
        },
        "date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": None
    }
    print(dump(data))