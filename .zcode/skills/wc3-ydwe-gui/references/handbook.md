# 魔兽3（YDWE / 逆天编辑器）GUI 编写手册 —— 通用版

> **适用范围：任意魔兽3 自定义地图**（YDWE / 逆天 GUI 触发器编辑器，中文 `.w3x`）。
> **写作目的：让另一个 AI 读完就能上手写这张图的 GUI，产出质量与风格达标。**
> **零项目专属内容** —— 具体地图的数值/键名/几何请按 §5 的套路自行摸清。
> 素材来源：实战踩坑 + 编辑器 UI 定义反查 + 编译产物逆推，全部经实测或对照实验确认。

---

## 0. 先记这三条（能避开 80% 返工）

1. **改任何一页之前，先重新列一遍页面/变量清单、核对索引。**
   新建页面通常插到 `index 0`，会让所有既有页索引整体后移。**曾因沿用旧索引，把另一页的动作覆盖成了整块代码。**
2. **写参数的两条命根子：种类位用 `type_id`（不是 `type`）+ 嵌套函数用 `func_params`（不是 `params`）。**
   写错是**静默失败**：语法检查照样通过，参数却已变成 `{"type_id":-1,"value":""}` —— **只有回读才能发现**。
3. **自建 UI 不显示时，排查顺序固定：父帧写法 → 贴图/资源路径 → 尺寸/锚点 → 图层顺序。**
   其中"父帧写成了取值函数"会得到**空父帧**：帧创建成功、属性全能写、**永远不渲染**，是隐蔽性最强的一类。

---

## 1. 环境与协作通路

### 1.1 两条通路（优先级从高到低）

**① 插件直写"编辑器里正开着的图"（首选，秒级生效）**
通过编辑器的扩展插件（本项目用 `KKWE` 系，工具名以 `mcp__kkwe-mcp__*` 开头；延迟工具：先 `ToolSearch` 再 `DeferExecuteTool`）。
- 探活：`ping` → `"pong"` 表示插件已在 WorldEdit 里跑。
- **通用读接口**：`get_map_info`（地图信息）/ `list_categories`（分类树）/ `list_triggers(cat)`（页清单）/ `get_trigger(cat,trg)`（整页 ECA 全文）/ `list_variables`（变量表）/ `list_trigger_functions(section,search)`（**可用动作/条件/事件/函数名 + 参数签名**，写没见过的动作前先查一次）/ `list_trigger_strings`（字符串表）/ `list_regions` / `list_units` / `list_doodads` / `list_custom_objects` / `get_object_data(_batch)` / `get_object_modifications`。
- **通用写接口**：`create_full_trigger` / `create_trigger` / `add_event` / `add_action` / `add_condition` / `replace_eca` / `remove_eca` / `reorder_eca` / `rename_trigger` / `set_trigger_enabled` / `set_trigger_description` / `create_variable` / `modify_variable` / `delete_variable` / `delete_trigger` / `validate_triggers` / `save_map` / 物编写 `set_object_data(_batch)` / `create_custom_object`。
- ⚠️ **写操作只进编辑器内存**（用户可 Ctrl+Z）→ **每完成一小块就让用户 Ctrl+S 保存**。
  实测教训：连续大量写入会把编辑器拖死；未保存时进程一死，**本轮全部内存改动丢失**（表现为调用报连接被重置）。
- ⚠️ 工具的调用清单是"会话开始时"注入的：**新加的东西在当前会话里可能还看不到**。

**② 解包/回包改 .w3x（插件不可用时）**
用地图工具（如 `w3x2lni` 的 `w2l.exe`）：`lni` 解包 → 改 `trigger\` 下的触发器文本（LML）+ `map\war3map.j` → `obj` 回包。
- **铁律：两层必须同改。** 回包工具**不重编译** `war3map.j`，只重建触发器数据；只改 LML 的话，编辑器里是新逻辑、**游戏里跑的还是老代码**（这种不一致极难排查）。
- 触发器文本靠**缩进**表达层级；`If/Else` 是两个并列的"动作"块（漏写块头会让后面整体错位）。
- 局部变量存"**裸名**"：存 `ls`，编辑器才显示成 `loc_ls`；照编辑器显示写 `loc_ls` 会变成 `loc_loc_ls`。
- 验收：回包日志必须 `0 个错误`；**反向解包后逐文件比 size+MD5** —— 整体文件的 MD5/体积**不可作为判据**（容器每次打包都有抖动），且"回包成功"不等于文件真被更新（输出被占用时会假成功）。

### 1.2 通用交付纪律
1. 小步写 → 每次 `validate_triggers`（**只验语法**）→ 再 `get_trigger` **回读核对**。
2. 让用户 **Ctrl+S**（编辑器卡死时先让用户连点几次 Ctrl+S，能存下就全保住）。
3. **设计/清单同时落本地文档** —— 编辑器崩了之后，文档是唯一重建依据。
4. 不主动替用户保存（让用户决定何时落盘）。

---

## 2. 逆天 GUI 的数据模型（写之前必须懂）

### 2.1 ECA 树
一页触发器 = 事件 + 条件 + 动作（合称 ECA），全部收录进一棵树。
- 顶层 ECA 的 `group_id = -1`；容器内部用 `group_id` 标"块"：
  **`IfThenElseMultiple`：条件 = 0 / Then = 1 / Else = 2**；单块容器（循环等）= 0。
- 容器子项全部放进**同一个 `children` 数组**，**顺序即语义**。
- **`eca_count` / `action_count` 只统计顶层**，children 不计入 → 想看全貌只能整页回读。

### 2.2 常用容器
| 容器名 | 用途 | 子块 |
|---|---|---|
| `IfThenElseMultiple` | 如果/则/否则 | 条件(0) + Then(1) + Else(2) |
| `YDWEForLoopLocVarMultiple` | 循环（带局部循环变量） | 动作(0)；参数 = 循环变量名 / 起 / 止 |
| `YDWEForLoopLocVarIndex` | 取循环下标（函数） | 常量 = 循环变量名 |
| `YDWEExecuteTriggerMultiple` | **执行触发器·带参数**（可传参） | 参数 = 触发器 / 模式；子项 = 赋值对 |
| `OrMultiple` / `AndMultiple` | 或 / 与 | 条件 |
| `YDWERegionMultiple` / `YDWEEnumUnitsInRangeMultiple` | 选取区域 / 范围内单位 | 动作 |
| `YDWERegisterTriggerMultiple` / `YDWETimerStartMultiple` | 动态注册 / 定时器 | 事件+动作 / 动作+动作 |

> ⚠️「执行触发器·带参数」走哈希槽位传参，**比较脆**（曾出现"回调里调它 → 崩溃 → 该回调所在的事件分发永久失效"）。
> 能用普通「运行触发器」（无参）+ 被调页自己重新取数时，**优先用它**。

### 2.3 参数的五种形态（写 payload 时唯一容易错的地方）
**写进去用 `type_id`**（写 `type` 会被当假值/忽略）：
| 形态 | 写法 | 说明 |
|---|---|---|
| 预设（枚举/关键字） | `{"type_id":0,"type_name":"<类型>","value":"<预设名>"}` | 下拉框取值 |
| **全局变量** | `{"type_id":1,"type_name":"<类型>","value":"<变量名>","array_index":{"type_id":3,"type_name":"integer","value":"0"}}` | 数组就带 `array_index` |
| 函数调用 | `{"type_id":2,"type_name":"<返回类型>","value":"<函数名>","func_params":[...]}` | **`func_params`，不是 `params`** |
| 字面量 | `{"type_id":3,"type_name":"integer|real|boolean|string","value":"..."}` | 布尔也用 3 + `"true"` |
| 局部变量（作参数） | `{"type_id":3,"type_name":"scriptcode","value":"<裸名>"}` | **裸名**，不带 `loc_`/`loop_` |

- ⚠️ **读写不对称**：读出来是 `func_call` + `params`，写进去要 `name` + `func_params` —— **别照着读出的结构回写**。
- ⚠️ `func_params` 必须**扁平**：`[a,b,c]`，不能 `[[a],b]`。
- ⚠️ **数组变量作参数时用"全局变量 + 下标"形式**；用"取局部变量的函数"顶包会在需要变量的位置传进空值（见 §2.4）。

### 2.4 🔴 全局变量 vs 局部变量是**两套写法**（最坑的一条）
- 要"全局变量 `F[0]`" → `type_id:1` + 变量名（+ `array_index`）。
- 要"局部变量 D" → **作参数**时：`type_id:3` + `scriptcode` + 裸名；**读值**时：函数 `YDWEGetAnyTypeLocalVariable`。
- ❌ **绝不能把"取局部变量的函数"当"全局变量"用。** 典型事故：建 UI 帧时父帧参数写成
  `{"type_id":2,"type_name":"frame","value":"YDWEGetAnyTypeLocalVariable","func_params":[{"array_index":{…0},"type_id":1,"type_name":"frame","value":"F"}]}`
  → 等于给帧传了**空父帧** → 帧建出来了、属性全能写、**永远不渲染**（现象：代码全对、屏幕上看不见）。
  ✅ 正确：`{"type_id":1,"type_name":"frame","value":"F","array_index":{"type_id":3,"type_name":"integer","value":"0"}}`

### 2.5 局部变量（YDLOC）与"裸名"
- 逆天局部变量**不是原生 local**，是哈希表：`SaveXxx(YDLOC, 触发器handle × 层号, KEY, v)`。
  命名空间 = 触发器 × 层号 → **不同触发器的同名局部变量互不干扰**，键可自由取。
- 🔑 **存储里一律写裸名**（`ls` / `q`）；`loc_` / `loop_` 是**编辑器自己加的前缀**，不属于名字。
  照编辑器显示写 → 编辑器再加一层 → `loc_loc_ls`（用户原话："loop 生成了两份"）。
- 需要"由外部「执行触发器·带参数」喂值"的变量，惯例是**在动作最前面补一条自赋值**（`设置 X = X`）——只声明不覆盖。
- 自查（都应为 0）：触发器文本里 `常量: loc_` / `常量: loop_` 的出现次数、脚本里 `ydul_loop_` 的出现次数。

### 2.6 字符串与本地化
- 中文/字面量：`type_id:3` + `type_name:"string"` → **原样保留**。
- 用 `type_name:"StringExt"` → 正文被塞进字符串表、参数变 `TRIGSTR_NNN` ✗。
- **要发中文提示：先 `设置 字符串局部变量 = "中文"`，再把变量传进"显示文本信息"** —— 最稳。
- `|n` **在系统消息里不换行**（只对工具提示/多面板有效）→ **多行明细"一条消息一行"，多次调用按代码顺序输出**。
- 颜色码 `|cffXXXXXX` 必须 `|r` 收尾；要数字变色写 `|cffffcc00+数值|r`（颜色码与数值包在一起）。
- 用本地玩家拼出来的字符串**只能用于显示**，绝不能进哈希表当同步逻辑（会不同步）。

---

## 3. 工具层硬规律（每条都是踩出来的）

| # | 现象 | 真因 / 正确做法 |
|---|---|---|
| 1 | 调用报 `Expected ',' or '}' in JSON at position N`（N≈2000~7900） | **单次 payload ≳7.8KB 会被截断**。→ 长 JSON **分行缩进**提交；超长就拆成多次 `add_action` / 把结构拆平 |
| 2 | 建完触发器，容器里的动作蒸发 | **`create_full_trigger` 的 `children` 会丢** → 只用它建"事件 + 顶层平铺动作"；带 children 的容器建完后再单独 `add_action`/`replace_eca` 填 |
| 3 | 改 A 页却改坏了 B 页 | **新建页插到 index 0** → 索引整体位移。→ **每次改页前重新列页清单核对索引** |
| 4 | 想改容器内部的一条子动作 → 做不到 | **嵌套节点无法单独定位**：`replace_eca` 只能作用于顶层 ECA。→ 把**整个容器（含全部子节点）**重新提交（要精确复刻原节点，只加要加的那条） |
| 5 | 触发器名莫名多出 " 001" | **先建了 `gg_trg_xxx` 变量、再建同名触发器** → 名字冲突被自动改。→ 顺序反过来：**先建触发器，再建变量** |
| 6 | 跨触发器调用引用不到 | 需先在变量表建 `gg_trg_<触发器名 sanitize 后>`（trigger 型）。sanitize = 非字母数字→下划线；**页面改名后变量名会变成工具自动生成的一串**，引用会断 |
| 7 | 路径里的反斜杠变双杠 | 参数 JSON 原文写 `\\` = 存 1 个反斜杠；写 `\\\\` = 存 2 个 ✗ |
| 8 | 一切正常但游戏里不对 | **语法校验只验 JASS 语法**（`0 错误` 什么都证明不了）→ 必须 `get_trigger` 回读逐项自查（`type_id:-1`、`TRIGSTR_`、容器是否多套一层、`group_id` 是否正确） |
| 9 | 删一条后索引全乱 | `remove_eca` 会让其后所有索引前移 → **从后往前删** |
| 10 | 想把动作插到中间 | `add_action` **只能追加到顶层末尾**；要插中间只能 `add_action` + `reorder_eca`，或整块 `replace_eca` |
| 11 | 参数被渲染成方括号原文（如 `[typename01_integer]`） | 用了 `type` 而不是 `type_id` ✗ |
| 12 | 字符串塞进 `unitcode`/`itemcode`/`abilcode` 等参数报错 | 目标 IP 类型要**套转换函数**（本项目为 `YDWES2UnitId` 字符串→unitcode、`YDWEI2UnitId` 整数→）；光改 `type_name` 不管用 |
| 13 | 深层函数嵌套导致参数丢失（`type_id:-1`） | `func_call` 里再嵌 `func_call` 会丢 → **先 `YDWESetAnyTypeLocalVariable` 存成中间变量再引用**（两跳代替嵌套）。判别口诀：**"参数里还能不能再看见一个函数调用？能 → 危险"** |
| 14 | `create_full_trigger` 报 `Unknown function: xxx` | 它的 `actions` 会**校验函数名**（条件名别混进 actions）；而 `add_action` 的 children **不校验**（名字写错静默通过） |
| 15 | 物编面板空白 / 树不见了 | **界面故障 ≠ 数据丢失**（用数据层接口一查就知道）→ 让用户**先保存再重启**编辑器 |
| 16 | 新建自定义单位在物编里看不到 | **不能以"另一个自定义单位"为基底**：必须以**标准 SLK 单位**为模板，并把需要的字段全部显式写一遍（数据层查不出来：脚本读得到，只有用户打开物编才发现） |

> 一条通用心法：**"工具返回成功" ≠ "改动生效"**。凡关键改动，一律"写 → 回读 → 给人看"三步走。

---

## 4. 帧 / 自绘 UI 编写规范（DZAPI 系）

### 4.1 建帧三步
```
① 先加载模板定义（一次即可，别每次建帧都调）      DzLoadToc("路径\\模板定义.toc")
② 建帧：DzCreateFrameByTagName(标签, 唯一名字, 父帧, 模板名, 0)
   标签 = BACKDROP / TEXT / BUTTON / SIMPLEFRAME…；**模板名是 fdf 模板**（可留空 = 默认字体）
③ 设属性：SetPoint / SetSize / SetText / SetTexture / SetAlpha / Show
```
- **第 4 个参数是"模板"不是"贴图"** ✗ —— 贴图要用 **`DzFrameSetTexture(帧, "路径.blp", 0)`**。
  空模板 `""` = 游戏默认字体（中文正常）；自定义模板（如 `BG11` 背景盒、`WZ3` 文本款式）来自随图导入的 fdf。
- `BACKDROP` 必须显式 `DzFrameSetSize`（不会自适应）；`TEXT` 不写尺寸则随文字自适应。

### 4.2 🔴 父帧参数写法（最隐蔽的坑）
- 父帧 = **全局变量形式**（`type_id:1` + 变量名 [+ `array_index`]）✓
- 写成"取局部变量的函数" → **空父帧**：帧**创建成功、属性全写得进、编译 0 错误、永远不渲染** ✗
- 排障口诀（自建帧不显示时按此顺序）：
  **① 父帧是不是空的（写法对不对）→ ② 贴图/资源路径是否存在 → ③ 尺寸/锚点 → ④ 图层顺序**

### 4.3 图层顺序：**后创建的在上层**
典型事故：先建文字、后建不透明背景盒 → 背景把文字压在下面（只见盒子、一个字不见）。
✅ 顺序：**背景/底图先建 → 文字/图标后建**。

### 4.4 自适应与"自动换行"
- 正文文字帧：`DzFrameSetSize(正文, 0.2, 0)` —— **宽 0.2、高 0（高度自适应）**，长文字自动换行、框跟着变高。
- 背景盒要"自动包住内容"：把盒子的**左上挂到最上面那个元素的左上**、**右下挂到最下面那个元素的右下**（各留 0.012 边距）。
- ⚠️ 锚定目标必须**已创建**（锚点是动作执行时求值）→ 顺序：先建元素、再给盒子挂锚点。

### 4.5 锚定链范式（一行行/一列列都靠"挂前一个元素的角"排）
```
[顶部元素]        左下 ↔ 下面一行的左上
[一行横排元素]    第2个.左下 ↔ 第1个.右下；第3个.左下 ↔ 第2个.右下 ……（横向串联）
[正文块]          其左上 ↔ 上面那一行的左下
[外框]            左上 ↔ 最上元素的左上(-0.012,0.012)、右下 ↔ 最下元素的右下(0.012,-0.012)
```
要点：**横排元素用"右下↔左下"串联**（不要竖叠成上/下）；改动量小、含义清晰、和手摆效果一致。

### 4.6 子帧随父帧显隐
把元素建成某父帧的子帧 → 父帧显示/隐藏时它们**自动跟着**，不用单独写 `Show`。
⚠️ 但**子帧不改变父帧尺寸**：`TEXT` 父帧只会被"文字"撑大 —— 要包住子帧得靠"外框挂锚点"（§4.4）。

### 4.7 坐标与枚举
- 屏幕坐标系：原点**左下**，整屏约 **0.8 × 0.6**（`y = 0.46` 就飞出屏幕了）。
- 锚点枚举：`0=左上 1=顶 2=右上 3=左 4=中心 5=右 6=左下 7=底 8=右下`。
- ⚠️ 个别预设名**自带尾随空格**（定义文件里写成 `名字 =`），要用得带引号 + 空格；**能用干净名字（如 Center）就别用带空格的**。

### 4.8 🔴 帧事件（鼠标移入/移出/点击）—— 最血泪的一段
```
DzFrameSetScriptMultiple(GetLocalPlayer(), FrameEvent_Mouse_Enter, 按钮帧)   // 移入
DzFrameSetScriptMultiple(GetLocalPlayer(), FrameEvent_Mouse_Leave, 按钮帧)   // 移出（成对）
DzFrameSetScriptMultiple(GetLocalPlayer(), FrameEvent_..._Pressed, 按钮帧)   // 点击
```
回调里取"当前事件帧/玩家"：**`DzGetTriggerUIEventFrame()` / `DzGetTriggerUIEventPlayer()`（都无参）** —— 不要自己反推。
命令栏按钮帧：`DzFrameGetCommandBarButton(行, 列)`，**0 基**，且**行列顺序与直觉常相反 → 改动前先让用户确认格子位置**。

三条铁律（全部实测）：
1. **同一帧 + 同一事件只能注册一次。**
   **第一次注册占住槽位，之后的注册被静默忽略**（不覆盖、不追加、不报错）。
   验证实验：同一处写两条结构完全相同的移出注册 → 只有**先注册**的那条会跑。
   ⇒ **"分两条注册、各做一半"永远行不通。**
2. **"禁用"一条注册 ≠ 删除它。**
   被禁用的条目**仍会生成注册调用**，但它的**回调体生成为空函数** → 它占着槽位、把一个"什么都不做"的空函数注册上去
   → 表现就是"另一条明明写了内容却永远不触发"。**重复的注册要删除，不能只禁用。**
3. **回调体里不能有任何会报错的动作。**
   帧事件回调里**报错一次，这个帧的整个事件分发就永久哑掉**（现象：注册那一刻响一次、之后鼠标怎么动都不响应，连"移出"都没有）。
   - ✅ 安全写法：**回调只做"写一个全局标记 / 打印"**，真正的取数、拼字、动 UI 帧**放到计时器线程或被调触发器里**。
   - ✅ 被调触发器**第一句自己兜底判空**（`如果 帧 为空 就结束`）—— 这是防"写哑"的命门。
   - ❌ 回调里不要碰可能为空的帧（对空帧 `Show/SetPoint` 会崩）；❌ 避免"执行触发器·带参数"。

### 4.9 常用查询与"取不到"清单
| 想要什么 | 用法 | 备注 |
|---|---|---|
| 当前选中单位 | `DzGetSelectedLeaderUnit()` | 无参 |
| 当前事件帧 / 玩家 | `DzGetTriggerUIEventFrame()` / `DzGetTriggerUIEventPlayer()` | 无参，回调里用 |
| 帧是否可见 | `DzFrameIsVisible(帧)` | 可用 |
| 鼠标焦点帧 | `DzGetMouseFocus()` | **实测常恒为 0** → 不可依赖 |
| 子帧遍历 | `DzFrameGetChild(帧,i)` | **实测常取不到** → 不可依赖 |
| "这个按钮是第几个" | 注册时把"帧→编号"写进数据表（`SaveAnyTypeDataByUserData`），回调里反查编号 | 把"控件"映射到"业务编号"的正规做法 |

⚠️ **帧句柄每局都会变**（同一个按钮两局实测值不同）→ **任何判定都不能把句柄写死成常量**。

---

## 5. 通用做法库（换一张图也能照这个套路摸清并落地）

### 5.1 接手一张陌生图：摸底清单（按顺序做）
1. `get_map_info` → 地图名/尺寸/玩家数/存档次数。
2. `list_categories` + `list_triggers(分类)` → 先把**页面全貌**列出来（含禁用页！禁用页往往是被证伪的旧实现，是宝贵的"排除项"）。
3. `list_variables` → 变量表（数组/初始值/是否初始化）——**变量名就说明了数据结构**。
4. `list_regions` / `list_units` → 几何与关键单位（棋盘/刷兵点/交互对象）。
5. 挑 1~2 个"核心玩法页"`get_trigger` 全文读 → **从读写的数据表键名反推业务模型**（谁存什么、键怎么拼）。
6. 写任何东西之前，先 `list_trigger_functions(section,search)` 确认**动作/条件/事件名**存在且**参数签名**对得上。
7. 涉及对象数据：`list_custom_objects` + `get_object_modifications`（能看到 `base_id` 与全部改动）。

### 5.2 数据表（哈希表）通用设计套路
- 键的两种常见拼法：`前缀 + 槽位号`（区域/格子）与 `玩家 + 字段名`（玩家资源）。
- ⚠️ **按"槽位号"索引的表，与"谁在线"无关** → "数值 > 0"**不能**替代在线判定。
  在线判定要两条配合：**"控制器 = 用户"（排电脑）+ "游戏状态 = 正在游戏"（排空位/已离开）** —— 单用任一条都漏。
- 需要"区域/单位句柄"做键时，存**句柄（handleID）**最省事，还能顺带绕开"玩家索引 0 基/1 基"的坑。
- 数据表里的矩形/点等**不是地图预置对象**，别去 `gg_rct_*` 里找。
- 通用原则：**数据表是"唯一真源"** —— 显示层、逻辑层都从同一张表读，避免两处口径不一致。

### 5.3 「这个动作是谁做的」——归因通道表（共享单位/公共设施的通用痛点）
| 通道 | 能归因？ | 说明 |
|---|---|---|
| **商店出售单位 / 购买物品** | ✅ | 引擎会给"买出来的东西"打上购买者的身份；**事件的"触发单位"= 商店本身**，连"哪个设施"都一并给了 |
| **按玩家注册「单位被选中」** | ✅ | 事件按玩家注册，`触发玩家` 就是选中者 |
| 施法事件 | ❌ | `触发玩家` 恒为**单位拥有者**，不是操作者 |
| 「发布命令」事件 | ❌（多数封装） | 实测常为**拥有者语义**；**各版本不一致，必须让用户跑一次实测** |
| `GetLocalPlayer()` 猜操作者 | ❌❌❌ | 本地信息；一旦用它决定"扣谁的钱"这类同步逻辑 → **不同步/掉线** |
- 通用心法：**优先找"引擎会主动携带身份的事件"（购买/拾取/选择），不要从"命令/施法"事件反推。**
- 固有限制（要跟用户明说）：**两个玩家同时选中同一单位时，谁按的键判不出来**，引擎不暴露，无 100% 解法。
  折中三档：① 实测「发布命令」能否白捡；②「选中即认领 + 施法后立刻清空记录」（把歧义窗口压到零点几秒）；③ **改结构**（拆成每玩家独立单位 / 回合制只有当前玩家能操作）。

### 5.4 "几十个可点选交互对象"（棋盘格、建筑位）怎么设计
- **不要按"对象数 × 玩家数"铺代理单位**（36×5=180 之类）——代理**不需要每对象一个**。
- 方案 A（最省）：**直接用「单位被选中」事件**，零反查、零歧义；防误触用"已选中数量 = 1"判定单击，或给每个玩家加冷却。
- 方案 B（需要技能按钮时）：**每玩家只要 1 个代理单位 + 一个目标型技能** → `施法单位的拥有者` = 操作者、`技能施放目标` = 对象。
- 方案 C（公共设施）：**商店 + 出售单位**（见 §5.3），不需要共享控制，天然防误触。
- 单位数量**不是性能瓶颈**（几千单位都能扛）；真实成本是**手工摆放量**和**框选时混入**。
- 前提必查：对象必须"可被选中"；"被选中"事件能否对非己方/共享单位触发，**让用户实测一次**。

### 5.5 循环与玩家遍历的通用坑
- **玩家索引基准必须实测**（1 基 or 0 基随封装不同）：写个一次性探针，循环 1..N 显示"序号 → 玩家名"，一眼看出。
  **绝不要按语言惯例推断** —— 曾按"0 基"去改，被实测推翻。
- **"我/你"这类本地化字符串**：一条消息只发给一个人 → 随便用；发给多人 → 必须按本地玩家分别拼（且**只能用于显示**）。
- **数组残留**：`数组[下标]` 只在条件成立时赋值 → 不满足时不重置会**残留上一轮的值**，要补 `= 0` 兜底（或改成无条件计算）。
- **守卫式写法优先于标记变量式**：
  ❌ 多条并列 `If`，每条都重复写同一组守卫 → 重复、冗长；
  ✅ **前置检查用"提前退出"**（`如果 X==0 → 提示 + 返回`），后面所有成功逻辑**不再需要守卫**，整体再套一个 `如果 ok → …`。
  口诀：**"不满足就走人，能走到最后的就该执行"**。
  ⚠️ **"提前返回"会跳过其后的所有动作** —— 用之前必须想清楚"要不要跳过收尾动作（如清理临时单位）"。
- **除法必须守卫**：整数除零会**崩掉该线程**，其后同线程的动作全不跑。
- 每加一版功能都**回头做减法**：删多余循环、内联中间变量、去掉"为了清零而存在的赋值"。

### 5.6 交互设计心法（能省掉一整类难题）
- **能拆成"每玩家自己的单位"就拆** —— 归属问题自然消失，"是谁操作的"不再需要判断。
- **回合制/顺序制**里，"当前该谁操作"本身就是答案，直接用现成变量，并顺手加"非当前玩家操作忽略"收紧玩法。
- 需要"识别发起者"时，先问清**"为什么需要知道是谁？"** —— 很多需求（只为扣钱、或可走公共池）在问清后就不需要识别了。

---

## 6. 排障方法论（怎么一次把问题问对）

1. **先做"对照实验"隔离变量**（最有效的手法）
   例：自绘 UI 不显示 → 把贴图临时换成**图里一定存在**的那张贴图 → 一次区分"路径不存在"还是"帧不渲染"。
2. **按"二分清单"顺序查，不要跳**
   UI 问题：父帧写法 → 贴图/资源 → 尺寸/锚点 → 图层顺序。
   事件问题：这个帧这个事件注册了几次（重复会顶掉）→ 回调体是否可能报错（会写哑）→ 被调页是否自己兜底。
3. **建"最小复现页"**：请用户新建一页"只有两条动作、只差一个变量"的试验页做 A/B —— 比在复杂页里猜快十倍。
4. **看"编译产物"而不是源码**：把一页**转换成 JASS**（编辑器功能，或解包 `war3map.j`），
   能直接看到**真实回调函数名、函数体、注册调用** —— "两条注册只活一条""回调体是空函数"这类问题只有这里看得见。
5. **要证据**：让用户给"一句话现象 + 截图"；自己下结论时也附依据（哪条实测 / 哪份编译产物）。

---

## 7. 与人类协作者的沟通规范

- **中文输出；结论先行**，再用表格/清单展开；每个发现**落到本地文档**（编辑器可能崩，文档是唯一重建依据）。
- **一轮做一件事、小步交付**，并明确说"下一步需要你做什么（保存 / 实测 / 截图）"。
- **报 bug 前先自查一句**：这条是我按语言惯例推断的，还是代码本身自相矛盾？**只有后者才值得报**。
- 用户可能**亲自核对改动量**（"上版 45 行这版 69 行"）→ 每轮回头做减法，并先给"删了什么"的清单。
- **明确说"我无法在本机实测游戏"**，请用户在编辑器/游戏里确认；他吃"证据表"（检查了哪个文件/哪一行/期望/实际）。
- 用户会用**编辑器里的读法**描述现象（如"当游戏逝去 1.00 秒" = 定时器事件、"按钮 (2,0)" = 命令栏行列）
  → **照他的读法理解，不要先翻译成脚本术语再反推**。
- 交付文档的形态：**修复/改动清单 + 关键结论 + 待拍板项**，越短越好（用户明确要求"别内联打补丁，给完整新版"）。

---

## 8. 可复制样板（payload 模板）

### A. 一个 If（then / else）
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

### B. 循环 + 取循环下标当参数
```json
{"name":"YDWEForLoopLocVarMultiple",
 "parameters":[{"type_id":3,"type_name":"scriptcode","value":"a"},     // ★裸名
               {"type_id":3,"type_name":"integer","value":"1"},
               {"type_id":3,"type_name":"integer","value":"36"}],
 "children":[ /* 循环体 */ ]}
// 取下标：{"type_id":2,"type_name":"integer","value":"YDWEForLoopLocVarIndex",
//         "func_params":[{"type_id":3,"type_name":"scriptcode","value":"a"}]}
```

### C. 帧事件注册（成对 + 回调极简 + 计时器干活）
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

### D. 跨触发器调用（无参，最稳）
```json
{"name":"TriggerExecute","parameters":[{"type_id":1,"type_name":"trigger","value":"gg_trg_目标页"}]}
// ⚠️ 被调页第一句必须自己兜底： 如果 关键帧为空 → ReturnAction
// 带参版本（较脆，慎用）：YDWEExecuteTriggerMultiple + 子项赋值
```

### E. 建帧 + 锚定链（父帧用全局变量形式！）
```json
{"name":"SetVariable",
 "parameters":[{"type_id":1,"type_name":"AnyGlobal","value":"F",
                "array_index":{"type_id":3,"type_name":"integer","value":"2"}},
   {"type_id":2,"type_name":"frame","value":"DzCreateFrameByTagName","func_params":[
     {"type_id":3,"type_name":"string","value":"BACKDROP"},
     {"type_id":3,"type_name":"string","value":"uizicon"},
     {"type_id":1,"type_name":"frame","value":"F",                        // ★父帧＝全局变量
      "array_index":{"type_id":3,"type_name":"integer","value":"0"}},
     {"type_id":3,"type_name":"string","value":""},                       // ★模板＝fdf 名，不是贴图
     {"type_id":3,"type_name":"integer","value":"0"}]}]}
// 贴图： DzFrameSetTexture(F[2], "UI\\Feedback\\Resources\\ResourceGold.blp", 0)
// 尺寸： DzFrameSetSize(F[2], 0.022, 0.022)
// 锚点： DzFrameSetPoint(F[2], FramePoints_BottomLeft, F[0], FramePoints_TopLeft, 0.006, 0.006)
```

### F. 字符串拼接 + 变色
```json
{"name":"YDWEOperatorString3","parameters":[
  {"type_id":3,"type_name":"string","value":"|cffffcc00第"},
  {"type_id":2,"type_name":"string","value":"I2S","func_params":[
    {"type_id":2,"type_name":"integer","value":"YDWEGetAnyTypeLocalVariable",
     "func_params":[{"type_id":3,"type_name":"scriptcode","value":"n"}]}]},
  {"type_id":3,"type_name":"string","value":"格|r"}]}
```

---

## 9. 速查卡（动手前扫一眼）

- **流程**：列页清单核对索引 → 小步写 → 语法校验 → **整页回读** → 让用户 **Ctrl+S**。
- **参数**：`type_id`（0 预设 / 1 全局变量 / 2 函数+`func_params` / 3 字面量、"scriptcode"=局部变量裸名）。
- **容器**：`IfThenElseMultiple`（0 条件 / 1 Then / 2 Else）、`YDWEForLoopLocVarMultiple`、`YDWEExecuteTriggerMultiple`、`Or/AndMultiple`。
- **工具**：单次 payload ≤ 7.8KB（长 JSON 分行）；带 children 的容器别用"一次性建页"；删条目从后往前；改容器内部就整块重提。
- **自绘 UI**：模板 ≠ 贴图；父帧用全局变量；背景先建；后建在上层；子帧随父显隐；外框挂最上/最下的锚点自适应。
- **帧事件**：一帧一事件**只注册一次**；重复的要**删**不要禁用；回调**报错一次 → 整个分发永久哑掉**；回调只写标记，重活放计时器/被调页，被调页第一句自己兜底。
- **归因**：卖/买/选中 ✓；施法、发命令 ✗；`GetLocalPlayer` 猜 ✗。
- **中文/文本**：先塞字符串局部变量；`|n` 在系统消息里不换行；颜色码要有 `|r`。
- **习惯**：报 bug 前自问"惯例推断还是代码自相矛盾"；每轮回头做减法；关键改动"写 → 回读 → 给人看"。



