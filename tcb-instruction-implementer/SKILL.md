---
name: tcb-instruction-implementer
description: 实现 TCB 蓝牙通讯指令。当用户要求实现 TCB 指令（如 REQ_XXX 格式）、添加 BLE 协议支持时使用。触发词："实现 TCB 指令"、"实现 REQ_XXX"、"添加 0xXX 指令"、"TCB 协议实现"。包含协议层、业务层、Registry 注册、UI 和 JsBridge 的完整实现流程。
---

# TCB 指令实现 Skill

专门用于实现 TCB (Transmission Control Block) 蓝牙通讯指令的标准化流程。

## 工作流程概览

```
1. 文档分析 → 2. 协议层 → 3. 业务层 → 4. Registry 注册 → 5. UI 层 → 6. JsBridge
```

## 第一步：文档分析（必须先执行）

### 1.1 查找指令文档
```
文档根目录: /Users/jiangjiwei/Code/Docs/xthing-docs-validation/docs/tcb/
├── TCB指令分类文档.md          # 先读取，确定指令分类
└── 指令文档/
    ├── 01-用户管理/
    ├── 02-锁控制/
    ├── 03-时间管理/
    └── ...                      # 按分类查找具体文档
```

### 1.2 必须提取的信息
- 指令码（REQ）和响应码（ACK）的十六进制值
- 请求数据包格式（字段偏移、长度、类型）
- 响应数据包格式（返回值解析）
- 参数取值范围和枚举值
- 特殊处理逻辑

### 1.3 文档不存在时
1. 在 `指令文档/` 目录搜索指令码
2. 询问用户是否有其他文档来源
3. **不要在没有文档时盲目实现**

## 第二步：协议层实现

**文件位置**: `shared-ble/src/commonMain/kotlin/com/anviz/multi/shared/ble/business/equip/fox/protocol/`

创建 `XxxProtocol.kt`，包含：
- `XxxRequest` 类：继承 `FoxTcbRequest<XxxResponse>`
- `XxxResponse` 类：实现 `TcbResponse` 接口

**详细模板**: 见 [references/protocol-template.md](references/protocol-template.md)

## 第三步：业务层集成

**文件位置**: `shared-ble/src/commonMain/kotlin/com/anviz/multi/shared/ble/business/equip/fox/commands/`

修改对应的 `XxxCommands.kt`：
- 接口中添加方法签名
- 实现类中添加具体逻辑

**详细模板**: 见 [references/business-template.md](references/business-template.md)

## 第四步：TcbCommandRegistry 注册

**文件位置**: `shared-biz/src/commonMain/kotlin/com/bin/chaos/shared_biz/protocol/tcb/commands/`

按指令分类选择文件：
| 分类 | 文件 |
|------|------|
| 系统/锁控制 | `SystemCommands.kt` |
| 时间管理 | `TimeCommands.kt` |
| 用户管理 | `UserCommands.kt` |
| WiFi 配置 | `WifiCommands.kt` |

**详细模板**: 见 [references/registry-template.md](references/registry-template.md)

## 第五步：UI 层集成

### 5.1 创建独立组件
**文件位置**: `composeApp/src/commonMain/kotlin/com/anviz/multi/bledemo/pages/connect/view/equip/fox/tab/component/`

创建 `CardXxx.kt`，包含：
- `XxxMenuItem` Composable 组件
- `performXxx` suspend 执行函数

### 5.2 在主文件中引用
在 `FoxActionMenuCard.kt` 中导入并使用组件

**详细模板**: 见 [references/ui-template.md](references/ui-template.md)

## 第六步：JsBridge 配置

**文件位置**: `composeApp/src/androidMain/assets/js/config.js`

在 `DEFAULT_TCB_COMMANDS` 数组中添加测试配置

**详细模板**: 见 [references/jsbridge-template.md](references/jsbridge-template.md)

---

## 重要规则

### 必须遵守
- 先读取文档再实现
- 使用 `TcbReq(command)` 直接创建请求，不修改 `TcbReq.kt`
- 必须在 Registry 注册（否则 JsBridge 报"指令未注册"）
- UI 组件独立文件，保持 `FoxActionMenuCard.kt` 简洁

### 禁止事项
- 不要创建单独的 ProtocolTest 测试文件
- 不要在没有文档时盲目实现
- 不要在主 UI 文件中写大量逻辑
- 不要自动提交 Git

## 命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 协议文件 | `XxxProtocol.kt` | `SetAutolockProtocol.kt` |
| UI 组件文件 | `CardXxx.kt` | `CardConfig.kt` |
| Composable | `XxxMenuItem` | `SetAutolockMenuItem` |
| 执行函数 | `performXxx` | `performSetAutolock` |
| Registry 指令名 | `REQ_XXX` | `REQ_SET_AUTOLOCK` |

## 输出格式

完成后输出：

```
### 完成总结

#### 从文档提取的信息：
- 文档路径: xxx
- 指令码/响应码: 0xXX/0xXX
- 数据包格式: xxx

#### 创建的文件：
- 协议层: `shared-ble/.../XxxProtocol.kt`
- UI组件: `component/CardXxx.kt`

#### 修改的文件：
- 业务层: `XxxCommands.kt` - 添加 xxx 方法
- Registry: `XxxCommands.kt` - 注册 REQ_XXX
- JsBridge: `config.js` - 添加测试配置
- 主UI: `FoxActionMenuCard.kt` - 引用组件

#### 测试方式：
- Native UI: 在 xxx 分组卡片中测试
- Web: 在 ble-demo.html TCB 批量测试区域
```
