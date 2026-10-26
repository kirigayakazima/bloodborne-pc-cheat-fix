import ctypes
from ctypes import wintypes
import sys

PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400

kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

pid = 23788 # current bb-probe pid
hProcess = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
if not hProcess:
    print("Failed to open process, error:", kernel32.GetLastError())
    sys.exit(1)

# Get base address of bb-probe.exe
hMods = (wintypes.HMODULE * 1024)()
cbNeeded = wintypes.DWORD()
if psapi.EnumProcessModules(hProcess, hMods, ctypes.sizeof(hMods), ctypes.byref(cbNeeded)):
    base_addr = hMods[0]
    print(f"Base address of bb-probe: {hex(base_addr)}")
else:
    print("EnumProcessModules failed")
    sys.exit(1)

def read_mem(addr, size):
    buf = ctypes.create_string_buffer(size)
    bytes_read = ctypes.c_size_t()
    if kernel32.ReadProcessMemory(hProcess, ctypes.c_void_p(addr), buf, size, ctypes.byref(bytes_read)):
        return buf.raw[:bytes_read.value]
    return None

# Offsets from PE ImageBase (0x140000000)
# online flag: 0x1438dc570 - 0x140000000 = 0x38dc570
online_flag_addr = base_addr + 0x38dc570
val_online = read_mem(online_flag_addr, 4)
print("Online flag at runtime:", val_online.hex() if val_online else "read error")

# pointer 2: 0x1438b70f4 - 0x140000000 = 0x38b70f4
ptr2_addr = base_addr + 0x38b70f4
val_ptr2 = read_mem(ptr2_addr, 8)
print("Ptr2 at runtime:", val_ptr2.hex() if val_ptr2 else "read error")

# cheat_vials: 0x141034510 - 0x140000000 = 0x1034510
vials_addr = base_addr + 0x1034510
val_vials = read_mem(vials_addr, 4)
print("cheat_vials at runtime:", int.from_bytes(val_vials, 'little') if val_vials else "read error")

# cheat_stamina: 0x141034518 - 0x140000000 = 0x1034518
stamina_addr = base_addr + 0x1034518
val_stamina = read_mem(stamina_addr, 1)
print("cheat_stamina at runtime:", int.from_bytes(val_stamina, 'little') if val_stamina else "read error")

kernel32.CloseHandle(hProcess)
