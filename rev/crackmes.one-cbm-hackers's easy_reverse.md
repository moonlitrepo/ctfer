# crackmes.one-cbm-hackers's easy_reverse

# overview
chall reverse dari `crackmes.one` buatan `cbm-hacker's` . 

Platform: Unix/linux etc.
Difficulty: 1.3
Quality: 4.7
Arch: x86-64

chall crackme sederhana yang membutuh kan value dan kondisi tertentu agar program melakukan print flag.


# analysis & exploit
karena info metadata sudah dijelaskan dari author soal, aku langsung menjalankan file programnya saja.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(crackme-easyreverse)
└> ./rev50_linux64-bit
USAGE: ./rev50_linux64-bit <password>
try again!
┌[rotalactf]-[LAPTOP-6QMID52F]-(crackme-easyreverse)
└> ./rev50_linux64-bit 1038f1
USAGE: ./rev50_linux64-bit <password>
try again!
```

sepertinya kita memerlukan password, aku lanjutkan analisis dengan GNU Debugger, karena tidak ada fungsi menarik jadi aku lakukan dissasembly pada fungsi mainnya saja
```Assembly
pwndbg> disas main
Dump of assembler code for function main:
   0x00000000000011c4 <+0>:     push   rbp
   0x00000000000011c5 <+1>:     mov    rbp,rsp
   0x00000000000011c8 <+4>:     sub    rsp,0x10
   0x00000000000011cc <+8>:     mov    DWORD PTR [rbp-0x4],edi
   0x00000000000011cf <+11>:    mov    QWORD PTR [rbp-0x10],rsi
   0x00000000000011d3 <+15>:    cmp    DWORD PTR [rbp-0x4],0x2
   0x00000000000011d7 <+19>:    jne    0x1257 <main+147>
   0x00000000000011d9 <+21>:    mov    rax,QWORD PTR [rbp-0x10]
   0x00000000000011dd <+25>:    add    rax,0x8
   0x00000000000011e1 <+29>:    mov    rax,QWORD PTR [rax]
   0x00000000000011e4 <+32>:    mov    rdi,rax
   0x00000000000011e7 <+35>:    call   0x1040 <strlen@plt>
   0x00000000000011ec <+40>:    cmp    rax,0xa
   0x00000000000011f0 <+44>:    jne    0x1246 <main+130>
   0x00000000000011f2 <+46>:    mov    rax,QWORD PTR [rbp-0x10]
   0x00000000000011f6 <+50>:    add    rax,0x8
   0x00000000000011fa <+54>:    mov    rax,QWORD PTR [rax]
   0x00000000000011fd <+57>:    add    rax,0x4
   0x0000000000001201 <+61>:    movzx  eax,BYTE PTR [rax]
   0x0000000000001204 <+64>:    cmp    al,0x40
   0x0000000000001206 <+66>:    jne    0x1235 <main+113>
   0x0000000000001208 <+68>:    lea    rdi,[rip+0xe16]        # 0x2025
   0x000000000000120f <+75>:    call   0x1030 <puts@plt>
   0x0000000000001214 <+80>:    mov    rax,QWORD PTR [rbp-0x10]
   0x0000000000001218 <+84>:    add    rax,0x8
   0x000000000000121c <+88>:    mov    rax,QWORD PTR [rax]
   0x000000000000121f <+91>:    mov    rsi,rax
   0x0000000000001222 <+94>:    lea    rdi,[rip+0xe07]        # 0x2030
   0x0000000000001229 <+101>:   mov    eax,0x0
   0x000000000000122e <+106>:   call   0x1050 <printf@plt>
   0x0000000000001233 <+111>:   jmp    0x1266 <main+162>
   0x0000000000001235 <+113>:   mov    rax,QWORD PTR [rbp-0x10]
   0x0000000000001239 <+117>:   mov    rax,QWORD PTR [rax]
   0x000000000000123c <+120>:   mov    rdi,rax
   0x000000000000123f <+123>:   call   0x118a <usage>
   0x0000000000001244 <+128>:   jmp    0x1266 <main+162>
   0x0000000000001246 <+130>:   mov    rax,QWORD PTR [rbp-0x10]
   0x000000000000124a <+134>:   mov    rax,QWORD PTR [rax]
   0x000000000000124d <+137>:   mov    rdi,rax
   0x0000000000001250 <+140>:   call   0x118a <usage>
   0x0000000000001255 <+145>:   jmp    0x1266 <main+162>
   0x0000000000001257 <+147>:   mov    rax,QWORD PTR [rbp-0x10]
   0x000000000000125b <+151>:   mov    rax,QWORD PTR [rax]
   0x000000000000125e <+154>:   mov    rdi,rax
   0x0000000000001261 <+157>:   call   0x118a <usage>
   0x0000000000001266 <+162>:   mov    eax,0x0
   0x000000000000126b <+167>:   leave
   0x000000000000126c <+168>:   ret
```

terlihat cukup merepotkan tapi jika diperhatikan lebih seksama, tidak semua baris ini berguna. untuk menganalisis hasil disassembly cukup amati fungsi apa saja yang dipanggil oleh
fungsi main ini karena fungsi yang dipanggil pasti akan dieksekusi jika kondisinya tercapai. berikut daftar fungsi yang dipanggil (call) oleh main  

`0x00000000000011e7 <+35>:    call   0x1040 <strlen@plt>` fungsi `strlen()`  mengecek panjang string  

`0x000000000000120f <+75>:    call   0x1030 <puts@plt>` fungsi `puts()`  melakukan output teks (mirip printf)  

`0x000000000000122e <+106>:   call   0x1050 <printf@plt>` fungsi `printf()`  (melakukan output teks)  

`0x000000000000123f <+123>:   call   0x118a <usage>`  
`0x0000000000001250 <+140>:   call   0x118a <usage>`  
`0x0000000000001261 <+157>:   call   0x118a <usage>` fungsi `usage()` ini adalah fungsi yang memeberi info **USAGE: ./rev50_linux64-bit password try again!**

dari sini kita bisa mengambil asumsi dan kesimpulan singkat. `hindari usage() tereksekusi agar program tidak berhenti` dan `paksa program mencapai ke kondisi yang membuat dia 
melakukan puts atau print`

jika kita melihat lagi di hasil disassemblynya 

---wu belum selesai---- 




