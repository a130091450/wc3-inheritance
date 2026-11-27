# 可复制 payload 样板（源自 handbook §8–§9）

> 写入前提醒：参数用 `type_id`；函数用 `func_params`（扁平）；局部变量写**裸名**；
> 单次 payload 控制在 7.8KB 以内，长 JSON 分行缩进提交。

## A. 一个 If（then / else）

```json
{"category_index":C,"trigger_index":T,"eca_index":N,"name":"IfThenElseMultiple","parameters":[],
 "children":[
  {"type":"condition","group_id":0,"name":"OperatorCompareInteger","children":[],
   "parameters":[{"type_id":2,"type_name":"integer","value":"YDWEGetAnyTypeLocalVariable",
     "func_params":[{"type_id":3,"type_name":"scriptcode","value":"n"}]},
    {"type_id":0,"type_name":"ComparisonOperator","value":"OperatorEqual"},
    {"type_id":3,"type_name":"integer","value":"0"}]},
  {"type":"action","group_id":1,"name":"ReturnAction","children":[],"parameters":[]},
  {"type":"action","group_id":2,"name":"SetVariable","children":[],
   "parameters":[{"type_id":1,"type_name":"AnyGlobal","value":"标记变量"},
     {"type_id":3,"type_name":"integer","value":"0"}]}
 ]}
```

## B. 循环 + 取循环下标当参数

```json
{"name":"YDWEForLoopLocVarMultiple",
 "parameters":[{"type_id":3,"type_name":"scriptcode","value":"a"},
               {"type_id":3,"type_name":"integer","value":"1"},
               {"type_id":3,"type_name":"integer","value":"36"}],
 "children":[ /* 循环体 */ ]}
```

取下标：

```json
{"type_id":2,"type_name":"integer","value":"YDWEForLoopLocVarIndex",
 "func_params":[{"type_id":3,"type_name":"scriptcode","value":"a"}]}
```

## C. 帧事件注册（成对 + 回调极简 + 计时器干活）

```json
// 事件：TriggerRegisterTimerEventSingle(2.00)
// 动作：DzFrameSetScriptMultiple(GetLocalPlayer(), FrameEvent_Mouse_Enter, 命令栏按钮(2,0))
{"name":"DzFrameSetScriptMultiple","parameters":[
  {"type_id":2,"type_name":"player","value":"GetLocalPlayer","func_params":[]},
  {"type_id":0,"type_name":"frameevent","value":"FrameEvent_Mouse_Enter"},
  {"type_id":2,"type_name":"frame","value":"DzFrameGetCommandBarButton",
   "func_params":[{"type_id":3,"type_name":"integer","value":"2"},
                  {"type_id":3,"type_name":"integer","value":"0"}]}],
 "children":[
   // ★回调体只允许这类动作：写标记 / 打印
   {"type":"action","group_id":0,"name":"SetVariable","children":[],"parameters":[
     {"type_id":1,"type_name":"AnyGlobal","value":"交接变量"},
     {"type_id":3,"type_name":"integer","value":"0"}]}
 ]}
```

## D. 跨触发器调用（无参，最稳）

```json
{"name":"TriggerExecute","parameters":[{"type_id":1,"type_name":"trigger","value":"gg_trg_目标页"}]}
```

- 被调页第一句必须自己兜底：`如果 关键帧为空 → ReturnAction`。
- 带参版本（较脆，慎用）：`YDWEExecuteTriggerMultiple` + 子项赋值。

## E. 建帧 + 锚定链（父帧用全局变量形式！）

```json
{"name":"SetVariable",
 "parameters":[{"type_id":1,"type_name":"AnyGlobal","value":"F",
                "array_index":{"type_id":3,"type_name":"integer","value":"2"}},
   {"type_id":2,"type_name":"frame","value":"DzCreateFrameByTagName","func_params":[
     {"type_id":3,"type_name":"string","value":"BACKDROP"},
     {"type_id":3,"type_name":"string","value":"uizicon"},
     {"type_id":1,"type_name":"frame","value":"F",
      "array_index":{"type_id":3,"type_name":"integer","value":"0"}},
     {"type_id":3,"type_name":"string","value":""},
     {"type_id":3,"type_name":"integer","value":"0"}]}]}
```

```
贴图： DzFrameSetTexture(F[2], "UI\\Feedback\\Resources\\ResourceGold.blp", 0)
尺寸： DzFrameSetSize(F[2], 0.022, 0.022)
锚点： DzFrameSetPoint(F[2], FramePoints_BottomLeft, F[0], FramePoints_TopLeft, 0.006, 0.006)
```

## F. 字符串拼接 + 变色

```json
{"name":"YDWEOperatorString3","parameters":[
  {"type_id":3,"type_name":"string","value":"|cffffcc00第"},
  {"type_id":2,"type_name":"string","value":"I2S","func_params":[
    {"type_id":2,"type_name":"integer","value":"YDWEGetAnyTypeLocalVariable",
     "func_params":[{"type_id":3,"type_name":"scriptcode","value":"n"}]}]},
  {"type_id":3,"type_name":"string","value":"格|r"}]}
```

## 速查卡

- **流程**：列页清单核对索引 → 小步写 → 语法校验 → **整页回读** → 让用户 **Ctrl+S**。
- **参数**：`type_id`（0 预设 / 1 全局变量 / 2 函数+`func_params` / 3 字面量、"scriptcode"=局部变量裸名）。
- **容器**：`IfThenElseMultiple`（0 条件 / 1 Then / 2 Else）、`YDWEForLoopLocVarMultiple`、`YDWEExecuteTriggerMultiple`、`Or/AndMultiple`。
- **工具**：单次 payload ≤ 7.8KB；带 children 的容器别用"一次性建页"；删条目从后往前；改容器内部就整块重提。
- **自绘 UI**：模板 ≠ 贴图；父帧用全局变量；背景先建；后建在上层；子帧随父显隐；外框挂最上/最下的锚点自适应。
- **帧事件**：一帧一事件只注册一次；重复的要**删**不要禁用；回调**报错一次 → 整个分发永久哑掉**；回调只写标记，重活放计时器/被调页。
- **归因**：卖/买/选中 ✓；施法、发命令 ✗；`GetLocalPlayer` 猜 ✗。
- **中文/文本**：先塞字符串局部变量；`|n` 在系统消息里不换行；颜色码要有 `|r`。


---

# 本轮真机验证过的补充样板（2026-11）

## G. 选英雄对话框（完整可跑）

```json
// ① 建对话框（放在 0.1s 定时器里，不要放"地图初始化"）
{"name":"SetVariable","parameters":[
  {"type_id":1,"type_name":"dialog","value":"HeroDialog"},
  {"type_id":2,"type_name":"dialog","value":"DialogCreate","func_params":[]}]}

// ② 加按钮 + 立刻把"最后创建的按钮"存进变量（三个按钮重复三遍）
{"name":"DialogAddButtonBJ","parameters":[
  {"type_id":1,"type_name":"dialog","value":"HeroDialog"},
  {"type_id":3,"type_name":"string","value":"|cffc0c0c0力量|r · 山丘之王"}]}
{"name":"SetVariable","parameters":[
  {"type_id":1,"type_name":"button","value":"BtnP"},
  {"type_id":2,"type_name":"button","value":"GetLastCreatedButtonBJ","func_params":[]}]}

// ③ 显示
{"name":"DialogDisplay","parameters":[
  {"type_id":0,"type_name":"player","value":"Player00"},
  {"type_id":1,"type_name":"dialog","value":"HeroDialog"},
  {"type_id":0,"type_name":"showhideoption","value":"ShowHideShow"}]}

// ④ 🔴 关键：动态注册事件（否则静态注册时 dialog 还是 null，点了永远没反应）
{"name":"CustomScriptCode","parameters":[
  {"type_id":3,"type_name":"scriptcode",
   "value":"call TriggerRegisterDialogEvent(gg_trg_Demo_Pick, udg_HeroDialog)"}]}
```

回调页（**不要**再加静态对话框事件）：

```json
{"name":"IfThenElseMultiple","parameters":[],"children":[
 {"type":"condition","group_id":0,"name":"OperatorCompareUnit","parameters":[
   {"type_id":2,"type_name":"unit","value":"GetClickedButtonBJ","func_params":[]},
   {"type_id":0,"type_name":"EqualNotEqualOperator","value":"OperatorEqualENE"},
   {"type_id":1,"type_name":"button","value":"BtnA"}]},
 {"type":"action","group_id":1,"name":"SetVariable","parameters":[
   {"type_id":1,"type_name":"unitcode","value":"HeroType"},
   {"type_id":3,"type_name":"unitcode","value":"Obla"}]}]}
```

> ⚠️ 判据提醒：WC3 **对话框点完会自动隐藏**，别拿"对话框消失"当事件触发的证据——要在回调里打印标记。

## H. 按键事件 + 死亡复活分支

```json
// F2 / F3（113 = VK_F2，114 = VK_F3）
{"name":"DzTriggerRegisterKeyEventTrg","parameters":[
  {"type_id":0,"type_name":"gamekeyaction","value":"GameKeyAction_Press"},
  {"type_id":0,"type_name":"gamekey","value":"GameKey_F2"}]}
```

```json
// 活则传送 / 死则原地复活（F3 回城用）
{"name":"IfThenElseMultiple","parameters":[],"children":[
 {"type":"condition","group_id":0,"name":"OperatorCompareBoolean","parameters":[
   {"type_id":2,"type_name":"boolean","value":"IsUnitAliveBJ","func_params":[
     {"type_id":1,"type_name":"unit","value":"Hero"}]},
   {"type_id":0,"type_name":"EqualNotEqualOperator","value":"OperatorEqualENE"},
   {"type_id":3,"type_name":"boolean","value":"true"}]},
 {"type":"action","group_id":1,"name":"DzSetUnitXY","parameters":[
   {"type_id":1,"type_name":"unit","value":"Hero"},
   {"type_id":3,"type_name":"real","value":"-2304"},
   {"type_id":3,"type_name":"real","value":"-1856"}]},
 {"type":"action","group_id":2,"name":"ReviveHero","parameters":[
   {"type_id":1,"type_name":"unit","value":"Hero"},
   {"type_id":3,"type_name":"real","value":"-2304"},
   {"type_id":3,"type_name":"real","value":"-1856"},
   {"type_id":0,"type_name":"showhideoption","value":"ShowHideShow"}]}]}
```

## I. 自测触发器（无外部输入也能验收）

```json
// 每 3 秒把关键数值打到屏幕，任何时刻截图都能读到
{"name":"TriggerRegisterTimerEventPeriodic","parameters":[{"type_id":3,"type_name":"real","value":"3.0"}]}

// 动作序列：取数量 → I2S → 拼字符串 → 显示
{"name":"SetVariable","parameters":[
  {"type_id":1,"type_name":"group","value":"TempGroup"},
  {"type_id":2,"type_name":"group","value":"GetUnitsInRectAll","func_params":[
    {"type_id":1,"type_name":"rect","value":"gg_rct_TrainArea"}]}]}
{"name":"SetVariable","parameters":[
  {"type_id":1,"type_name":"integer","value":"TempInt"},
  {"type_id":2,"type_name":"integer","value":"CountUnitsInGroup","func_params":[
    {"type_id":1,"type_name":"group","value":"TempGroup"}]}]}
{"name":"SetVariable","parameters":[
  {"type_id":1,"type_name":"string","value":"Msg"},
  {"type_id":2,"type_name":"string","value":"I2S","func_params":[
    {"type_id":1,"type_name":"integer","value":"TempInt"}]}]}
{"name":"DisplayTextToPlayer","parameters":[
  {"type_id":0,"type_name":"player","value":"Player00"},
  {"type_id":3,"type_name":"real","value":"0"},
  {"type_id":3,"type_name":"real","value":"0"},
  {"type_id":2,"type_name":"string","value":"YDWEOperatorString3","func_params":[
    {"type_id":3,"type_name":"string","value":"STAT SPAWN="},
    {"type_id":1,"type_name":"string","value":"Msg"},
    {"type_id":3,"type_name":"string","value":""}]}]}
```
