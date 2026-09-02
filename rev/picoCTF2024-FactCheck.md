# picoCTF2024-FactCheck.md

hello guys welcome back to my write up  

# summary
challenge pico kali ini adalah file program yang di compile dari bahasa C++ . dan program ini tidak mengembalikan flag ke layar. flag sudah ada di source code namun hanya setengahnya saja
sisanya akan ditambahkan manual satu per satu. namun tepat setelah flag lengkap, program justru menghapusnya lagi tanpa melakukan print sama sekali. bahkan saat dijalankan program ini
langsung selesai dalam waktu kurang dari 1 detik.  wkwkwkw

# tools
- gdb
- ghidra

# recon
pertama kita harus cari info sebanyak mungkin dari file program ini. mulai dari menjalannkan programnya dan mengecek metadata program tersebut.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(fastcheck)
└> file bin
bin: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=9b71e552659a84bdd5959009beb7735e6338f493, for GNU/Linux 3.2.0, not stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(fastcheck)
└> ./bin
┌[rotalactf]-[LAPTOP-6QMID52F]-(fastcheck)
└>
```
kabar baiknya program ini tidak di kompresi. kabar lainnya program tidak melakukan apa apa jadi kita tidak bisa mendapatkan info lagi jika hanya dengan menjalankan program 
tersebut. saat ku disas fungsi mainnya menggunakan gdb ternyata program ini di compile dari bahasa C++. dan barisnya banyak banget. main nya aja hingga+5000. mustahil dibaca manual
satu per satu.  

potongan program
```assembly
pwndbg> disas main
Dump of assembler code for function main:
   0x0000000000001289 <+0>:     endbr64
   0x000000000000128d <+4>:     push   rbp
   0x000000000000128e <+5>:     mov    rbp,rsp
   0x0000000000001291 <+8>:     push   rbx
   0x0000000000001292 <+9>:     sub    rsp,0x248
   0x0000000000001299 <+16>:    mov    rax,QWORD PTR fs:0x28
   0x00000000000012a2 <+25>:    mov    QWORD PTR [rbp-0x18],rax
   0x00000000000012a6 <+29>:    xor    eax,eax
   0x00000000000012a8 <+31>:    lea    rax,[rbp-0x241]
   0x00000000000012af <+38>:    mov    rdi,rax
   0x00000000000012b2 <+41>:    call   0x1180 <_ZNSaIcEC1Ev@plt>
   0x00000000000012b7 <+46>:    lea    rdx,[rbp-0x241]
   0x00000000000012be <+53>:    lea    rax,[rbp-0x240]
   0x00000000000012c5 <+60>:    lea    rsi,[rip+0xd39]        # 0x2005
   0x00000000000012cc <+67>:    mov    rdi,rax
   0x00000000000012cf <+70>:    call   0x1150 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC1EPKcRKS3_@plt>
```
at least kita tahu bahwa program ini dibuat dari bahasa C++. tapi tunggu dulu. lihat di **main+9**. program membuat stack dengan ukuran 0x248. besar banget . besar kemungkinan
flag akan di letakkan di stack. namun tetap saja aku tidak bisa jika membaca alur programnya dari gdb saja. jadi aku putuskan decompile pakai ghidra

```C++
/* WARNING: Removing unreachable block (ram,0x0010170c) */

undefined8 main(void)

{
  char cVar1;
  char *pcVar2;
  long in_FS_OFFSET;
  allocator local_249;
  string flag [32];
  string local_228 [32];
  string local_208 [32];
  string local_1e8 [32];
  string local_1c8 [32];
  string local_1a8 [32];
  string local_188 [32];
  string local_168 [32];
  string local_148 [32];
  string local_128 [32];
  string local_108 [32];
  string local_e8 [32];
  string local_c8 [32];
  string local_a8 [32];
  string local_88 [32];
  string local_68 [32];
  string local_48 [40];
  long local_20;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(flag,"picoCTF{wELF_d0N3_mate_",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_228,"4",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_208,"5",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_1e8,"6",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_1c8,"3",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_1a8,"e",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_188,"5",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_168,"a",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_148,"e",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_128,"e",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_108,"d",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_e8,"b",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_c8,"f",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_a8,"6",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_88,"e",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_68,"d",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_48,"8",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  pcVar2 = (char *)std::__cxx11::string::operator[]((ulong)local_208);
  if (*pcVar2 < 'B') {
    std::__cxx11::string::operator+=(flag,local_c8);
  }
  pcVar2 = (char *)std::__cxx11::string::operator[]((ulong)local_a8);
  if (*pcVar2 != 'A') {
    std::__cxx11::string::operator+=(flag,local_68);
  }
  pcVar2 = (char *)std::__cxx11::string::operator[]((ulong)local_1c8);
  cVar1 = *pcVar2;
  pcVar2 = (char *)std::__cxx11::string::operator[]((ulong)local_148);
  if ((int)cVar1 - (int)*pcVar2 == 3) {
    std::__cxx11::string::operator+=(flag,local_1c8);
  }
  std::__cxx11::string::operator+=(flag,local_1e8);
  std::__cxx11::string::operator+=(flag,local_188);
  pcVar2 = (char *)std::__cxx11::string::operator[]((ulong)local_168);
  if (*pcVar2 == 'G') {
    std::__cxx11::string::operator+=(flag,local_168);
  }
  std::__cxx11::string::operator+=(flag,local_1a8);
  std::__cxx11::string::operator+=(flag,local_88);
  std::__cxx11::string::operator+=(flag,local_228);
  std::__cxx11::string::operator+=(flag,local_128);
  std::__cxx11::string::operator+=(flag,'}');
  std::__cxx11::string::~string(local_48);
  std::__cxx11::string::~string(local_68);
  std::__cxx11::string::~string(local_88);
  std::__cxx11::string::~string(local_a8);
  std::__cxx11::string::~string(local_c8);
  std::__cxx11::string::~string(local_e8);
  std::__cxx11::string::~string(local_108);
  std::__cxx11::string::~string(local_128);
  std::__cxx11::string::~string(local_148);
  std::__cxx11::string::~string(local_168);
  std::__cxx11::string::~string(local_188);
  std::__cxx11::string::~string(local_1a8);
  std::__cxx11::string::~string(local_1c8);
  std::__cxx11::string::~string(local_1e8);
  std::__cxx11::string::~string(local_208);
  std::__cxx11::string::~string(local_228);
  std::__cxx11::string::~string(flag);
  if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
    return 0;
  }
                    /* WARNING: Subroutine does not return */
  __stack_chk_fail();
}
```

sangat banyak perulangannya. nah disini flagnya jelas banget: **picoCTF{wELF_d0N3_mate_** namun sayang hanya setengah. tapi tepat dibawahnya ada beberapa program yang memasukkan
value karakter random ke dalam sebuah variabel. 
```C++
 std::__cxx11::string::string(local_228,"4",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_208,"5",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_1e8,"6",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_1c8,"3",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_1a8,"e",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_188,"5",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_168,"a",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_148,"e",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_128,"e",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_108,"d",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_e8,"b",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_c8,"f",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_a8,"6",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_88,"e",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_68,"d",&local_249);
  std::allocator<char>::~allocator((allocator<char> *)&local_249);
  std::allocator<char>::allocator();
  std::__cxx11::string::string(local_48,"8",&local_249);
```
jika di ekstrak karakter tersebut maka akan jadi **456e5aeedbf6ed8** dan di bawah nya lagi beberapa baris kemudian ada baris program yang menambahkan karakter penutup flag
```C++
std::__cxx11::string::operator+=(flag,'}');
```
dan tepat setelah baris ini, adalah baris yang menghapus semua string flag dari stack.
```C++
  std::__cxx11::string::~string(local_48);
  std::__cxx11::string::~string(local_68);
  std::__cxx11::string::~string(local_88);
  std::__cxx11::string::~string(local_a8);
  std::__cxx11::string::~string(local_c8);
  std::__cxx11::string::~string(local_e8);
  std::__cxx11::string::~string(local_108);
  std::__cxx11::string::~string(local_128);
  std::__cxx11::string::~string(local_148);
  std::__cxx11::string::~string(local_168);
  std::__cxx11::string::~string(local_188);
  std::__cxx11::string::~string(local_1a8);
  std::__cxx11::string::~string(local_1c8);
  std::__cxx11::string::~string(local_1e8);
  std::__cxx11::string::~string(local_208);
  std::__cxx11::string::~string(local_228);
  std::__cxx11::string::~string(flag);
  if (local_20 == *(long *)(in_FS_OFFSET + 0x28)) {
    return 0;
  }
```

jika kita tambahkan ke flag tadi maka jadinya **picoCTF{wELF_d0N3_mate_456e5aeedbf6ed8}**  
done? sayangnya tidak. flag ini salah dan tidak valid di picoctf. mungkin ini adalah poin penting yang membuat nama chall ini factcheck. kita harus cari tau faktanya dulu. haha

jadi kenapa salah padahal semua itu dimasukkan ke variabel? nah jawabannya memang benar semua masuk ke variabel. tapi **tidak semua variabel ditambahkan ke flag**
```
  if (*pcVar2 < 'B') {
    std::__cxx11::string::operator+=(flag,local_c8);
  }
  pcVar2 = (char *)std::__cxx11::string::operator[]((ulong)local_a8);
  if (*pcVar2 != 'A') {
    std::__cxx11::string::operator+=(flag,local_68);
  }
  pcVar2 = (char *)std::__cxx11::string::operator[]((ulong)local_1c8);
  cVar1 = *pcVar2;
  pcVar2 = (char *)std::__cxx11::string::operator[]((ulong)local_148);
  if ((int)cVar1 - (int)*pcVar2 == 3) {
    std::__cxx11::string::operator+=(flag,local_1c8);
  }
  std::__cxx11::string::operator+=(flag,local_1e8);
  std::__cxx11::string::operator+=(flag,local_188);
  pcVar2 = (char *)std::__cxx11::string::operator[]((ulong)local_168);
  if (*pcVar2 == 'G') {
    std::__cxx11::string::operator+=(flag,local_168);
  }
  std::__cxx11::string::operator+=(flag,local_1a8);
  std::__cxx11::string::operator+=(flag,local_88);
  std::__cxx11::string::operator+=(flag,local_228);
  std::__cxx11::string::operator+=(flag,local_128);
```
jujur aku tidak terlalu memahami bahasa C++ tapi potongan program diatas bisa membuktikannya.

**TAPI, jika akhir flag adalah kurung kurawal penutup,( } ) maka bisa di asumsikan pada baris saat program menambahkan kurung kurawal tutup adalah baris saat flag dalam kondisi lengkap. jadi kita 
harus memaksa program berhenti saat kondisi itu. dan _membaca flagnya langsung dari stack_**

# exploit
langkah langkah exploit :  
- mencari kondisi saat flag utuh di gdb (asssembly)
- memaksa program berhenti di posisi itu
- membaca stack

aku bisa dengan mudah mencari bentuk disassemblynya dengan ghidra. 
<img width="768" height="491" alt="image" src="https://github.com/user-attachments/assets/9a92476c-c830-44f2-9c36-914b2aa4d901" />

jika kita melihat baris program yang menambahkan } ke flag. char } ditulis secara hardcode jadi ketika di asm ini akan tertulis juga namun dalam bentuk hex. jika aku cari tahu
dari tabel ascii, } = 0x7d dalam hex. dengan ciri ciri ini aku berhasil menemukan tempat
di program dimana kondisi flag dalam kondisi utuh :
```assembly
   0x000000000000184c <+1475>:  lea    rax,[rbp-0x240]
   0x0000000000001853 <+1482>:  mov    esi,0x7d
   0x0000000000001858 <+1487>:  mov    rdi,rax
   0x000000000000185b <+1490>:  call   0x1100 <_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEpLEc@plt>
   0x0000000000001860 <+1495>:  mov    ebx,0x0
   0x0000000000001865 <+1500>:  lea    rax,[rbp-0x40]
```
lihat pada main+1482 , disini program memasukkan 0x7d kedalam register esi. sebagai argumen kedua fungsi yang dipanggil di 1490. maka ini lah program yang kita cari
. maka kondisi saat flag utuh terjadi setelah fungsi di main+1490 dipanggil. yaitu di main+1495 .  

sudah ditentukan kondisi flag utuh ada di **main+1945 atau alamat memory 0x0000000000001860**  

masuk ke gdb dan pasang gdb di posisi tersebut.
```
pwndbg> b *main+1495
Breakpoint 1 at 0x1860
pwndbg> r
```
jika menggunakan pwndbg atau gef biasanya stack akan terbaca secara otomatis. namun kita bisa juga membacanya manual dengan stack  
```
pwndbg> stack
00:0000│ rsp     0x7fffffffdba0 ◂— 0
01:0008│-248     0x7fffffffdba8 ◂— 0
02:0010│ rax rdi 0x7fffffffdbb0 —▸ 0x55555556b2d0 ◂— 'picoCTF{wELF_d0N3_mate_fd65ee4e}'
03:0018│-238     0x7fffffffdbb8 ◂— 0x20 /* ' ' */
04:0020│-230     0x7fffffffdbc0 ◂— 0x2e /* '.' */
05:0028│-228     0x7fffffffdbc8 ◂— 0
06:0030│-220     0x7fffffffdbd0 —▸ 0x7fffffffdbe0 ◂— 0x34 /* '4' */
07:0038│-218     0x7fffffffdbd8 ◂— 1
```
done

**flag : picoCTF{wELF_d0N3_mate_fd65ee4e}**


# how it works
# conclusion
program ini membuat 
