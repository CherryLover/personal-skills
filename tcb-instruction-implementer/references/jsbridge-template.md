# JsBridge 配置模板

## 文件位置
`composeApp/src/androidMain/assets/js/config.js`

## 基础配置模板

在 `DEFAULT_TCB_COMMANDS` 数组中添加：

```javascript
// === X.X {分类名称} ===
{
  commandName: 'REQ_XXX',           // 必须与 Registry 注册的名称一致
  params: {},                        // 无参数
  timeout: 5000,                     // 超时时间（毫秒）
  enabled: true                      // 是否默认启用
}
```

## 带参数配置模板

```javascript
{
  commandName: 'REQ_SET_XXX',
  params: {
    "value": 0,                      // key 必须加引号
    "option": "default"
  },
  timeout: 5000,
  enabled: false                     // 设置类操作建议默认禁用
}
```

## 完整示例

```javascript
const DEFAULT_TCB_COMMANDS = [
  // === 1. 系统信息 ===
  {
    commandName: 'REQ_GET_FIRMWARE_VERSION',
    params: {},
    timeout: 5000,
    enabled: true
  },

  // === 2. 锁控制 ===
  {
    commandName: 'REQ_GET_AUTOLOCK',
    params: {},
    timeout: 5000,
    enabled: true
  },
  {
    commandName: 'REQ_SET_AUTOLOCK',
    params: {
      "seconds": 30
    },
    timeout: 5000,
    enabled: false
  },

  // === 3. 时间管理 ===
  {
    commandName: 'REQ_READ_TIME',
    params: {},
    timeout: 5000,
    enabled: true
  },
  {
    commandName: 'REQ_WRITE_TIME',
    params: {
      "timestamp": 1703001600000
    },
    timeout: 5000,
    enabled: false
  },

  // === 4. 配置 ===
  {
    commandName: 'REQ_GET_LANGUAGE',
    params: {},
    timeout: 5000,
    enabled: true
  },
  {
    commandName: 'REQ_SET_LANGUAGE',
    params: {
      "languageCode": 0
    },
    timeout: 5000,
    enabled: false
  }
];
```

## 参数配置规范

### 参数格式
- Key 必须加双引号：`"paramKey": value`
- 字符串值加引号：`"mode": "auto"`
- 数值不加引号：`"count": 10`
- 布尔值不加引号：`"enabled": true`

### 启用状态建议
| 指令类型 | enabled | 原因 |
|---------|---------|------|
| 查询/读取 | `true` | 安全，可直接测试 |
| 设置/修改 | `false` | 避免误操作 |
| 删除/危险 | `false` | 必须手动启用 |

### 超时设置
| 操作类型 | timeout | 说明 |
|---------|---------|------|
| 简单查询 | 5000 | 5秒 |
| 复杂查询 | 10000 | 10秒（如读取列表） |
| 写入操作 | 5000-10000 | 视操作复杂度 |
| WiFi 操作 | 15000-30000 | 网络操作较慢 |

## 测试方式

1. 打开 `ble-demo.html` 页面
2. 连接设备
3. 在 "TCB 批量指令" 区域勾选要测试的指令
4. 点击执行，查看结果

## 注意事项
- `commandName` 必须与 `TcbCommandRegistry` 中注册的名称完全一致
- 参数 key 必须与 Registry 中 `params["key"]` 对应
- 新增指令建议先设为 `enabled: false`，测试通过后再改为 `true`
