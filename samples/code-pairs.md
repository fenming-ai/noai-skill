# 代码表达样例

去味只处理用户授权的注释和说明，不借机重构、改名或改变异常与返回行为。

## 重复注释可以删除，函数保持不动

原文：
```python
# This function transforms the data and returns the result.
def process_data(data):
    return data.transform()
```

改后：
```python
def process_data(data):
    return data.transform()
```

依据：注释只复述可见行为。没有资料说明业务目的，不能补“临时方案”、日期或故障经历。`process_data` 是否合适是命名任务，不能仅凭通用动词认定有问题。

## 必要说明保留

原文与改后相同：
```python
# Keep cleanup in finally: it must run when api_call raises.
try:
    return api_call()
finally:
    cleanup_resources()
```

依据：注释说明异常路径，删掉或改成重试逻辑都超出去味范围。一致命名、相同长度和完整错误处理不是缺陷证据。
