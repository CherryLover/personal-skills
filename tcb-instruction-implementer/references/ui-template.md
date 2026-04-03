# UI 层模板

## 文件位置

### 组件文件
`composeApp/src/commonMain/kotlin/com/anviz/multi/bledemo/pages/connect/view/equip/fox/tab/component/CardXxx.kt`

### 主文件
`composeApp/src/commonMain/kotlin/com/anviz/multi/bledemo/pages/connect/view/equip/fox/tab/FoxActionMenuCard.kt`

## 独立组件模板（CardXxx.kt）

```kotlin
package com.anviz.multi.bledemo.pages.connect.view.equip.fox.tab.component

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings  // 选择合适的图标
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.anviz.multi.shared.ble.business.equip.fox.FoxBluetoothOperatorImpl
import io.github.aakira.napier.Napier
import kotlinx.coroutines.launch

/**
 * XXX操作菜单项
 */
@Composable
fun XxxMenuItem(
    operator: FoxBluetoothOperatorImpl,
    modifier: Modifier = Modifier
) {
    var isLoading by remember { mutableStateOf(false) }
    var result by remember { mutableStateOf<ActionResult?>(null) }
    val coroutineScope = rememberCoroutineScope()

    Column(modifier = modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 左侧：图标和功能说明
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.weight(1f)
            ) {
                Icon(
                    imageVector = Icons.Default.Settings,
                    contentDescription = "XXX操作",
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(20.dp)
                )

                Column {
                    Text(
                        text = "XXX操作",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = "操作描述 (0xXX)",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // 右侧：执行按钮
            Button(
                onClick = {
                    coroutineScope.launch {
                        isLoading = true
                        result = null
                        try {
                            result = performXxx(operator)
                        } catch (e: Exception) {
                            result = ActionResult.Error("操作失败: ${e.message}")
                        } finally {
                            isLoading = false
                        }
                    }
                },
                enabled = !isLoading,
                modifier = Modifier.height(36.dp)
            ) {
                if (isLoading) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(6.dp)
                    ) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(14.dp),
                            strokeWidth = 2.dp
                        )
                        Text("执行中", style = MaterialTheme.typography.bodySmall)
                    }
                } else {
                    Text("执行", style = MaterialTheme.typography.bodyMedium)
                }
            }
        }

        // 结果显示
        result?.let { actionResult ->
            Spacer(modifier = Modifier.height(8.dp))
            ResultDisplay(actionResult)
        }
    }
}

/**
 * 执行XXX操作
 */
suspend fun performXxx(operator: FoxBluetoothOperatorImpl): ActionResult {
    Napier.d("开始执行XXX操作", tag = "FoxActionMenu")
    return try {
        val result = operator.config.getXxx()  // 或 setXxx()

        if (result.isSuccess) {
            val value = result.getOrThrow()
            Napier.d("XXX操作成功: $value", tag = "FoxActionMenu")
            ActionResult.Success("操作成功: $value")
        } else {
            val error = result.exceptionOrNull()?.message ?: "操作失败"
            Napier.w("XXX操作失败: $error", tag = "FoxActionMenu")
            ActionResult.Error(error)
        }
    } catch (e: Exception) {
        Napier.e("XXX操作异常: ${e.message}", tag = "FoxActionMenu")
        ActionResult.Error("操作异常: ${e.message}")
    }
}
```

## 带参数输入的组件模板

```kotlin
@Composable
fun SetXxxMenuItem(
    operator: FoxBluetoothOperatorImpl,
    modifier: Modifier = Modifier
) {
    var isLoading by remember { mutableStateOf(false) }
    var result by remember { mutableStateOf<ActionResult?>(null) }
    var inputValue by remember { mutableStateOf("") }
    val coroutineScope = rememberCoroutineScope()

    Column(modifier = modifier.fillMaxWidth()) {
        // 输入框
        OutlinedTextField(
            value = inputValue,
            onValueChange = { inputValue = it },
            label = { Text("参数值") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        Spacer(modifier = Modifier.height(8.dp))

        // 执行按钮
        Button(
            onClick = {
                coroutineScope.launch {
                    isLoading = true
                    result = null
                    try {
                        val value = inputValue.toIntOrNull() ?: 0
                        result = performSetXxx(operator, value)
                    } catch (e: Exception) {
                        result = ActionResult.Error("操作失败: ${e.message}")
                    } finally {
                        isLoading = false
                    }
                }
            },
            enabled = !isLoading && inputValue.isNotBlank()
        ) {
            Text(if (isLoading) "设置中..." else "设置")
        }

        // 结果显示
        result?.let { ResultDisplay(it) }
    }
}
```

## 在主文件中引用

```kotlin
// FoxActionMenuCard.kt 中

// 1. 导入组件
import com.anviz.multi.bledemo.pages.connect.view.equip.fox.tab.component.XxxMenuItem

// 2. 在对应分组中使用
@Composable
fun ConfigCommandGroup(
    operator: FoxBluetoothOperatorImpl,
    modifier: Modifier = Modifier
) {
    Card(/*...*/) {
        Column(/*...*/) {
            Text(text = "配置类指令", /*...*/)

            Spacer(modifier = Modifier.height(12.dp))

            // 使用独立组件
            XxxMenuItem(operator = operator)

            HorizontalDivider(/*...*/)

            // 其他菜单项...
        }
    }
}
```

## 常用图标

```kotlin
Icons.Default.Settings      // 设置
Icons.Default.Lock          // 锁
Icons.Default.LockOpen      // 开锁
Icons.Default.Person        // 用户
Icons.Default.Schedule      // 时间
Icons.Default.Wifi          // WiFi
Icons.Default.Info          // 信息
Icons.Default.VolumeOff     // 静音
Icons.Default.Language      // 语言
```

## 注意事项
- 组件独立为单独文件，保持 `FoxActionMenuCard.kt` 简洁
- 使用 `ActionResult` 密封类统一处理结果展示
- 必须有加载状态和错误处理
- 使用 `Napier` 记录日志
