# -*- coding: utf-8 -*-
"""
血源诅咒 PC 移植版 (Lantern Engine) 修改器失效一键综合修复工具
"""

import os
import sys
import subprocess

def show_menu():
    print("=" * 65)
    print("      血源诅咒 PC 移植版 (Lantern Engine) 修改器失效修复工具")
    print("=" * 65)
    print("【失效原因排查总结】")
    print("  Lantern Engine 自带联机服务器（The Hunter's Dream）反作弊机制。")
    print("  当配置文件中 online_enabled=1 开启联机时，引擎会在日志中提示：")
    print("    'Cheats: off while playing online'")
    print("  并在运行时每帧主动清空修改器指针，导致所有修改项静默失效。")
    print("-" * 65)
    print("【可用修复方案】")
    print("  [1] 内存实时热修复 (推荐！游戏当前正在运行时使用，无需退出游戏)")
    print("  [2] 修改配置文件为离线模式 (推荐！关闭联机模式，原生恢复修改器)")
    print("  [3] 引擎核心二进制永久补丁 (修改 bb-probe.exe，联机离线均可用)")
    print("  [4] 还原引擎核心备份 (.bak)")
    print("  [5] 诊断当前游戏状态与配置")
    print("  [0] 退出")
    print("=" * 65)

def run_script(script_name, args=None):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    subprocess.run(cmd)

def main():
    while True:
        show_menu()
        choice = input("请输入选项编号 (0-5): ").strip()
        print()
        if choice == "1":
            run_script("hotpatch_live.py")
        elif choice == "2":
            run_script("fix_bb_config.py")
        elif choice == "3":
            run_script("patch_engine_binary.py")
        elif choice == "4":
            run_script("patch_engine_binary.py", ["restore"])
        elif choice == "5":
            run_script("check_live_process.py")
        elif choice == "0":
            break
        else:
            print("[-] 无效选项，请重新输入。")
        print()
        input("按 Enter 键继续...")
        print("\n" * 2)

if __name__ == "__main__":
    main()
