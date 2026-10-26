import pefile

pe = pefile.PE(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe")
base_va = pe.OPTIONAL_HEADER.ImageBase
target_va = 0x1438b70f5

# Let's check 0x1438b70f0 to 0x1438b7100
# Target2 is a pointer, aligned to 8 bytes: 0x1438b70f0 or 0x1438b70f8?
# In 0x1403fe2ed: 48 c7 05 fd 8d 4b 03 00 00 00 00
# instr end = 0x1403fe2f8. 0x1403fe2f8 + 0x034b8dfd = 0x1438b70f5.
# Wait! 48 c7 05 is mov qword ptr [rip+disp], imm32
# If disp is 0x034b8dfd, rip is 0x1403fe2f8.
# 0x1403fe2f8 + 0x034b8dfd:
# 0x2f8 + 0xdfd = 0x10f5!
# Wait! Why is it an unaligned address 0x1438b70f5?
# Let's check the exact bytes:
with open(r"E:\Game\PC\BloodbornePC\engine\out\bb-probe.exe", "rb") as f:
    f.seek(pe.get_offset_from_rva(0x3fe2ed))
    raw = f.read(20)
print("Bytes at 0x1403fe2ed:", raw.hex())
