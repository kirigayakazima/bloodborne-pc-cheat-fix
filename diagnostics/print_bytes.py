import pefile

pe = pefile.PE(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe")
base_va = pe.OPTIONAL_HEADER.ImageBase

def get_bytes(va, length):
    offset = pe.get_offset_from_rva(va - base_va)
    with open(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe", "rb") as f:
        f.seek(offset)
        return f.read(length)

chunk = get_bytes(0x1403fe2d0, 100)
for i in range(len(chunk)):
    va = 0x1403fe2d0 + i
    b = chunk[i:i+7]
    print(f"{hex(va)}: {b.hex()}")
