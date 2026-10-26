import pefile

pe = pefile.PE(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe")
base_va = pe.OPTIONAL_HEADER.ImageBase

def get_bytes(va, length):
    offset = pe.get_offset_from_rva(va - base_va)
    with open(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe", "rb") as f:
        f.seek(offset)
        return f.read(length)

code = get_bytes(0x1403fe9e0, 0x1403feea0 - 0x1403fe9e0)
print("Code around 0x1403fe9e0..0x1403feea0:")
print(code.hex())
