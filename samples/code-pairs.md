# 代码媒介曲子库

> 以下为教学示例，不是实测或可直接套用的补写。具体技术、数字、日期、经历、代码行为和风险须有当前材料支持；缺少依据时只保留判断方向，不新增事实、不删必要信息、不改变程序语义。

> 代码注释/命名/结构 的 AI 味 → 人味 对比对。
> 每首曲子 = AI 默认输出 + 人味改写 + WHY + 记住什么。

---

### 曲子 1：[有温度] 注释内容

AI 味：
```python
# This function processes the data and returns the result.
def process_data(data):
    return data.transform()
```

人味：
```python
# 2024-03-15: 临时方案，等 API v2 上线后删。能跑但丑。
def normalize_input(raw):
    return raw.transform()
```

WHY：
"processes the data and returns the result"是统计最可能的注释——描述代码做什么。人写注释时有情绪和判断，会写"为什么这么做""好不好""什么时候删"。

记住什么：
注释不是说明书，是工程师的自言自语——有日期、有判断、有还债意识。

---

### 曲子 2：[有具体] 命名方式

AI 味：
```python
def handle_request(request):
    data = extract_information(request)
    result = process_information(data)
    return format_output(result)
```

人味：
```python
def parse_webhook(payload):
    event = payload.get("event_type")
    ticket = create_ticket(event)
    return ticket.to_json()
```

WHY：
"handle_request""extract_information""process_information"是统计最像"专业"的命名——抽象动词+泛化名词。人用具体业务词（parse_webhook/create_ticket），因为人知道这段代码在业务里干什么。

记住什么：
命名叫具体业务动作，不叫抽象动词。"handle""process""extract"= AI 味。

---

### 曲子 3：[有取舍] 错误处理

AI 味：
```python
try:
    result = api_call()
except Exception as e:
    logger.error(f"An error occurred: {e}")
    raise
finally:
    cleanup_resources()
```

人味：
```python
try:
    result = api_call()
except TimeoutError:
    # 超时了，重试 3 次还是挂就告警
    retry_count += 1
    if retry_count > 3:
        alert_oncall("webhook 超时，可能 Slack 挂了")
    return None
except ValueError as e:
    # payload 格式不对，不重试，记日志
    logger.warning(f"bad payload: {e}")
    return None
```

WHY：
`except Exception`是统计最安全的——catch-all 不会漏。但"不会漏"= 没有判断。人分场景处理：超时重试+告警，格式错误记日志不重试。人有判断，知道不同错误该干什么。

记住什么：
不要 catch-all。每种错误有不同处理策略 = 有人做了判断。

---

### 曲子 4：[有判断] 结构选择

AI 味：
```python
class DataProcessor:
    """A comprehensive data processing utility."""

    def __init__(self, config):
        self.config = config
        self.validator = Validator()
        self.transformer = Transformer()
        self.formatter = Formatter()

    def process(self, data):
        validated = self.validator.validate(data)
        transformed = self.transformer.transform(validated)
        formatted = self.formatter.format(transformed)
        return formatted
```

人味：
```python
def run_pipeline(raw_data, config):
    # 就三步：验→转→排。简单到不需要 class
    clean = sanitize(raw_data)
    rows = to_rows(clean, config.schema)
    return rows  # 调用方负责格式化
```

WHY：
AI 默认"全面/专业"——建 class、加 docstring、分离 validator/transformer/formatter。统计上最像"好代码"的结构。但过度封装 = 没有取舍。人知道三步逻辑不需要 class，一个函数搞定。

记住什么：
简单逻辑一行搞定，复杂逻辑才展开。过度封装 = AI 味。

---

### 曲子 5：[有节奏] 代码密度

AI 味：
```python
# 所有函数等长，所有注释密度统一，所有方法都返回同一类型
class UserService:
    def get_user(self, user_id):
        """Retrieve a user by their unique identifier."""
        user = self.repository.find_by_id(user_id)
        return user

    def update_user(self, user_id, data):
        """Update a user's information."""
        user = self.repository.find_by_id(user_id)
        user.update(data)
        self.repository.save(user)
        return user

    def delete_user(self, user_id):
        """Delete a user by their unique identifier."""
        self.repository.delete_by_id(user_id)
        return True
```

人味：
```python
def get_user(uid): return db.users.find_one(uid)
def update_user(uid, data): db.users.update(uid, data); return get_user(uid)
def delete_user(uid): db.users.delete(uid)  # 硬删，不做软删了——上次软删出过 bug
```

WHY：
AI 默认所有方法等长、所有注释统一、所有结构对称——统计最均匀的输出。人的代码有快有慢：简单的一行，复杂的展开，注释只在需要判断的地方。

记住什么：
代码有节奏——简单的一行，复杂的展开。等长等结构 = 匀速 = AI 味。

---
