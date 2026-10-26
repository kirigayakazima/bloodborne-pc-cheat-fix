import pefile

pe = pefile.PE(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe")
base_va = pe.OPTIONAL_HEADER.ImageBase
target_va = 0x1438b70f4

text_sec = [s for s in pe.sections if s.Name.startswith(b".text")][0]
text_data = text_sec.get_data()
text_va = base_va + text_sec.VirtualAddress

print("Searching for writes/refs to Ptr2 (0x1438b70f4)...")
for i in range(len(text_data)-7):
    # Check RIP relative with disp
    for d_off in (2, 3):
        disp = int.from_bytes(text_data[i+d_off:i+d_off+4], byteorder="little", signed=True)
        instr_end = text_va + i + d_off + 4
        if instr_end + disp == target_va:
            print(f"Ref at VA {hex(text_va + i)}: {text_data[i:i+d_off+4].hex()}")
