import pefile

pe = pefile.PE(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe")
base_va = pe.OPTIONAL_HEADER.ImageBase

# Find function start of 0x1403fe280
# Let's search backward from 0x1403fe280 for 55 48 89 e5 or 48 83 ec or 55 41 57...
chunk = open(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe", "rb").read()
off = pe.get_offset_from_rva(0x3fe280)
# search back for 0xcc
start_off = off
while start_off > off - 0x1000 and chunk[start_off] != 0xcc:
    start_off -= 1
func_start_rva = pe.get_rva_from_offset(start_off + 1)
func_start_va = base_va + func_start_rva
print("Cheat function start VA:", hex(func_start_va))

text_sec = [s for s in pe.sections if s.Name.startswith(b".text")][0]
text_data = text_sec.get_data()
text_va = base_va + text_sec.VirtualAddress

for i in range(len(text_data)-5):
    if text_data[i] == 0xe8:
        disp = int.from_bytes(text_data[i+1:i+5], byteorder="little", signed=True)
        if text_va + i + 5 + disp == func_start_va:
            print(f"Caller at VA: {hex(text_va + i)}")
