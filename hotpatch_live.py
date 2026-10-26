# -*- coding: utf-8 -*-
"""
Bloodborne PC (Lantern Engine) - 内存实时修改器解锁补丁
用于在游戏运行状态下，实时解除由于联机/安全检查导致的修改器失效问题。
"""

import ctypes
from ctypes import wintypes
import sys

PROCESS_ALL_ACCESS = 0x1F0FFF
PAGE_EXECUTE_READWRITE = 0x40

kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

def get_process_by_name(process_name="bb-probe.exe"):
    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [
            ('dwSize', wintypes.DWORD),
            ('cntUsage', wintypes.DWORD),
            ('th32ProcessID', wintypes.DWORD),
            ('th32DefaultHeapID', ctypes.c_size_t),
            ('th32ModuleID', wintypes.DWORD),
            ('cntThreads', wintypes.DWORD),
            ('th32ParentProcessID', wintypes.DWORD),
            ('pcPriClassBase', wintypes.LONG),
            ('dwFlags', wintypes.DWORD),
            ('szExeFile', ctypes.c_char * 260)
        ]
    
    hSnapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
    pe = PROCESSENTRY32()
    pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
    
    found_pid = None
    if kernel32.Process32First(hSnapshot, ctypes.byref(pe)):
        while True:
            if pe.szExeFile.decode('utf-8', errors='ignore').lower() == process_name.lower():
                found_pid = pe.th32ProcessID
                break
            if not kernel32.Process32Next(hSnapshot, ctypes.byref(pe)):
                break
    kernel32.CloseHandle(hSnapshot)
    return found_pid

def apply_hotpatch(pid):
    hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not hProcess:
        print(f"[-] 无法以完全访问权限打开进程 PID={pid}，错误代码: {kernel32.GetLastError()}")
        return False
    
    try:
        # 获取 bb-probe.exe 模块基址
        hMods = (wintypes.HMODULE * 1024)()
        cbNeeded = wintypes.DWORD()
        if not psapi.EnumProcessModules(hProcess, hMods, ctypes.sizeof(hMods), ctypes.byref(cbNeeded)):
            print("[-] 枚举进程模块失败")
            return False
        
        base_addr = hMods[0]
        print(f"[+] 找到 bb-probe.exe 基址: {hex(base_addr)}")
        
        # 1. 检查并重置 online_flag (基址 + 0x38dc570)
        online_flag_addr = base_addr + 0x38dc570
        zero_byte = (ctypes.c_uint8 * 1)(0)
        bytes_written = ctypes.c_size_t()
        kernel32.WriteProcessMemory(hProcess, ctypes.c_void_p(online_flag_addr), zero_byte, 1, ctypes.byref(bytes_written))
        print(f"[+] 已将内存 online_flag (地址 {hex(online_flag_addr)}) 重置为 0")
        
        # 2. 修改 0x1403fe2e3 处的跳转 (75 1c -> eb 1c: 无条件跳转跳过清空逻辑)
        # 该跳转控制每帧作弊更新时是否触发防作弊清零
        patch_addr = base_addr + 0x3fe2e3
        old_protect = wintypes.DWORD()
        if not kernel32.VirtualProtectEx(hProcess, ctypes.c_void_p(patch_addr), 2, PAGE_EXECUTE_READWRITE, ctypes.byref(old_protect)):
            print(f"[-] 修改内存保护失败: {kernel32.GetLastError()}")
            return False
        
        # 写入 eb 1c (jmp +0x1c)
        patch_bytes = (ctypes.c_uint8 * 2)(0xEB, 0x1C)
        kernel32.WriteProcessMemory(hProcess, ctypes.c_void_p(patch_addr), patch_bytes, 2, ctypes.byref(bytes_written))
        kernel32.VirtualProtectEx(hProcess, ctypes.c_void_p(patch_addr), 2, old_protect, ctypes.byref(old_protect))
        print(f"[+] 已解除运行时反作弊清零拦截 (地址 {hex(patch_addr)} 改为 EB 1C)")
        
        # 3. 验证当前作弊选项
        vials_addr = base_addr + 0x1034510
        bullets_addr = base_addr + 0x1034514
        stamina_addr = base_addr + 0x1034518
        
        buf4 = (ctypes.c_uint32 * 1)()
        buf1 = (ctypes.c_uint8 * 1)()
        kernel32.ReadProcessMemory(hProcess, ctypes.c_void_p(vials_addr), buf4, 4, None)
        vials_val = buf4[0]
        kernel32.ReadProcessMemory(hProcess, ctypes.c_void_p(bullets_addr), buf4, 4, None)
        bullets_val = buf4[0]
        kernel32.ReadProcessMemory(hProcess, ctypes.c_void_p(stamina_addr), buf1, 1, None)
        stamina_val = buf1[0]
        
        print("=" * 60)
        print("[+] 内存热修复应用成功！")
        print(f"    - 采血瓶数量设置值: {vials_val}")
        print(f"    - 水银子弹数量设置值: {bullets_val}")
        print(f"    - 无限精力开关状态: {'开启' if stamina_val else '关闭'}")
        print("[+] 现在在游戏中按 Insert 或 L3+R3 呼出修改菜单，修改项已全面恢复生效！")
        print("=" * 60)
        return True
    finally:
        kernel32.CloseHandle(hProcess)

if __name__ == "__main__":
    pid = get_process_by_name("bb-probe.exe")
    if not pid:
        print("[-] 未检测到正在运行的血源诅咒进程 (bb-probe.exe)。")
        print("    请先启动游戏，或使用离线配置修复方案。")
        sys.exit(1)
    print(f"[+] 检测到游戏进程 PID: {pid}")
    apply_hotpatch(pid)
