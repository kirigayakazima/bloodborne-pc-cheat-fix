import pefile

pe = pefile.PE(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe")
base_va = pe.OPTIONAL_HEADER.ImageBase

def find_xrefs(target_va):
    text_sec = [s for s in pe.sections if s.Name.startswith(b".text")][0]
    text_data = text_sec.get_data()
    text_va = base_va + text_sec.VirtualAddress
    for i in range(len(text_data)-7):
        disp = int.from_bytes(text_data[i+3:i+7], byteorder="little", signed=True)
        if text_va + i + 7 + disp == target_va:
            print(f"Xref to {hex(target_va)} at VA {hex(text_va + i)}: {text_data[i:i+7].hex()}")

# Let's find target_va
# Instruction was: 48 8b 15 b6 8d 4b 03 at 0x1403fe310
# instr end = 0x1403fe317. target = 0x1403fe317 + 0x034b8db6 = 0x1438b70cd?
# wait, let's calculate carefully:
instr_va = 0x1403fe30e
# 48 8b 15 b6 8d 4b 03:
# instr len 7: 0x1403fe30e + 7 = 0x1403fe315
# 0x1403fe315 + 0x034b8db6 = 0x1438b70cb
target1 = 0x1403fe315 + 0x034b8db6
target2 = 0x1403fe322 + 0x034b8dd2
print("Target 1:", hex(target1))
print("Target 2:", hex(target2))

find_xrefs(target1)
find_xrefs(target2)
