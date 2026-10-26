import pefile

pe = pefile.PE(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe")
base_va = pe.OPTIONAL_HEADER.ImageBase

def get_bytes(va, length):
    offset = pe.get_offset_from_rva(va - base_va)
    with open(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe", "rb") as f:
        f.seek(offset)
        return f.read(length)

chunk = get_bytes(0x140401650, 60)
print("0x140401650:", chunk.hex())
