# -*- coding: utf-8 -*-
"""
Bloodborne PC (Lantern Engine) - 配置文件修复脚本
通过关闭 lantern.ini 中的联机模式，彻底解除游戏内置的反作弊锁定。
"""

import os
import shutil

LANTERN_INI = r"E:\Game\PC\BloodbornePC\lantern.ini"

def fix_lantern_ini():
    if not os.path.exists(LANTERN_INI):
        print(f"[-] 未找到配置文件: {LANTERN_INI}")
        return False
    
    # 备份原始配置
    backup_path = LANTERN_INI + ".bak"
    if not os.path.exists(backup_path):
        shutil.copyfile(LANTERN_INI, backup_path)
        print(f"[+] 已创建原始配置备份: {backup_path}")
    
    with open(LANTERN_INI, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    new_lines = []
    modified = False
    
    keys_to_set_zero = {
        "online_enabled": "0",
        "online_connected": "0",
        "online_upnp": "0"
    }
    
    for line in lines:
        stripped = line.strip()
        replaced = False
        for k, v in keys_to_set_zero.items():
            if stripped.startswith(f"{k}="):
                old_val = stripped.split("=")[1]
                if old_val != v:
                    new_lines.append(f"{k}={v}\n")
                    print(f"[+] 配置项修改: {k}={old_val} -> {k}={v}")
                    modified = True
                    replaced = True
                break
        if not replaced:
            new_lines.append(line)
            
    if modified:
        with open(LANTERN_INI, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print("[+] 配置文件保存完成！联机模式已成功关闭。")
        print("    下次启动游戏时，引擎不再加载联机反作弊组件，所有修改器选项将自然生效。")
    else:
        print("[*] 配置文件中的联机选项已经处于关闭状态。")
        
    return True

if __name__ == "__main__":
    fix_lantern_ini()
