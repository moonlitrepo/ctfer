# crackmes.one-simple XOR crackme

# overview
<img width="983" height="581" alt="image" src="https://github.com/user-attachments/assets/43be253f-ae23-47f0-b820-5f13ebcfc4df" />

file program dari challenge ini membutuhkan 1 argumen unutk dapat dijalankan, argumen tersebut adalah key yang digunakan untuk bypass. nantinya argumen kita akan di compare dengan key encoded .

# analysis & exploit

```
┌──[reno@cybersec]──[~/ctf/rev/simplexor]
└[]> file crackme
crackme: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=5c4e8ac6d7a71eeda4b5ad18884d44161238cf58,
 for GNU/Linux 4.4.0, not stripped
┌──[reno@cybersec]──[~/ctf/rev/simplexor]
└[]> ./crackme
usage ./crackme "<key>"
┌──[reno@cybersec]──[~/ctf/rev/simplexor]
└[]> ./crackme 2fb92bf2vf9
Nope.
```

aku lanjutkan analisis dengan melakukan decompile menggunakan ghidra
```C

undefined8 main(int param_1,long param_2)

{
  byte *pbVar1;
  byte *pbVar2;
  byte *pbVar3;
  byte *pbVar4;
  byte *pbVar5;
  long in_FS_OFFSET;
  byte local_88 [32];
  byte local_68 [32];
  byte local_48 [32];
  byte local_28 [24];
  long local_10;
  
  pbVar2 = local_88;
  local_10 = *(long *)(in_FS_OFFSET + 40);
  if (param_1 == 2) {
    local_88[16] = 0;
    pbVar5 = local_68;
    local_68[16] = 0;
    pbVar1 = *(byte **)(param_2 + 8);
    pbVar4 = local_48;
    pbVar3 = local_28;
    local_48[16] = 0;
    local_28[16] = 0;
    local_88[0] = 94;
    local_88[1] = 54;
    local_88[2] = 50;
    local_88[3] = 40;
    local_88[4] = 65;
    local_88[5] = 121;
    local_88[6] = 38;
    local_88[7] = 51;
    local_88[8] = 96;
    local_88[9] = 114;
    local_88[10] = 55;
    local_88[11] = 106;
    local_88[12] = 124;
    local_88[13] = 81;
    local_88[14] = 125;
    local_88[15] = 62;
    local_68[0] = 54;
    local_68[1] = 105;
    local_68[2] = 117;
    local_68[3] = 55;
    local_68[4] = 40;
    local_68[5] = 105;
    local_68[6] = 85;
    local_68[7] = 66;
    local_68[8] = 112;
    local_68[9] = 68;
    local_68[10] = 36;
    local_68[11] = 57;
    local_68[12] = 75;
    local_68[13] = 108;
    local_68[14] = 73;
    local_68[15] = 67;
    local_48[0] = 58;
    local_48[1] = 118;
    local_48[2] = 84;
    local_48[3] = 51;
    local_48[4] = 63;
    local_48[5] = 91;
    local_48[6] = 90;
    local_48[7] = 125;
    local_48[8] = 99;
    local_48[9] = 86;
    local_48[10] = 39;
    local_48[11] = 111;
    local_48[12] = 102;
    local_48[13] = 56;
    local_48[14] = 63;
    local_48[15] = 67;
    local_28[0] = 51;
    local_28[1] = 75;
    local_28[2] = 112;
    local_28[3] = 42;
    local_28[4] = 51;
    local_28[5] = 43;
    local_28[6] = 78;
    local_28[7] = 100;
    local_28[8] = 106;
    local_28[9] = 120;
    local_28[10] = 95;
    local_28[11] = 41;
    local_28[12] = 64;
    local_28[13] = 107;
    local_28[14] = 100;
    local_28[15] = 78;
    do {
      if (*pbVar1 != (byte)(*pbVar2 ^ *pbVar3 ^ *pbVar5 ^ *pbVar4 ^ 32)) {
        puts("Nope.");
        goto LAB_00101176;
      }
      pbVar2 = pbVar2 + 1;
      pbVar5 = pbVar5 + 1;
      pbVar4 = pbVar4 + 1;
      pbVar3 = pbVar3 + 1;
      pbVar1 = pbVar1 + 1;
    } while (pbVar2 != local_88 + 16);
    puts("Pass valid!");
  }
  else {
    puts("usage ./crackme \"<key>\"");
  }
LAB_00101176:
  if (local_10 == *(long *)(in_FS_OFFSET + 40)) {
    return 0;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}
```
disini ternyata argumen kita akan di bandingkan dengan hasil xor yang sebenarnya cukup sederhana. aku tinggal menyalin xor itu ke skrip python untuk mendapatkan key nya.

```Python
local_88 = [94,54,50,40,65,121,38,51,96,114,55,106,124,81,125,62,54]
local_68 = [54,105,117,55,40,105,85,66,112,68,36,57,75,108,73,67]
local_48 = [58,118,84,51,63,91,90,125,99,86,39,111,102,56,63,67]
local_28 = [51,75,112,42,51,43,78,100,106,120,95,41,64,107,100,78]

result = []
for i in range(16):
    xored = local_88[i] ^ local_68[i] ^ local_48[i] ^ local_28[i] ^ 32
    result.append(xored)

print("".join([chr(i) for i in result]))
```
result : 
```
┌──[reno@cybersec]──[~/ctf/rev/simplexor]
└[]> python3 exploit.py
ABC&E@GH98K51NOP
┌──[reno@cybersec]──[~/ctf/rev/simplexor] [127]
└[]> ./crackme "ABC&E@GH98K51NOP"
Pass valid!
```
done 

key = `ABC&E@GH98K51NOP`
