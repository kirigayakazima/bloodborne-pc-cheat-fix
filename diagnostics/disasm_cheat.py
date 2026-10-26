import pefile

pe = pefile.PE(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe")
base_va = pe.OPTIONAL_HEADER.ImageBase

def get_bytes(va, length):
    offset = pe.get_offset_from_rva(va - base_va)
    with open(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe", "rb") as f:
        f.seek(offset)
        return f.read(length)

# Read 0x1403fe280 to 0x1403fe900
code = get_bytes(0x1403fe280, 0x1403fe900 - 0x1403fe280)
print("Code len:", len(code))

# Let's search all strings in .rdata referenced in this function
rdata_sec = [s for s in pe.sections if s.Name.startswith(b".rdata")][0]
rdata_va = base_va + rdata_sec.VirtualAddress
rdata_len = rdata_sec.SizeOfRawData
rdata = rdata_sec.get_data()

for i in range(len(code)-7):
    disp = int.from_bytes(code[i+3:i+7], byteorder="little", signed=True)
    target = 0x1403fe280 + i + 7 + disp
    if rdata_va <= target < rdata_va + rdata_len:
        ro_off = target - rdata_va
        s = rdata[ro_off:ro_off+100].split(b"\x00")[0]
        if len(s) > 2 and all(32 <= b < 127 for b in s):
            print(f"At {hex(0x1403fe280 + i)} -> {hex(target)}: {s.decode('latin1', errors='ignore')}")
