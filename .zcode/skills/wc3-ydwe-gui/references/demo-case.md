# 实战案例：选英雄 + 练功房（2026-11 实测通过）

这是一个**已在本机真机跑通**的最小闭环，可直接当模板改。成品：`testmap.w3x`（64×64 空图，1 玩家）。

## 玩法闭环

```
开局 0.1s 弹对话框（3 英雄按钮）
  → 点选创建 8 级英雄（山丘/剑圣/大法师）+ 选中 + 镜头
  → F2 传送练功房（镜头平移 + 提示）
  → 每 10s 刷 2 只强盗（上限 6，波次提示）
  → 击杀 +50 金币
  → F3 回基地（死了自动复活）
```

## 坐标（地图中心为原点，地图范围 -4096 ~ 4096）

| 对象 | 坐标/范围 |
|---|---|
| 基地城堡 hcas | (-2304, -2304) |
| 防御塔 hgtw ×2 | (-2640, -2304) / (-1968, -2304) |
| 英雄落点 | (-2304, -1856)（城堡北 448，避开 5×5 占位） |
| 练功房区域 gg_rct_TrainArea | (1664,1664) ~ (2944,2944) |
| 刷怪点 ×2 | (1984,1984) / (2624,2624)，玩家 `PlayerNA`（中立敌对） |

## 六个页面的最小结构

| 页面 | 事件 | 关键点 |
|---|---|---|
| Demo_Init | 计时器 0.10s | 建装饰 → `DialogCreate` → 3 按钮（各存 `GetLastCreatedButtonBJ`）→ `DialogDisplay` → **`CustomScriptCode` 动态注册对话框事件** |
| Demo_Pick | **无静态事件** | 隐藏框 → 默认 `Hmkg`，按钮命中 `BtnA/BtnI` 覆盖为 `Obla/Hjai` → `CreateUnit` → `SelectUnitForPlayerSingle` → 镜头 → `AddHeroXP 2500` |
| Demo_F2 | 按键 F2 | `HeroPicked` 守卫 → `DzSetUnitXY` → `InTrain=true` → 选中/镜头/小地图 |
| Demo_F3 | 按键 F3 | `HeroPicked` 守卫 → `IsUnitAliveBJ` 分支（活：传送 / 死：`ReviveHero`）→ `InTrain=false` → 镜头 |
| Demo_Spawn | 周期 10s | 不在练功房 return → `CountUnitsInGroup > 6` return → `Wave = udg_Wave + 1` → 刷 2 只 → 波次提示 |
| Demo_Reward | 任意单位死亡 | `GetDyingUnit` 的拥有者 == `PlayerNA` → `AdjustPlayerStateBJ(+50)` → 回显金币 |

## 变量

`HeroDialog(dialog)` `Hero(unit)` `HeroType(unitcode)` `HeroPicked(bool)` `InTrain(bool)`
`BtnP/BtnA/BtnI(button)` `Wave(int)` `Msg(string)` `TempUnit/TempPl/TempGroup/TempInt`

## 实测结论

| 环节 | 证据 |
|---|---|
| 对话框 | 三色按钮渲染正常（截图） |
| 点选建英雄 | 8 级山丘之王，5/12 人口，头像正常 |
| F2 | 传送 + 镜头跟到练功房，提示可见 |
| 刷怪 | `第3波`、场上 3~4 只、上限 6 生效 |
| 奖励 | 金币 111 → 229，屏幕 `REWARD +50` |
| F3 | 回基地，镜头跟随 |

## 复制这段时的三个必改点

1. **对话框**：一定加 `CustomScriptCode → call TriggerRegisterDialogEvent(gg_trg_你的回调页, udg_对话框变量)`，否则点了没反应且不报错。
2. **算术**：`udg_变量名 + 1`，漏了 `udg_` 整图编译失败。
3. **刷怪强度**：先按 2 只/10 秒/上限 6 起步，英雄给 8 级；4 只/8 秒/上限 16 会把 1 级英雄 30 秒围死。

## 关联脚本（本技能 scripts/）

- `kkwe_client.py` — MCP over SSE 直连（`ping` / `list_*` / `add_action` …）
- `eca.py` — payload 构造器（`preset/lit/gvar/fn/if_then`）
- `game_input.ps1` — 真机注入（鼠标 `mouse_event`、键盘 `PostMessage`）
