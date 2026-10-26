import pefile

pe = pefile.PE(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe")
base_va = pe.OPTIONAL_HEADER.ImageBase

def get_bytes(va, length):
    offset = pe.get_offset_from_rva(va - base_va)
    with open(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe", "rb") as f:
        f.seek(offset)
        return f.read(length)

chunk = get_bytes(0x1403fe2c0, 100)

# Let's inspect each instruction precisely:
# 0x1403fe2c0:
# 0fb6 05 49 3a c5 00 (movzx eax, byte ptr [rip+0xc53a49]) -> len 7
# 84 c0 (test al, al) -> len 2
# 0f 84 8f 33 00 00 (jz ...) -> len 6
# 44 0f b6 15 91 e2 4d 03 (movzx r10d, byte ptr [rip+0x34de291]) -> len 8
# 41 80 fa 01 (cmp r10b, 1) -> len 4
# 75 1c (jne +0x1c) -> len 2
# 48 c7 05 e0 8d 4b 03 00 00 00 00 (mov qword ptr [rip+0x34b8de0], 0) -> len 11
# 48 c7 05 fd 8d 4b 03 00 00 00 00 (mov qword ptr [rip+0x34b8dfd], 0) -> len 11
# 31 c9 (xor ecx, ecx) -> len 2
# 31 c0 (xor eax, eax) -> len 2
# eb 0c (jmp +0x0c) -> len 2
# 8b 0d 09 62 c3 00 (mov ecx, [cheat_vials]) -> len 6
# 8b 05 07 62 c3 00 (mov eax, [cheat_bullets]) -> len 6
# 89 4d 38 (mov [rbp+0x38], ecx) -> len 3
# 89 45 3c (mov [rbp+0x3c], eax) -> len 3

pos = 0x1403fe2c0 + 7 + 2 + 6
print("At online check start:", hex(pos))
# 44 0f b6 15 ... (len 8)
pos += 8
print("At cmp r10b, 1:", hex(pos))
# 41 80 fa 01 (len 4)
pos += 4
print("At jne:", hex(pos))
# 75 1c (len 2)
pos += 2
print("At mov 1:", hex(pos))
m1_target = pos + 11 + 0x034b8de0
print("m1_target:", hex(m1_target))
pos += 11
print("At mov 2:", hex(pos))
m2_target = pos + 11 + 0x034b8dfd
print("m2_target:", hex(m2_target))
pos += 11
print("At xor ecx:", hex(pos))
pos += 2 + 2 + 2 # xor, xor, jmp
print("At jne target (not online):", hex(pos))
