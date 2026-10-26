import pefile

pe = pefile.PE(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe")
base_va = pe.OPTIONAL_HEADER.ImageBase

def get_bytes(va, length):
    offset = pe.get_offset_from_rva(va - base_va)
    with open(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe", "rb") as f:
        f.seek(offset)
        return f.read(length)

chunk = get_bytes(0x1403fe2f9, 60)
# 0x1403fe2f9:
# 8b 0d 09 62 c3 00 (mov ecx, [cheat_vials]) -> len 6
# 8b 05 07 62 c3 00 (mov eax, [cheat_bullets]) -> len 6
# 89 4d 38 (mov [rbp+0x38], ecx) -> len 3
# 89 45 3c (mov [rbp+0x3c], eax) -> len 3
# 48 8b 15 b6 8d 4b 03 (mov rdx, [rip+0x34b8db6]) -> len 7
# 48 85 d2 (test rdx, rdx) -> len 3
# 7f 10 (jg ...) -> len 2
# 48 8b 15 d2 8d 4b 03 (mov rdx, [rip+0x34b8dd2]) -> len 7
# 48 85 d2 (test rdx, rdx) -> len 3
# 0f 8e f1 0e 00 00 (jle ...) -> len 6

pos = 0x1403fe2f9 + 6 + 6 + 3 + 3
print("At first mov rdx:", hex(pos))
target1 = pos + 7 + 0x034b8db6
print("Target 1 read:", hex(target1))

pos += 7 + 3 + 2
print("At second mov rdx:", hex(pos))
target2 = pos + 7 + 0x034b8dd2
print("Target 2 read:", hex(target2))
