# -*- coding: utf-8 -*-
"""
Bloodborne PC (Lantern Engine) - 引擎核心永久反作弊解除补丁
直接修补 bb-probe.exe，永久放行内置修改器，即使在联机模式下也不会被强制清空。
自动创建 bb-probe.exe.bak 备份，支持一键还原。
"""

import os
import shutil
import sys

ENGINE_EXE = r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe"
BACKUP_EXE = r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe.bak"

PATCH_OFFSET = 0x3FD6E3
ORIGINAL_BYTES = b"\x75\x1C"  # jne +0x1c
PATCHED_BYTES  = b"\xEB\x1C"  # jmp +0x1c (无条件跳过反作弊清零)

def apply_patch():
    if not os.path.exists(ENGINE_EXE):
        print(f"[-] 未找到引擎主程序: {ENGINE_EXE}")
        return False
    
    # 检查当前文件状态
    with open(ENGINE_EXE, "rb") as f:
        f.seek(PATCH_OFFSET)
        current_bytes = f.read(2)
        
    if current_bytes == PATCHED_BYTES:
        print("[*] 补丁已经应用过了，bb-probe.exe 当前处于完全解锁修改器状态！")
        return True
    
    if current_bytes != ORIGINAL_BYTES:
        print(f"[-] 目标字节与预期不符 (当前: {current_bytes.hex()}, 预期: {ORIGINAL_BYTES.hex()})，中止修补以防破坏文件。")
        return False
        
    # 创建备份
    if not os.path.exists(BACKUP_EXE):
        shutil.copyfile(ENGINE_EXE, BACKUP_EXE)
        print(f"[+] 已创建备份文件: {BACKUP_EXE}")
    else:
        print(f"[*] 已存在备份文件: {BACKUP_EXE}")
        
    try:
        with open(ENGINE_EXE, "r+b") as f:
            f.seek(PATCH_OFFSET)
            f.write(PATCHED_BYTES)
        print("[+] 补丁成功应用！")
        print("    已将 0x3FD6E3 处的 75 1C 修改为 EB 1C。")
        print("    现在无论游戏是否开启联机，游戏内修改器功能都将永久生效。")
        return True
    except PermissionError:
        print("[-] 写入失败：文件可能正被运行中的游戏占用。")
        print("    请先退出游戏，或直接使用 hotpatch_live.py 进行内存热修复。")
        return False

def restore_backup():
    if not os.path.exists(BACKUP_EXE):
        print("[-] 未找到备份文件，无法还原。")
        return False
    try:
        shutil.copyfile(BACKUP_EXE, ENGINE_EXE)
        print("[+] 已成功从备份文件还原原版 bb-probe.exe。")
        return True
    except Exception as e:
        print(f"[-] 还原失败: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "restore":
        restore_backup()
    else:
        apply_patch()
