---
name: wc3-ydwe-gui
description: >
  魔兽争霸3（War3 / .w3x / YDWE / 逆天编辑器 / KK 系）地图 GUI/ECA 触发器编写与改图手册。
  覆盖：加事件/条件/动作、If/循环容器、参数 JSON（type_id / func_params）、全局与局部变量、
  数据表设计、DZAPI 自绘 UI 建帧与帧事件、物编自定义对象，以及"代码全对但游戏里无效"的静默失效排查。

  ALWAYS use this skill when 用户提到：魔兽3、魔兽争霸3、war3、w3x、YDWE、逆天编辑器、kkwe、kkwe-mcp、
  w3x2lni、GUI触发器、触发器、ECA、事件、条件、动作、局部变量、数据表、哈希表、自绘UI、
  DzCreateFrame、帧事件、命令栏按钮、物编、自定义单位、改图、加触发器、改触发器、触发器没反应。

  ALSO use it whenever this session's tools include any kkwe-mcp tool — ping / get_map_info / list_categories /
  list_triggers / get_trigger / list_variables / add_action / add_condition / add_event / replace_eca /
  validate_triggers / save_map 等 —— 哪怕用户没提技能名，也要先加载本技能再动手写触发器。

  本技能是魔兽3 .w3x 体系，不要与 Y3 引擎的 y3-* 技能混用。
---

# 魔兽3 逆天 GUI 触发器手册（操作版）

权威细节源：`references/handbook.md`（全文，含踩坑原委与实测结论）。
需要抄 JSON 结构时读 `references/payloads.md`（If / 循环 / 帧事件 / 建帧 / 字符串拼接样板）。
下面是与"动手"直接相关的部分，正常情况下够用；拿不准的条目回 handbook 查原文。

## 0. 环境适配（先做这一步，别假设工具在）

- 本机 kkwe-mcp **已配置**：SSE `http://127.0.0.1:19816/sse`。它由编辑器内的 KKWE 插件启动 →
  **前提是 WorldEdit / 逆天编辑器已打开并加载地图，且插件已启用**。
- 开工第一步 `ping`，回 `pong` 才动手。连不上按顺序查：编辑器进程在不在 →
  `netstat -ano | findstr 19816` 有无监听 → 插件是否启用 → 重开 ZCode 会话（连接失败的 MCP 不会在当前会话里复活）。
- MCP 工具清单是**会话开始时**注入的：当前会话看不到 kkwe 工具，说明这次会话拿不到，别硬试；
  要么让用户重开会话，要么走解包路线（handbook §1.1②）。
- 工具可用性不确定时先 `list_trigger_functions(section,search)` 查名字和参数签名，**不要凭记忆写动作名**。
- 本机同时配了 Y3 系服务（`y3-helper` / `y3editor` / `y3runtime`）——那是另一个引擎的工作流，**别混用**。

## 1. 三条铁律（能避开 80% 返工）

1. **改任何一页之前，重新列页面/变量清单核对索引。** 新建页面插到 `index 0`，既有页索引整体后移（曾把另一页覆盖成整块代码）。
2. **参数写 `type_id`（不是 `type`），函数参数写 `func_params`（不是 `params`）。** 写错是静默失败：校验通过、参数变成 `{"type_id":-1,"value":""}`，只有回读能发现。
3. **自建 UI 不显示，按固定顺序查**：父帧写法 → 贴图/资源路径 → 尺寸/锚点 → 图层顺序。父帧写成"取值函数"会得到空父帧：帧建成功、属性全能写、永远不渲染。

## 2. 标准工作流

1. 摸底：`get_map_info` → `list_categories` + `list_triggers`（**含禁用页**）→ `list_variables` → `list_regions` / `list_units` → 挑核心玩法页 `get_trigger` 全文，从数据表键名反推业务模型。
2. 小步写：一次一小块 → `validate_triggers`（**只验语法**）→ `get_trigger` **整页回读核对**。
3. 每完成一小块让用户 **Ctrl+S**；编辑器卡死时让用户连点几次 Ctrl+S。写操作只进内存，进程一死全丢。
   ⚠️ **MCP 的 `save_map` 不编译脚本**：地图里会留下 vJass 源码（`#include`），重启编辑器后测试会直接崩
   （见 §11 第 13 条）。所以"让用户 Ctrl+S"不只是保存，**还是把脚本编译成纯 JASS 的唯一可靠方式**。
4. 设计与清单同步落本地文档 —— 编辑器崩了，文档是唯一重建依据。
5. **不主动替用户保存。**
6. 关键改动"写 → 回读 → 给人看"三步走；**"工具返回成功" ≠ "改动生效"**。

## 3. 数据模型速查

**ECA 树**：一页 = 事件 + 条件 + 动作；顶层 `group_id = -1`；容器内 `IfThenElseMultiple` 条件 0 / Then 1 / Else 2，单块容器为 0；子项同一 `children` 数组，**顺序即语义**；`eca_count` 只统计顶层。

**参数五种形态**（写入时）：

| 形态 | 写法 |
|---|---|
| 预设 | `{"type_id":0,"type_name":"<类型>","value":"<预设名>"}` |
| 全局变量 | `{"type_id":1,"type_name":"<类型>","value":"<变量名>","array_index":{"type_id":3,"type_name":"integer","value":"0"}}` |
| 函数调用 | `{"type_id":2,"type_name":"<返回类型>","value":"<函数名>","func_params":[...]}` |
| 字面量 | `{"type_id":3,"type_name":"integer\|real\|boolean\|string","value":"..."}`（布尔也用 3 + `"true"`） |
| 局部变量作参数 | `{"type_id":3,"type_name":"scriptcode","value":"<裸名>"}` |

- 读写不对称：读出来是 `func_call` + `params`，写进去要 `name` + `func_params`，**别照读出的结构回写**。
- `func_params` 必须扁平 `[a,b,c]`；嵌套 `func_call` 会丢参数 → 先存中间变量再引用（"参数里还能不能再看见一个函数调用？能 → 危险"）。

**全局 vs 局部是两套写法**：要全局 `F[0]` → `type_id:1` + 变量名 + `array_index`；要局部 D → 作参数用 `type_id:3` + `scriptcode` + 裸名，读值用 `YDWEGetAnyTypeLocalVariable`。**绝不能把"取局部变量的函数"当全局变量用**（空父帧事故的根源）。

**局部变量裸名**：存储里一律写裸名（`ls` / `q`），`loc_` / `loop_` 是编辑器加的前缀；照编辑器显示写会变成 `loc_loc_ls`。自查项都应为 0：`常量: loc_` / `常量: loop_` / 脚本里 `ydul_loop_`。

**中文文本**：先 `设置 字符串局部变量 = "中文"`，再把变量传给"显示文本信息"；`type_name:"StringExt"` 会把正文塞进字符串表变 `TRIGSTR_NNN`。`|n` 在系统消息里不换行 → 多行明细就多次调用。颜色码 `|cffXXXXXX ... |r` 必须收尾。

## 4. 工具层硬规律（踩过的）

| 现象 | 真因 / 做法 |
|---|---|
| JSON 解析报错（position N） | 单次 payload ≳7.8KB 被截断 → 长 JSON 分行缩进，超长拆多次或拆平 |
| 容器里动作蒸发 | `create_full_trigger` 的 `children` 会丢 → 只用来建"事件 + 顶层平铺动作"，容器建完再单条填 |
| 改 A 页改坏 B 页 | 新页插 index 0 → 每次改页前重列清单核对索引 |
| 改不了容器内部一条 | 嵌套节点无法单独定位 → 整个容器（含全部子节点）重新提交 |
| 名字莫名多个 " 001" | 先建了 `gg_trg_xxx` 变量再建同名触发器 → 顺序反：先触发器后变量 |
| 跨触发器引用不到 | 需先建 `gg_trg_<sanitize 名>`（trigger 型）；页面改名后变量名会变 |
| 反斜杠变双杠 | 原文写 `\\` = 存 1 个 |
| 删条后索引乱 | `remove_eca` 后索引前移 → **从后往前删** |
| 想插到中间 | `add_action` 只能追加末尾 → `add_action` + `reorder_eca`，或整块 `replace_eca` |
| 参数渲染成 `[typename01_integer]` | 用了 `type` 而非 `type_id` |
| 字符串塞进 unitcode/abilcode 报错 | 套转换函数（如 `YDWES2UnitId`），光改 `type_name` 不管用 |
| `create_full_trigger` 报 Unknown function | 它的 actions 校验函数名；`add_action` 的 children **不校验**（写错静默通过） |
| 物编面板空白 | 界面故障≠数据丢失 → 先保存再重启编辑器 |
| 新建自定义单位物编看不到 | 必须**以标准 SLK 单位为模板**（不能以另一个自定义单位为基底），字段显式写全 |

## 5. 自绘 UI（DZAPI 系）

- 建帧三步：`DzLoadToc`（一次即可）→ `DzCreateFrameByTagName(标签, 唯一名, 父帧, 模板名, 0)` → `SetPoint/SetSize/SetText/SetTexture/Show`。
  **第 4 个参数是 fdf 模板不是贴图**；贴图用 `DzFrameSetTexture(帧,"路径.blp",0)`；空模板 = 默认字体（中文正常）。
- `BACKDROP` 必须显式 `DzFrameSetSize`；`TEXT` 可宽 0.2、高 0 让高度随文字自适应换行。
- **后创建的在上层** → 背景/底图先建，文字/图标后建。
- 锚定链：横排元素用"第 2 个左下 ↔ 第 1 个右下"串联；外框左上挂最上元素左上、右下挂最下元素右下（留 0.012）；锚定目标必须**已创建**。
- 子帧随父帧显隐，但不改变父帧尺寸 → 要包住子帧得靠外框挂锚点。
- 坐标原点左下，整屏约 0.8 × 0.6（`y=0.46` 就出屏）；锚点枚举 `0=左上 1=顶 2=右上 3=左 4=中心 5=右 6=左下 7=底 8=右下`。

## 6. 帧事件——最血泪的一段

```
DzFrameSetScriptMultiple(GetLocalPlayer(), FrameEvent_Mouse_Enter, 按钮帧)
DzFrameSetScriptMultiple(GetLocalPlayer(), FrameEvent_Mouse_Leave, 按钮帧)   // 成对
DzFrameSetScriptMultiple(GetLocalPlayer(), FrameEvent_..._Pressed, 按钮帧)
```
回调里取事件帧/玩家用 `DzGetTriggerUIEventFrame()` / `DzGetTriggerUIEventPlayer()`（无参），不要反推。

1. **同一帧 + 同一事件只能注册一次**：先注册的占住槽位，后面的静默忽略（不覆盖、不追加、不报错）。
2. **"禁用"≠删除**：被禁用的注册仍生成调用，但回调体是空函数 → 占槽把一个"什么都不做"的空函数注册上去。重复的注册要**删**。
3. **回调体不能有任何会报错的动作**：报错一次，该帧整个事件分发**永久哑掉**。安全写法=回调只写全局标记/打印，取数拼字动 UI 放到计时器线程或被调触发器里；**被调触发器第一句自己判空兜底**。

其他：帧句柄每局都变，不能写死；`DzGetMouseFocus` / `DzFrameGetChild` 实测常取不到；"这个按钮是第几个"用 `SaveAnyTypeDataByUserData` 反查；命令栏按钮 `DzFrameGetCommandBarButton(行,列)` 0 基且行列顺序与直觉常相反，**改前先让用户确认格子**。

## 7. 交互与归因（省掉一整类难题）

| 通道 | 能归因"谁做的" | 说明 |
|---|---|---|
| 商店出售单位 / 购买物品 | ✅ | 引擎给买出来的东西打购买者身份；触发单位=商店 |
| 按玩家注册「单位被选中」 | ✅ | 触发玩家=选中者 |
| 施法事件 | ❌ | 触发玩家恒为拥有者 |
| 「发布命令」事件 | ❌ 多数封装 | 各版本不一致，必须让用户实测一次 |
| `GetLocalPlayer()` 猜 | ❌❌❌ | 本地信息进同步逻辑 → 不同步/掉线 |

- 优先找"引擎主动携带身份"的事件（购买/拾取/选择），不要从命令/施法反推。
- 固有限制要跟用户明说：两玩家同时选中同一单位，谁按的键判不出来。
- 能拆成"每玩家自己的单位"就拆；几十个可点选对象**不要按"对象数 × 玩家数"铺代理单位**，用"单位被选中"或"每玩家 1 个代理 + 目标型技能"，公共设施用"商店 + 出售单位"。
- 玩家索引 1 基还是 0 基**必须实测**（写探针循环显示"序号 → 玩家名"），绝不按语言惯例推断。
- 在线判定要两条配合：控制器=用户 + 游戏状态=正在游戏；单用"数值 > 0"不行。
- 守卫式写法优先于标记变量式："不满足就走人"；但提前返回会跳过其后所有动作（含清理）。**除法必须守卫**，整数除零会崩线程。

## 8. 排障

1. **对照实验隔离变量**（自绘 UI 不显示 → 把贴图换成图里一定存在的那张，一次区分"路径不存在"还是"帧不渲染"）。
2. 按二分清单顺序查，不要跳：UI = 父帧 → 资源 → 尺寸/锚点 → 图层；事件 = 注册了几次 → 回调是否可能报错 → 被调页是否兜底。
3. 建"最小复现页"做 A/B（只差一个变量的两条动作），比在复杂页里猜快十倍。
4. **看编译产物**：把页转成 JASS 或解包 `war3map.j`，"两条注册只活一条""回调体是空函数"只有这里看得见。
5. 要证据：用户给"一句话现象 + 截图"；自己下结论也附依据（哪条实测 / 哪份编译产物）。

## 9. 解包路线（插件不可用时）

`w2l.exe` lni 解包 → 改 `trigger\` 下 LML + `map\war3map.j` → obj 回包。
**铁律：两层必须同改**——回包工具不重编译 `war3map.j`，只改 LML 会"编辑器里新逻辑、游戏里老代码"。
触发器文本靠缩进表达层级；`If/Else` 是两个并列的动作块；局部变量存裸名。
验收：回包日志 `0 个错误` + 反向解包逐文件比 size+MD5（整体 MD5 不可作判据，且"回包成功"可能是假成功）。

## 10. 沟通规范

- 中文、结论先行，表格/清单展开；每个发现落到本地文档。
- 一轮做一件事、小步交付，明确说"下一步需要你做什么（保存 / 实测 / 截图）"。
- 报 bug 前自问："这是按语言惯例推断的，还是代码本身自相矛盾？"只有后者值得报。
- 每轮回头做减法（用户会核对改动行数），先给"删了什么"。
- 明确说"我无法在本机实测游戏"，请用户在编辑器/游戏里确认；交付"修复清单 + 关键结论 + 待拍板项"，越短越好。
- 用户用编辑器的读法描述现象（"当游戏逝去 1.00 秒"=定时器事件、"按钮 (2,0)"=命令栏行列），照他的读法理解，不要先翻译成脚本术语再反推。

## 11. 实测补充（2026-11 testmap Demo）

1. **ZCode 本会话 MCP 连接失败时，可以自建 SSE 客户端直连**：编辑器 Welcome 行会打印
   `KKWE MCP Tool Enabled, Listen on: http://127.0.0.1:19816`。协议 = MCP over SSE
   （GET `/sse` 拿 endpoint → POST `/messages?session_id=…` → 响应回 SSE）。本技能 `scripts/kkwe_client.py` 即实现（工作区也常放一份到 `tools/`）。
2. **算术函数（名字是一个空格 `" "`）里的 scriptcode 必须自己写 `udg_` 前缀**：
   写 `"Wave + 1"` 会原样编译成 `set udg_Wave = Wave + 1` → 未定义变量 → **整图编译失败**。正确写法 `"udg_Wave + 1"`。
3. **中文写进 StringExt 参数会自动进字符串表**（编辑器里显示 `TRIGSTR_NNN`），但编译产物是正确中文，
   功能不受影响；`list_trigger_strings` 能查到。不必强行改成局部变量。
4. **连续大量写入会把编辑器写崩**（实测两次 `ConnectionReset` + 进程消失）。对策：**每建完一页就 `save_map`**，
   逐条加动作时也是"加一条存一次"；崩后用 `list_triggers` 判断建到哪，续建即可。
5. **崩溃后重开编辑器**：`KKWE.exe` 不接受命令行地图路径，要用 `Ctrl+O` → 文件对话框 → 文件名框输入路径 → 打开。
6. **`test_map()` 能起游戏**；魔兽是 DirectDraw 表面，**Computer Use 截不到图、发不了按键**
   （`invalid_target` / `app_ref did not resolve` / `frame_id expired`）→ 改用下面第 10 条的
   PowerShell 注入方案真机验收；纯静态核对则用 `get_trigger` 回读 + `w2l lni` 解包看 `war3map.j`。
7. **`w2l.exe lni <map> <out>` 解包后可读 `map/war3map.j`** —— 不依赖编辑器就能核对最终脚本，
   是"写 → 回读 → 给人看"里"给人看"的最快形式。


8. **对话框事件的静态注册是空指针陷阱**：`TriggerRegisterDialogEventBJ(对话变量)` 在**地图初始化**时求值，
   而对话框通常是定时器里才 `DialogCreate` → 注册到 null → **点按钮永远不触发**（且没有任何报错）。
   ✅ 正解：`Demo_Init` 末尾加 `CustomScriptCode`：
   `call TriggerRegisterDialogEvent(gg_trg_Demo_Pick, udg_HeroDialog)`。
9. **WC3 对话框被点击后会自动隐藏** → **不能**用"对话框消失"判断事件是否触发（这是本轮误判过的坑）。
   要判断是否触发，只能在回调里打印标记。
10. **可以真机跑游戏做验收**（CUA 对魔兽窗口无效时）：
    - 截图：PowerShell `Graphics.CopyFromScreen`（CUA 捕获 DirectDraw 会 `invalid_target`）
    - 鼠标：`mouse_event`（LButton down/up）→ 能点游戏内 UI
    - 键盘：`SendInput` 会被 Raw Input 挡掉；改用 `PostMessage(hwnd, WM_KEYDOWN/WM_KEYUP, VK, 0)` 才生效
      （F2=0x71、F3=0x72、Enter=0x0D）
    - 单机 WC3 **失焦即暂停**：截图/注入前先 `SetForegroundWindow`，否则定时器不动、现象像"触发全失效"
11. **自测触发器模式**（无需外部输入即可验收）：加一组临时页，用计时器自动模拟"选人→传送→刷怪→击杀"，
   把 PASS/FAIL 与关键数值 `DisplayTextToPlayer` 打到屏幕（每 3 秒重复一遍，避免截图错过），跑完删掉。
12. **`action_count` 统计的是 ECA 总数（含事件）**，回读核对时别只按 action 数算。
13. 🔴 **MCP `save_map` ≠ 编辑器 Ctrl+S（最贵的坑，会让你以为图坏了）**：
    - `save_map` 只写触发器数据 + **未经编译的 vJass 源码**（`war3map.j` 约 346 行，开头是
      `#define USE_BJ_ANTI_LEAK` / `#include <YDTrigger/...>`），文件 ~21KB。
    - 编辑器 **Ctrl+S** 会跑 `Wave.exe` + `clijasshelper.exe`，写入**纯 JASS**（~2200 行、无 `#include`），文件涨到 ~37KB。
    - 测试时编辑器判断"是否需要编译"（日志 `No need to compile.`）：
      本轮改过（dirty）→ 自动编译 → 能跑；**重启编辑器后打开未编译的图 → 判定无需编译 → 直接把 vJass 丢给游戏
      → War3 加载期崩溃**（`ACCESS_VIOLATION`，栈 `Game.dll ← kkapi_local_plugin.dll`，地址稳定复现）。
    - 判别：解包看 `war3map.j` **含 `#include` = 未编译**（必崩），无 = 已编译（可跑）。
    - 修复：让用户在编辑器里按一次 **Ctrl+S**；之后测试正常（实测 18:16 保存后无崩溃、游戏正常起）。
    - ⇒ 交付纪律再加强一条：**MCP 改完必须让用户 Ctrl+S 一次**，不只是防丢，**更是防崩**。


14. 🔴 **`GetUnitsInRectAll` 会把尸体和英雄一起数进去**（实测）。用"区域单位数 < N 才刷怪"做上限判定 =
    杀几只后地上堆 3 具尸体 + 英雄 1 只 → 计数永远 ≥N → **彻底停止刷怪**，且没有任何报错。
    ✅ 正解：**独立计数器** —— 生成时 `CreepN[区] += 1`、死亡时按"单位自定义值标地盘号"
    （`SetUnitUserData(怪, 区号+1)`）`CreepN[区] -= 1`（用 `IMaxBJ(x-1,0)` 防负数锁死）。
15. 🔴 **队伍里有玩家 ≠ 同盟**：`.w3i` 的 `force_flags = 0` 时四人同队照样红名互殴。
    判定同盟看 `force_flags`（7 = 同盟 + 同盟胜利 + 共享视野）。
    双保险写法：`set_player_config` 时 `force_flags=7` **且** 在初始化触发器里对 4 人 12 个有序对各发
    `SetPlayerAlliance(p1,p2,ALLIANCE_PASSIVE,true)` + `ALLIANCE_SHARED_VISION`；
    验证靠 `GetPlayerAlliance(i,j,ALLIANCE_PASSIVE)` 打印 12 个方向是否全 true。
16. **删掉"正被引用的触发器"会弹模态框**（"该变量 gg_trg_XXX 现在使用中…"），模态框会把后续 MCP 调用卡死
    （表现为 120s 超时）。改页请用「清空 ECA 再重建」，别 `delete_trigger`；卡住了用 `PostMessage(hwnd, WM_CLOSE)` 关弹窗。
17. **Ctrl+S 前必须 `ShowWindow(SW_RESTORE)` + `SetWindowPos(HWND_TOPMOST)` 再 `SetForegroundWindow`**，
    否则按键被吞、文件 mtime 不变；而 `save_map` 又是假成功 → 很容易误判"已存盘"。

## 12. 真机验收流程（可直接照抄，实测有效）

前提：编辑器开着 + 地图已存盘。`scripts/game_input.ps1` 是这套的实现（鼠标 + 键盘 + 前置置顶）。

```
1) python -I tools/q.py test_map '{}'          # 起图
2) 等 12~15 秒（单机 WC3 加载慢），PowerShell 截全屏 → 看当前窗口位置
   Add-Type -AssemblyName System.Windows.Forms,System.Drawing
   $b=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
   $bmp=New-Object System.Drawing.Bitmap $b.Width,$b.Height
   $g=[System.Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size)
   $bmp.Save("shot.png")
3) 用截图里的实际坐标点按钮（窗口每次启动位置都不一样，**不要复用上一轮坐标**）
   powershell -File tools/game_input.ps1 -Action click -X <x> -Y <y>
4) 按键：powershell -File tools/game_input.ps1 -Action postkey -Key F2
5) 再截图核对（数值/单位/提示文字）
```

要点：
- 每次截图后重新定位，窗口位置会变（我因此误判过两轮"点击无效"）。
- 游戏必须先 `SetForegroundWindow`（脚本里已做），否则单机 WC3 暂停、定时器不走。
- 判断功能是否生效，看**人口/金币/单位数/屏幕提示**这些客观量，不要只看"对话框消失了"（WC3 点完自动隐藏）。

## 13. 参考文件与脚本

- `references/handbook.md` — 完整原文：环境与协作通路、参数五种形态详解、容器表、工具层 16 条、UI 规范全部细节、归因与设计套路、payload 样板、速查卡。**遇到本页没覆盖的细节或需要引用实测原委时读它。**
- `references/payloads.md` — 可直接复制的 JSON 样板：If/Else、循环+下标、帧事件注册、跨触发器调用、建帧+锚定、字符串拼接，**以及本轮真机验证过的对话框全套、按键事件、死亡复活分支、自测触发器**。
- `references/demo-case.md` — 已跑通的实战案例（选英雄 + 练功房）完整规格：坐标、六页结构、变量、实测结论、复制时的三个必改点。
- `scripts/kkwe_client.py` — MCP over SSE 最小客户端（ZCode 连不上 kkwe-mcp 时直连 19816）。用法：`python -I kkwe_client.py list` / `call <tool> '<json>'`。
- `scripts/eca.py` — ECA payload 构造器（`preset/lit/gvar/fn/raw/if_then/act` + `Editor` 驱动类），写构建脚本时 import 它。
- `scripts/game_input.ps1` — 真机输入注入：`-Action click -X -Y`（鼠标）、`-Action postkey -Key F2`（键盘，绕 Raw Input）。
