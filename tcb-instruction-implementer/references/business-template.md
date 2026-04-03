# 业务层模板

## 文件位置
`shared-ble/src/commonMain/kotlin/com/anviz/multi/shared/ble/business/equip/fox/commands/XxxCommands.kt`

## 接口定义

```kotlin
/**
 * XXX操作接口
 */
interface XxxOperations {
    /**
     * 获取XXX
     */
    suspend fun getXxx(): Result<Int>

    /**
     * 设置XXX
     * @param value 参数值 (范围: 0-255)
     */
    suspend fun setXxx(value: Int): Result<Unit>
}
```

## 实现类模板（返回 Unit）

```kotlin
override suspend fun setXxx(value: Int): Result<Unit> {
    return try {
        val request = SetXxxRequest(context, value)
        val result = executor.execute(request)

        if (result.isSuccess) {
            val response = result.getOrThrow()
            if (response.isSuccess) {
                Napier.d("设置XXX成功: $value", tag = TAG)
                Result.success(Unit)
            } else {
                Napier.w("设置XXX失败: ${response.statusDescription}", tag = TAG)
                Result.failure(Exception("设置失败: ${response.statusDescription}"))
            }
        } else {
            val error = result.exceptionOrNull() ?: Exception("Unknown error")
            Napier.e("设置XXX错误", error, tag = TAG)
            Result.failure(error)
        }
    } catch (e: Exception) {
        Napier.e("设置XXX异常", e, tag = TAG)
        Result.failure(e)
    }
}
```

## 实现类模板（返回数据）

```kotlin
override suspend fun getXxx(): Result<Int> {
    return try {
        val request = GetXxxRequest(context)
        val result = executor.execute(request)

        if (result.isSuccess) {
            val response = result.getOrThrow()
            if (response.isSuccess) {
                Napier.d("获取XXX成功: ${response.value}", tag = TAG)
                Result.success(response.value)
            } else {
                Napier.w("获取XXX失败: ${response.statusDescription}", tag = TAG)
                Result.failure(Exception("获取失败: ${response.statusDescription}"))
            }
        } else {
            val error = result.exceptionOrNull() ?: Exception("Unknown error")
            Napier.e("获取XXX错误", error, tag = TAG)
            Result.failure(error)
        }
    } catch (e: Exception) {
        Napier.e("获取XXX异常", e, tag = TAG)
        Result.failure(e)
    }
}
```

## 返回复杂对象模板

```kotlin
override suspend fun getXxxInfo(): Result<XxxInfo> {
    return try {
        val request = GetXxxInfoRequest(context)
        val result = executor.execute(request)

        if (result.isSuccess) {
            val response = result.getOrThrow()
            if (response.isSuccess) {
                val info = XxxInfo(
                    field1 = response.field1,
                    field2 = response.field2,
                    field3 = response.field3
                )
                Napier.d("获取XXX信息成功: $info", tag = TAG)
                Result.success(info)
            } else {
                Napier.w("获取XXX信息失败: ${response.statusDescription}", tag = TAG)
                Result.failure(Exception("获取失败: ${response.statusDescription}"))
            }
        } else {
            val error = result.exceptionOrNull() ?: Exception("Unknown error")
            Napier.e("获取XXX信息错误", error, tag = TAG)
            Result.failure(error)
        }
    } catch (e: Exception) {
        Napier.e("获取XXX信息异常", e, tag = TAG)
        Result.failure(e)
    }
}

/**
 * XXX信息数据类
 */
data class XxxInfo(
    val field1: Int,
    val field2: String,
    val field3: Boolean
)
```

## 现有 Commands 文件参考

| 文件 | 用途 |
|------|------|
| `UserCommands.kt` | 用户管理（登录、注册、删除） |
| `LockControlCommands.kt` | 锁控制（开锁、反锁） |
| `ConfigCommands.kt` | 配置（时间、语言、静音等） |
| `SystemCommands.kt` | 系统信息（固件版本、SN等） |

## 注意事项
- 使用 `Napier` 记录日志，tag 使用 `TAG` 常量
- 异常必须捕获并返回 `Result.failure`
- 方法签名需添加 KDoc 注释说明参数范围
