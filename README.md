# 血源诅咒 PC 移植版 (Lantern Engine) 修改器失效原因分析与修复工具

## 1. 为什么修改器不生效？（根本原因分析）

通过对游戏引擎核心 `E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe` 的逆向反汇编及运行时内存追踪，确认了修改器失效的根源：

### 核心机制：联机模式反作弊保护
1. **配置文件开启了联机功能**：
   在 `lantern.ini` 中配置了：
   ```ini
   online_enabled=1
   online_connected=1
   online_pool=huntersdream
   ```
2. **引擎启动时识别并锁定**：
   游戏启动引导模块 `bb-start.exe` 检测到联机开启后，会向子进程传递 `BB_ONLINE=1` 环境变量。主引擎 `bb-probe.exe` 启动时在会话日志（`logs/last_session.log`）中输出：
   ```text
   Cheats: off while playing online
   ```
   并将运行时的反作弊标识变量 `online_flag`（内存偏移 `0x38dc570`）置为 `1`。
3. **渲染循环中拦截修改项**：
   每帧渲染时（调用 `0x1403fe250` 作弊更新例程），引擎会检测 `online_flag`。一旦为 `1`，引擎会**强制将游戏数据指针（`Target1` 与 `Target2`）清零**，并执行 `jle exit` 提前跳出作弊逻辑。
4. **结论**：
   无论在游戏内的图形设置菜单（`Insert` / `L3+R3`）中勾选了多少项修改器（采血瓶 50、子弹 50、无限精力、回响倍率等），每帧应用前都被引擎强制清零并拦截，导致在游戏中没有任何效果。

---

## 2. 修复方案

本工具箱提供三种针对不同使用场景的修复方式：

### 方案 A：内存实时热修复（推荐，正在游戏中无需重启）
- **适用场景**：游戏当前正在后台运行，不想退出游戏重新加载。
- **运行方式**：直接运行 [hotpatch_live.py](file:///D:/CodePackage/血源诅咒PC/hotpatch_live.py)。
- **原理**：通过 Windows API 将运行中的 `bb-probe.exe` 内存中 `online_flag` 设为 `0`，并将 `0x1403fe2e3` 处的跳转逻辑修补为无条件放行（`EB 1C`），瞬间恢复采血瓶 50、水银子弹 50、无限精力等功能。

### 方案 B：修改配置文件为离线模式（推荐，官方原生纯净方案）
- **适用场景**：单人游玩，无需联机。
- **运行方式**：运行 [fix_bb_config.py](file:///D:/CodePackage/血源诅咒PC/fix_bb_config.py)（或在启动器“联机”页面关闭联机）。
- **原理**：将 `lantern.ini` 中的 `online_enabled=0`、`online_connected=0`。下次启动游戏时，引擎不再加载联机反作弊组件，内置修改器所有项自然正常生效。

### 方案 C：引擎主程序永久解锁补丁（联机/离线双生效）
- **适用场景**：希望在联机模式下也能使用修改器功能，一劳永逸。
- **运行方式**：先关闭游戏，然后运行 [patch_engine_binary.py](file:///D:/CodePackage/血源诅咒PC/patch_engine_binary.py)。
- **原理**：自动备份原版为 `bb-probe.exe.bak`，并在 `bb-probe.exe` 二进制文件 `0x3FD6E3` 偏移处将条件跳转 `75 1C` 改为无条件跳转 `EB 1C`，永久旁路反作弊清零逻辑。支持使用 `python patch_engine_binary.py restore` 一键还原。

---

## 3. 文件清单

- [main_fix_tool.py](file:///D:/CodePackage/血源诅咒PC/main_fix_tool.py)：交互式控制台修复主程序，整合了所有功能。
- [fix_cheats.bat](file:///D:/CodePackage/血源诅咒PC/fix_cheats.bat)：一键双击运行脚本。
- [hotpatch_live.py](file:///D:/CodePackage/血源诅咒PC/hotpatch_live.py)：当前运行进程实时热修复脚本。
- [fix_bb_config.py](file:///D:/CodePackage/血源诅咒PC/fix_bb_config.py)：配置文件单人模式快速切换脚本。
- [patch_engine_binary.py](file:///D:/CodePackage/血源诅咒PC/patch_engine_binary.py)：二进制永久补丁与还原脚本。
- `diagnostics/`：逆向分析、内存断点比对与验证过程脚本。
