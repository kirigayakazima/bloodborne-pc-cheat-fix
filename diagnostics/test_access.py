import ctypes
from ctypes import wintypes
import time

PROCESS_ALL_ACCESS = 0x1F0FFF
kernel32 = ctypes.windll.kernel32

pid = 23788
hProcess = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
if not hProcess:
    print("Cannot open process with ALL_ACCESS, error:", kernel32.GetLastError())
    # try with VM_READ | VM_WRITE | VM_OPERATION
    hProcess = kernel32.OpenProcess(0x0010 | 0x0020 | 0x0008 | 0x0400, False, pid)
    print("Fallback open:", bool(hProcess))

if hProcess:
    base_addr = 0x140000000
    
    # 1. Check current online flag (0x1438dc570)
    online_flag_addr = 0x1438dc570
    buf = ctypes.create_string_buffer(4)
    kernel32.ReadProcessMemory(hProcess, ctypes.c_void_p(online_flag_addr), buf, 4, None)
    print("Current online_flag:", buf.raw.hex())
    
    # 2. Check instruction at 0x1403fe2db (75 1c -> jne not_online)
    jne_addr = 0x1403fe2db
    code_buf = ctypes.create_string_buffer(2)
    kernel32.ReadProcessMemory(hProcess, ctypes.c_void_p(jne_addr), code_buf, 2, None)
    print("Current opcode at 0x1403fe2db:", code_buf.raw.hex())
    
    # 3. Check Target2 pointer at 0x1438b70f0
    ptr2_addr = 0x1438b70f0
    pbuf = ctypes.create_string_buffer(8)
    kernel32.ReadProcessMemory(hProcess, ctypes.c_void_p(ptr2_addr), pbuf, 8, None)
    print("Current Target2:", hex(int.from_bytes(pbuf.raw, 'little')))
    
    kernel32.CloseHandle(hProcess)
