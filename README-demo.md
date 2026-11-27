# testmap.w3x — 选英雄 / 练功房 Demo

生成时间：2026-11-26　编辑器：KKWE（C:\games\KKWE_editor）
MCP 通路：kkwe-mcp SSE `127.0.0.1:19816`（编辑器内插件启动）

## 玩法

1. 开局 0.1 秒弹出**选英雄对话框**（3 个按钮，带颜色）
2. 点选后在基地创建英雄（力量·山丘之王 / 敏捷·剑圣 / 智力·大法师），初始 8 级，自动选中 + 镜头平移 + 小地图闪烁
3. **F2** → 传送到练功房（镜头 0.8s 平移 + 提示）
4. **F3** → 传送回基地；**英雄已阵亡则直接在基地复活**
5. 人在练功房时，每 **10 秒**刷 **2 只**强盗（中立敌对），场上上限 **6 只**，每波提示"第 N 波怪物来袭"
6. 强盗死亡 → 玩家 **+50 金币**（带提示）

## 地图布局（原点地图中心，左下为负）

| 区域 | 范围 | 用途 |
|---|---|---|
| BaseArea | (-2816,-2816) ~ (-1792,-1792) | 基地：城堡(-2304,-2304) + 双塔 |
| TrainArea | (1664,1664) ~ (2944,2944) | 练功房：英雄落点(2304,2304)，怪刷对角(1984/2624) |
| 英雄落点 | (-2304, -1856) | 城堡正北 448，避开建筑占位 |

## 触发器（分类 Demo）

| 页面 | 事件 | ECA 数 | 说明 |
|---|---|---|---|
| Demo_Init | 计时器 0.10s | 16 | 建城堡/双塔、建对话框 3 按钮、显示、提示、镜头、**运行时注册对话框事件** |
| Demo_Pick | **无静态事件**（由 Init 动态注册） | 11 | 隐藏对话框 → 判定英雄类型 → 创建/选中/镜头/提示 → 给 2500 经验 |
| Demo_F2 | 硬件按键 F2 | 8 | 守卫(未选英雄提示返回) → 传送练功房 → 选中/镜头/提示 |
| Demo_F3 | 硬件按键 F3 | 8 | 守卫 → 活着则传送、死了则 `ReviveHero` 原地复活 → 回到基地 |
| Demo_Spawn | 周期计时器 10s | 10 | 不在练功房返回 → 数量>6 返回 → 波次+1 → 刷 2 怪 → 波次提示 |
| Demo_Reward | 任意单位死亡 | 4 | 死亡单位属中立敌对 → +50 金币并回显总数 |

## 变量

HeroDialog(dialog) / Hero(unit) / HeroType(unitcode) / HeroPicked(bool) / InTrain(bool)
BtnP,BtnA,BtnI(button) / Wave(int) / Msg(string) / TempUnit / TempPl / TempGroup / Killer(未用) / TempInt(int)
区域：gg_rct_BaseArea / gg_rct_TrainArea

## 实测结论（2026-11-26，真跑游戏验证）

| 环节 | 结果 |
|---|---|
| 选英雄对话框显示 | ✅ 三色按钮正常 |
| 点击按钮创建英雄 | ✅ 8 级山丘之王，5/12 人口 |
| F2 进练功房 | ✅ 传送 + 镜头平移 + 提示 |
| 定时刷怪 | ✅ 2 只/10 秒、上限 6、波次提示 |
| 击杀奖励 | ✅ 金币 111 → 229（+50 ×2 + 系统赏金） |
| F3 回基地 | ✅ 回城 + 镜头 |

## 本轮踩到并修掉的坑（都已验证）

1. **对话框点击无效（最隐蔽）**：`Demo_Pick` 的对话框事件在地图初始化时静态注册，那一刻 `HeroDialog` 还是 null → 事件挂到空对象上，点按钮永远不触发。
   → 改成 `Demo_Init` 末尾 `CustomScriptCode`：`call TriggerRegisterDialogEvent(gg_trg_Demo_Pick, udg_HeroDialog)`。
2. **算术写 `Wave + 1` 编译成裸 `Wave`** → JASS 未定义变量，整图编译失败。必须写 `udg_Wave + 1`。
3. **刷怪过猛**：4 只/8 秒、上限 16，1 级英雄 30 秒被围死。→ 2 只/10 秒、上限 6、英雄初始 8 级。
4. **英雄死后 F3 只挪尸体**。→ F3 增加 `IsUnitAliveBJ` 判定，死了走 `ReviveHero`。
5. 中文写进 StringExt 参数会转成 `TRIGSTR_NNN`（编辑器里显示 TRIGSTR），但编译产物是正确中文，功能无影响。
6. 编辑器连续大量写入会崩（实测两次）→ **每建完一页/每条动作立即 `save_map`**。
7. 🔴 **MCP `save_map` 不编译脚本**：地图里存的是 vJass 源码（含 `#include`，21KB / 346 行）。编辑器重启后直接测试
   会跳过编译 → War3 加载期崩溃（`ACCESS_VIOLATION`，栈在 `kkapi_local_plugin.dll`）。
   **必须在编辑器里 Ctrl+S（编译后 37KB / 2220 行纯 JASS）再测试**。判别：解包看 `war3map.j` 有没有 `#include`。

## 自动化验证

```bash
python -I tools/verify.py --compiled     # 60 项断言：结构 / 静默失效 / 变量区域 / 编译产物
```
当前结果：**60 通过，0 失败**。

## 工具目录

| 文件 | 用途 |
|---|---|
| `tools/kkwe_client.py` | MCP over SSE 最小客户端（ZCode 连不上时直连 19816） |
| `tools/eca.py` | ECA payload 构造器（type_id / func_params / 容器） |
| `tools/build_demo.py` | 全量构建（可重跑，幂等） |
| `tools/verify.py` | 回归检查（改完必跑） |
| `tools/game_input.ps1` | 向游戏窗口注入鼠标点击 / 按键（PostMessage，键盘绕 Raw Input） |
