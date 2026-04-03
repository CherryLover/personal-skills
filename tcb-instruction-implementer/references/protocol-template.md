# 协议层模板

## 文件位置
`shared-ble/src/commonMain/kotlin/com/anviz/multi/shared/ble/business/equip/fox/protocol/XxxProtocol.kt`

## 基础模板（无参数请求，简单响应）

```kotlin
package com.anviz.multi.shared.ble.business.equip.fox.protocol

import com.anviz.multi.shared.ble.business.equip.fox.model.FoxDeviceContext
import com.anviz.multi.shared.ble.business.equip.fox.protocol.base.FoxTcbRequest
import com.anviz.multi.shared.ble.business.equip.fox.protocol.base.TcbResponse
import com.anviz.multi.shared.ble.business.equip.fox.tcb.TcbAck
import com.anviz.multi.shared.ble.business.equip.fox.tcb.TcbReq
import com.anviz.multi.shared.ble.business.equip.fox.tcb.TcbBase

/**
 * XXX指令请求 (0xXX)
 */
class XxxRequest(
    context: FoxDeviceContext
) : FoxTcbRequest<XxxResponse>(context) {

    override val command = TcbBase.CommCmd.REQ_XXX

    override fun buildStandardRequest(): TcbReq {
        return TcbReq(command)
    }

    override fun parseResponse(ack: TcbAck): XxxResponse {
        return XxxResponse(
            isSuccess = ack.isSuccess(),
            statusCode = ack.getRetStatus().toInt(),
            statusDescription = ack.getStatusDescription()
        )
    }
}

/**
 * XXX指令响应
 */
data class XxxResponse(
    override val isSuccess: Boolean,
    override val statusCode: Int,
    override val statusDescription: String
) : TcbResponse
```

## 带参数请求模板

```kotlin
class SetXxxRequest(
    context: FoxDeviceContext,
    private val paramValue: Int  // 根据文档定义参数
) : FoxTcbRequest<SetXxxResponse>(context) {

    override val command = TcbBase.CommCmd.REQ_SET_XXX

    override fun buildStandardRequest(): TcbReq {
        return TcbReq(command).apply {
            // 根据文档的数据包格式添加参数
            addByte(paramValue.toByte())           // 1字节参数
            // addShort(paramValue.toShort())      // 2字节参数
            // addInt(paramValue)                   // 4字节参数
            // addBytes(byteArrayOf(...))          // 字节数组
        }
    }

    override fun parseResponse(ack: TcbAck): SetXxxResponse {
        return SetXxxResponse(
            isSuccess = ack.isSuccess(),
            statusCode = ack.getRetStatus().toInt(),
            statusDescription = ack.getStatusDescription()
        )
    }
}
```

## 带数据返回的响应模板

```kotlin
class GetXxxRequest(
    context: FoxDeviceContext
) : FoxTcbRequest<GetXxxResponse>(context) {

    override val command = TcbBase.CommCmd.REQ_GET_XXX

    override fun buildStandardRequest(): TcbReq {
        return TcbReq(command)
    }

    override fun parseResponse(ack: TcbAck): GetXxxResponse {
        val data = ack.getData()
        return GetXxxResponse(
            isSuccess = ack.isSuccess(),
            statusCode = ack.getRetStatus().toInt(),
            statusDescription = ack.getStatusDescription(),
            // 根据文档解析返回数据
            value1 = data.getOrNull(0)?.toInt() ?: 0,      // 偏移0，1字节
            value2 = data.getShortAt(1),                    // 偏移1，2字节
            value3 = data.getIntAt(3)                       // 偏移3，4字节
        )
    }
}

data class GetXxxResponse(
    override val isSuccess: Boolean,
    override val statusCode: Int,
    override val statusDescription: String,
    val value1: Int,
    val value2: Int,
    val value3: Int
) : TcbResponse
```

## 常用数据解析方法

```kotlin
// 从 ByteArray 解析
val data = ack.getData()

// 单字节
val byte = data[offset].toInt() and 0xFF

// 双字节（小端序）
val short = ((data[offset + 1].toInt() and 0xFF) shl 8) or (data[offset].toInt() and 0xFF)

// 四字节（小端序）
val int = ((data[offset + 3].toInt() and 0xFF) shl 24) or
          ((data[offset + 2].toInt() and 0xFF) shl 16) or
          ((data[offset + 1].toInt() and 0xFF) shl 8) or
          (data[offset].toInt() and 0xFF)

// 字符串（定长）
val str = data.copyOfRange(offset, offset + length).decodeToString().trimEnd('\u0000')
```

## 注意事项
- 直接使用 `TcbReq(command)` 创建请求，不要修改 `TcbReq.kt`
- 参数添加顺序必须与文档一致
- 响应解析偏移必须与文档一致
- 注意字节序（通常是小端序）
