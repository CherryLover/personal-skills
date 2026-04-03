# TcbCommandRegistry 注册模板

## 文件位置
`shared-biz/src/commonMain/kotlin/com/bin/chaos/shared_biz/protocol/tcb/commands/`

## 按指令分类选择文件

| 指令分类 | 文件 | 示例指令 |
|---------|------|---------|
| 系统信息/锁控制 | `SystemCommands.kt` | REQ_FIRMWARE_VERSION, REQ_UNLOCK, REQ_GET_AUTOLOCK |
| 时间管理 | `TimeCommands.kt` | REQ_READ_TIME, REQ_WRITE_TIME |
| 用户管理 | `UserCommands.kt` | REQ_ADMIN_LOGIN, REQ_DELETE_USER |
| WiFi 配置 | `WifiCommands.kt` | REQ_SET_WIFI_AP, REQ_GET_WIFI_STATUS |

## 注册模板（无返回值）

```kotlin
// 在 register() 方法中添加

// REQ_SET_XXX - 设置XXX (0xXX)
registry.register("REQ_SET_XXX") { operator, params ->
    // 从 params 提取参数
    val value = params["value"]?.toString()?.toIntOrNull() ?: 0

    // 调用业务层方法
    val result = operator.config.setXxx(value)

    // 处理结果
    TcbCommandUtils.handleUnitResult(result)
}
```

## 注册模板（返回简单值）

```kotlin
// REQ_GET_XXX - 获取XXX (0xXX)
registry.register("REQ_GET_XXX") { operator, params ->
    val result = operator.config.getXxx()

    // 根据返回值类型选择方法
    TcbCommandUtils.handleIntResult(result, "xxxValue")
    // TcbCommandUtils.handleStringResult(result, "xxxValue")
    // TcbCommandUtils.handleBooleanResult(result, "xxxValue")
    // TcbCommandUtils.handleLongResult(result, "xxxValue")
}
```

## 注册模板（返回复杂对象）

```kotlin
// REQ_GET_XXX_INFO - 获取XXX信息 (0xXX)
registry.register("REQ_GET_XXX_INFO") { operator, params ->
    val result = operator.config.getXxxInfo()

    TcbCommandUtils.handleResult(result) { response ->
        jsonObject {
            put("field1", response.field1)
            put("field2", response.field2)
            put("field3", response.field3)
            // 可选字段
            response.optionalField?.let { put("optionalField", it) }
        }
    }
}
```

## TcbCommandUtils 方法速查

| 方法 | 返回值类型 | 用途 |
|------|-----------|------|
| `handleUnitResult(result)` | Unit | 无返回值操作（设置类） |
| `handleIntResult(result, key)` | Int | 整型值 |
| `handleLongResult(result, key)` | Long | 长整型值 |
| `handleStringResult(result, key)` | String | 字符串 |
| `handleBooleanResult(result, key)` | Boolean | 布尔值 |
| `handleResult(result) { ... }` | 自定义 | 复杂对象，需构建 JsonObject |

## 参数提取示例

```kotlin
// Int 参数
val intValue = params["key"]?.toString()?.toIntOrNull() ?: defaultValue

// Long 参数
val longValue = params["key"]?.toString()?.toLongOrNull() ?: defaultValue

// Boolean 参数
val boolValue = params["key"]?.toString()?.toBoolean() ?: false

// String 参数
val strValue = params["key"]?.toString() ?: ""

// 可选参数（可能为 null）
val optionalValue = params["key"]?.toString()?.toIntOrNull()
```

## 注意事项
- 指令名称必须与 `js/config.js` 中的 `commandName` 一致
- 遗漏注册会导致 JsBridge 调用时报 "指令未注册" 错误
- 参数名（如 `value`）需与 JsBridge 配置中的 params key 对应
