# picoCTF2021-gogo

# overview
<img width="446" height="365" alt="image" src="https://github.com/user-attachments/assets/6cc63598-e946-4c5b-a714-fff8db91b4f0" />

file binary dan koneksi nc terlampir.

# analysis & exploit
<img width="957" height="112" alt="image" src="https://github.com/user-attachments/assets/9dce39b7-d950-4de7-a6ab-aec456c93e8e" />

file yang terlampir tersebut merupakan hasil compile dari bahasa **go** , dan sesuai namanya program ini meminta password. aku melanjutkan analisis menggunakan ghidra dan
menemukan fungsi menarik bernama `main.checkPassword`. ini adalah fungsi yang melakukan validasi input yang diberikan. 

```C
/* WARNING: Unknown calling convention */

void main.checkPassword(string input,bool ~r1)

{
  code *pcVar1;
  uint uVar2;
  int iVar3;
  int *in_GS_OFFSET;
  uint8 key [32];
  byte local_20 [28];
  undefined4 uStack_4;
  
  while (&stack0x00000000 <= *(undefined1 **)(*(int *)(*in_GS_OFFSET + -4) + 8)) {
    uStack_4 = 135089010;
    runtime.morestack_noctxt();
  }
  if (input.len < 32) {
    os.Exit(0);
  }
  FUN_08090b18();
  key[0] = 56;
  key[1] = 54;
  key[2] = 49;
  key[3] = 56;
  key[4] = 51;
  key[5] = 54;
  key[6] = 102;
  key[7] = 49;
  key[8] = 51;
  key[9] = 101;
  key[10] = 51;
  key[11] = 100;
  key[12] = 54;
  key[13] = 50;
  key[14] = 55;
  key[15] = 100;
  key[16] = 102;
  key[17] = 97;
  key[18] = 51;
  key[19] = 55;
  key[20] = 53;
  key[21] = 98;
  key[22] = 100;
  key[23] = 98;
  key[24] = 56;
  key[25] = 51;
  key[26] = 56;
  key[27] = 57;
  key[28] = 50;
  key[29] = 49;
  key[30] = 52;
  key[31] = 101;
  FUN_08090fe0();
  uVar2 = 0;
  iVar3 = 0;
  while( true ) {
    if (31 < (int)uVar2) {
      if (iVar3 == 32) {
        return;
      }
      return;
    }
    if (((uint)input.len <= uVar2) || (31 < uVar2)) break;
    if ((input.str[uVar2] ^ key[uVar2]) == local_20[uVar2]) {
      iVar3 = iVar3 + 1;
    }
    uVar2 = uVar2 + 1;
  }
  runtime.panicindex();
                    /* WARNING: Does not return */
  pcVar1 = (code *)invalidInstructionException();
  (*pcVar1)();
}
```

dari fungsi ini aku mendapatkan cukup banyak info yaitu:
- value key yang digunakan untuk validasi input 
- panjang input yang valid : (32 byte / 32 karakter)
- operasi validasi : (input ^ KEY == local_20) -> if true = login

input yang dimasukkan akan di xor dengan key terlampir dan di compare dengan `local_20`. karena value local_20 cukup sulit di ekstrak dari ghidra jadi aku melanjutkan analisis dengan GDB dan memasang breakpoint di instruksi tersebut untuk mencari valuenya. alamat instruksinya bisa ku dapatkan dengan mudah dengan ghidra

<img width="652" height="92" alt="image" src="https://github.com/user-attachments/assets/326ebf45-f294-46c5-a81c-6f8caabbcdb2" />

alamat : `080d4b28`

# gdb 

```
pwndbg> b *0x080d4b28
Breakpoint 1 at 0x80d4b28: file /app/enter_password.go, line 71.
pwndbg> cyclic 32
aaaabaaacaaadaaaeaaafaaagaaahaaa
pwndbg> r
Starting program: /pathpathpath/enter_password
[New LWP 5595]
[New LWP 5596]
[New LWP 5597]
[New LWP 5598]
Enter Password: aaaabaaacaaadaaaeaaafaaagaaahaaa
```

```Assemblly
   0x080d4b1f <+159>:   jae    0x80d4b66 <main.checkPassword+230>
   0x080d4b21 <+161>:   movzx  esi,BYTE PTR [esp+eax*1+0x4]
   0x080d4b26 <+166>:   xor    ebp,esi
=> 0x080d4b28 <+168>:   movzx  esi,BYTE PTR [esp+eax*1+0x24]
   0x080d4b2d <+173>:   xchg   ebp,eax
```
setelah berhenti di breakpoint, terlihat ini ada di dalam fungsi  `main.checkPassword` . bisa dilihat bahwa KEY dan result valuenya disimpan di `esp+0x4` dan `esp+0x24` 
<img width="752" height="171" alt="image" src="https://github.com/user-attachments/assets/566edb3c-403a-4c80-be4c-5de6a21a2401" />

kotak ungu adalah value dari local_20 dan kotak merah adalah keynya , mirip seperti yang terlampir di source code.

hex 2 digit itu adalah value yang disimpan dan di sebelah kanannya adalah character nya jika di print. beberapa merupakan printable character dan sisanya bytes random tapi value yang aku ekstrak hexnya aja. 

skrip piton
```Python
from pwn import *

context.log_level = "error"

raw_key = "38 36 31 38  33 36 66 31  33 65 33 64  36 32 37 64 66 61 33 37  35 62 64 62  38 33 38 39  32 31 34 65" #hex dari hexdump
raw_result = '4a 53 47 5d  41 45 03 54  5d 02 5a 0a  53 57 45 0d 05 00 5d 55  54 10 01 0e  41 55 57 4b  45 50 46 01' #sama, cuman yang ini itu resultnya 

key , result = raw_result.replace(" ",""), raw_key.replace(" ","")

data = xor(unhex(key),unhex(result))
print(data.decode())

```
penjelasan:
- jika validasi nya `input ^ KEY == local_20` maka untuk dapat nilai local_10 tinggal di xor saja jadi `local_20 ^ KEY == input`.
- untuk memudahkan proses xor dan manipulasi string hex aku menggunakan fungsi dari libc pwntools
- hasillnya tidak wajib di decode tapi jika tidak di lakukan nanti stringnya dibungkus dengan b'' (format bytes).

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(go_hard)
└> python3 exploit.py
reverseengineericanbarelyforward
┌[rotalactf]-[LAPTOP-6QMID52F]-(go_hard)
└> ./enter_password
Enter Password: reverseengineericanbarelyforward
=========================================
This challenge is interrupted by psociety
What is the unhashed key?

```
password = `reverseengineericanbarelyforward`
password ini valid dan aku berhasil bypass dengan lancar namun masih ada validasi ke dua, lebih ke pertanyaan random. `What is the unhashed key?` ?? jika dilihat lebih teliti ternyata string dari key memang terlihat seperti hash.

string key : `861836f13e3d627dfa375bdb8389214e`

untuk hash bisa gunakan tools online : crackstation 

<img width="959" height="460" alt="image" src="https://github.com/user-attachments/assets/cecdb618-0f46-4514-bcf4-b82e4d5e5315" />

rupanya itu adalah hash `md5` dan string aslinya adalah `goldfish`
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(go_hard)
└> ./enter_password
Enter Password: reverseengineericanbarelyforward
=========================================
This challenge is interrupted by psociety
What is the unhashed key?
goldfish
panic: open flag.txt: no such file or directory
```

panic but dont panic

<img width="380" height="147" alt="image" src="https://github.com/user-attachments/assets/ad15b4c3-3296-482c-b121-ad8240bcae11" />

flag : `picoCTF{p1kap1ka_p1c01a475a0d}`
# conclusion

challenge ini menguji kemampuan dasar dalam pembacaan bahasa pemrograman go dan assembly.
