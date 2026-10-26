# Bloodborne PC (Lantern Engine) - In-Game Cheats Fix & Analysis
# 血源诅咒 PC 移植版 (Lantern Engine) 修改器失效原因分析与修复工具箱

[English](#english) | [中文说明](#chinese)

---

<a name="english"></a>
## English

### 1. Overview
In **Lantern Engine** (the native PC compatibility layer for Bloodborne, developed by Awaken), players frequently report that in-game modifiers (blood vials, quicksilver bullets, infinite stamina, weapon durability, echo multipliers, etc.) **do not take effect**, even though the toggles and sliders are successfully checked and saved in the GUI overlay (`Insert` / `L3+R3`) or the external launcher (`修改项` tab).

This repository provides:
- A thorough **root cause analysis** via reverse engineering of `bb-probe.exe`.
- **Three distinct fix tools**: Live memory hotpatch (no restart), clean config switch (offline mode), and permanent binary patch.
- Disassembly scripts and runtime memory diagnostics.

---

### 2. Root Cause Analysis

#### A. Anti-Cheat Enforcement in Multiplayer Mode
When `online_enabled=1` is set in `lantern.ini` (connecting to The Hunter's Dream server):
1. **Startup Check**:
   `bb-start.exe` sets the environment variable `BB_ONLINE=1`. During initialization, `bb-probe.exe` checks this environment variable via `getenv("BB_ONLINE")` at `0x140401d60`.
2. **Session Log Output**:
   The engine logs the suppression notice in `logs/last_session.log`:
   ```text
   Cheats: off while playing online
   ```
   and sets the runtime online flag at `base + 0x38dc570` (`online_flag = 1`).
3. **Control Flow Interception in Frame Loop**:
   During every rendered frame, `bb-probe.exe` invokes the cheat dispatch routine at `0x1403fe250`. At `0x1403fe2d7`, it reads `online_flag`:
   ```asm
   0x1403fe2d7: 44 0f b6 15 91 e2 4d 03   movzx r10d, byte ptr [online_flag] ; read online state
   0x1403fe2df: 41 80 fa 01               cmp r10b, 1                         ; is online == 1?
   0x1403fe2e3: 75 1c                     jne not_online                      ; bypass if offline
   0x1403fe2e5: 48 c7 05 e0 8d 4b 03 ...  mov qword ptr [Target1], 0          ; ZERO OUT POINTER 1
   0x1403fe2f0: 48 c7 05 fd 8d 4b 03 ...  mov qword ptr [Target2], 0          ; ZERO OUT POINTER 2
   0x1403fe2fb: 31 c9                     xor ecx, ecx
   0x1403fe2fd: 31 c0                     xor eax, eax
   0x1403fe2ff: eb 0c                     jmp skip_load                       ; bypass cheat values
   ```
4. **Immediate Exit**:
   Immediately following at `0x1403fe317`:
   ```asm
   mov rdx, [Target2]
   test rdx, rdx
   jle 0x1403ff20e  ; Target2 was cleared to 0, so it immediately jumps to exit!
   ```
   Because `Target2` is set to `0`, the function **immediately jumps out of the cheat logic**, preventing all cheat code from ever executing.

#### B. The UX Issue
The in-game menu (`Insert`) and launcher do not warn the player that modifiers are disabled while online. Toggles remain interactive, leading users to believe the cheats are simply broken.

---

### 3. Available Solutions

| Solution | Tool Script | Recommended Scenario | Description |
| :--- | :--- | :--- | :--- |
| **Solution 1** | `hotpatch_live.py` | **Game currently running** | Patches running memory via Win32 API. Bypasses the online wipe and restores pointers **instantly without restarting the game**. |
| **Solution 2** | `fix_bb_config.py` | Offline Single Player | Sets `online_enabled=0` in `lantern.ini`. Pure native solution intended by the engine. |
| **Solution 3** | `patch_engine_binary.py` | Permanent / Online Cheats | Patches `bb-probe.exe` binary at `0x3FD6E3` (`75 1C` -> `EB 1C`). Auto-creates `bb-probe.exe.bak` backup. |
| **Launcher** | `fix_cheats.bat` / `main_fix_tool.py` | All | Interactive CLI menu grouping all functions together. |

---

### 4. How to Use

#### Method 1: Live Memory Hotpatch (Quickest)
If your game is running right now:
```powershell
python hotpatch_live.py
```
Switch back to your game window: stamina won't deplete, and vials/bullets/echoes will update immediately according to your settings.

#### Method 2: Offline Single-Player Config Switch (Official / Clean)
```powershell
python fix_bb_config.py
```
Disables online mode in `lantern.ini`. Start the game normally; cheats will be enabled naturally.

#### Method 3: Permanent Binary Patch
Close the game first, then run:
```powershell
python patch_engine_binary.py
```
To revert back to original:
```powershell
python patch_engine_binary.py restore
```

---

<a name="chinese"></a>
## 中文说明

### 1. 项目简介
在 **血源诅咒 PC 移植版（Lantern Engine）** 中，很多玩家反馈在游戏内图形设置界面（按 `Insert` 或手柄 `L3+R3`）或启动器“修改项”标签中勾选了修改器功能（采血瓶数量、水银子弹、无限精力、武器耐久、回响获取倍率等），但是在实际游戏中**完全没有任何效果**。

本项目对游戏主程序 `bb-probe.exe` 进行了反汇编与内存逆向分析，确认了**失效原因**并提供了**三种一键修复工具**。

---

### 2. 根本原因剖析

#### 核心机制：联机模式下引擎主动开启反作弊拦截
1. **配置文件开启了联机功能**：
   在 `lantern.ini` 中配置了 `online_enabled=1` 与 `online_connected=1`（连接到 The Hunter's Dream 联机服务器）。
2. **启动阶段识别并记录**：
   启动引导程序 `bb-start.exe` 向子进程传递 `BB_ONLINE=1`。引擎核心 `bb-probe.exe` 初始化时通过 `0x140401d60` 检测到该变量，在会话日志（`logs/last_session.log` 第 159 行）中打印：
   ```text
   Cheats: off while playing online
   ```
   并将运行时的反作弊标识变量 `online_flag`（偏移 `0x38dc570`）置为 `1`。
3. **渲染循环强制清空作弊指针**：
   每帧渲染时（调用 `0x1403fe250` 作弊更新例程），引擎会检测 `online_flag`。一旦为 `1`，执行汇编指令：
   ```asm
   movzx r10d, byte ptr [online_flag]
   cmp r10b, 1
   jne not_online
   mov qword ptr [Target1], 0  ; 强制清空游戏数据指针 1
   mov qword ptr [Target2], 0  ; 强制清空游戏数据指针 2
   xor ecx, ecx
   xor eax, eax
   jmp skip_load
   ```
   随后在 `0x1403fe317` 检测 `Target2`：因其已在上方被强制置 0，直接触发 `jle exit` 提前跳出整个作弊处理逻辑！
4. **结论**：
   界面虽然允许勾选与配置，但只要开启了联机功能，引擎每帧在生效前都会强制清空作弊指针并静默拦截，导致修改项全部失效。

---

### 3. 工具清单与修复方案

- [hotpatch_live.py](hotpatch_live.py)：**内存实时热修复**。无需退出游戏，直接通过 Windows API 放行当前运行中游戏的反作弊跳转并恢复指针。
- [fix_bb_config.py](fix_bb_config.py)：**配置文件单人模式切换**。将 `lantern.ini` 设为 `online_enabled=0`，官方原生最安全稳定方案。
- [patch_engine_binary.py](patch_engine_binary.py)：**核心程序永久解锁补丁**。自动备份 `bb-probe.exe.bak`，直接修补二进制核心（`75 1C` 改为 `EB 1C`），无论是否联机永久可用。支持 `restore` 一键还原。
- [main_fix_tool.py](main_fix_tool.py) / [fix_cheats.bat](fix_cheats.bat)：一键控制台菜单，支持双击交互操作。
- `diagnostics/`：包含逆向分析过程中的断点验证、汇编计算与测试脚本。

---

### 4. 建议提交官方改进方向 (Suggestions for Lantern Engine)
1. **增加 UI 提示**：若联机模式下强制禁用修改器，建议在图形设置菜单与启动器中将选项置灰或显示提示 `(联机模式下已禁用 / Disabled in Online Mode)`，避免用户困惑。
2. **快捷离线开关**：在修改器页面提供一键切入单人离线模式的快捷开关。

---

## License
MIT License. Free to use, modify, and distribute.
