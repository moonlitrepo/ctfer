# crackmes.one-senha-e-flag-C-2

# overview 
<img width="743" height="410" alt="image" src="https://github.com/user-attachments/assets/32c35261-0e98-48d4-8e90-7eb09319d20f" />

challenge ini memiliki password dan flag dalam kondisi terenkripsi dan bisa di solve dengan banyak cara seperti patching atau membuat keygen. namun program yang diberikan
sudah memiliki fungsi decodenya.

# analysis & exploit
pertama tentu analisis metadata dan fungsi yang ada di program tersebut.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(passwdandflag)
└> file senha-e-flag-C-2
senha-e-flag-C-2: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked,
interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=706c3a54f963cd43c02e337d3316fd80e765c185, for GNU/Linux 3.2.0, not stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(passwdandflag)
└> ./senha-e-flag-C-2
Insira sua senha: 123456789
Você errou hahahahah
```
sepertinya ini file  normal, saat di jalankan ia meminta sesuatu dalam bahasa portugis, `Insira sua senha` berarti `masukkan kata sandi anda` dalam bahasa indonesia.
aku coba gunakan ltrace untuk mencari info lebih lanjut.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(passwdandflag)
└> ltrace ./senha-e-flag-C-2
printf("Insira sua senha: ")                                                = 18
fflush(0x7e47002045c0Insira sua senha: )                                                      = 0
__isoc99_scanf(0x563049f2d017, 0x7fffd1fcc210, -1, 0x7e470011c6a4 123456789  <-- input user dilakukan dengan scanf() disini aku memasukkan 123456789
)          = 1
malloc(147)                                                                 = 0x563066bf0ac0
malloc(128)                                                                 = 0x563066bf0b60
memcpy(0x563066bf0b60, "\250\234(\032\261\270\323\344a\236\237\264S\323\aQ\004\016]\231\216\337\036\2300\206{+\225%\262="..., 128) = 0x563066bf0b60
malloc(8)                                                                   = 0x563066bf0bf0
malloc(19)                                                                  = 0x563066bf0c10
memcpy(0x563066bf0c10, "senhafoda1234567890", 19)                           = 0x563066bf0c10
strcmp("123456789", "senhafoda1234567890")                                  = -66
puts("Voc\303\252 errou hahahahah"Você errou hahahahah
)                                         = 22
free(0x563066bf0ac0)                                                        = <void>
+++ exited (status 0) +++
```
well jackpot, coba lihat baris ini.

```C
strcmp("123456789", "senhafoda1234567890")
```
disini input ku `123456789` dibandingkan dengan string `senhafoda1234567890`

sepertinya itu adalah password. jika bertanya kenapa aku berasumsi begitu ya karena ini adalah fungsi yang membandingkan input. pasti akan terjadi sesuatu yang berbeda 
jika input ku sesuai dengan apa yang diharapkan oleh program : `senhafoda1234567890` jadi kita bisa bypass kondisi ini.

<img width="423" height="71" alt="image" src="https://github.com/user-attachments/assets/25058949-62dd-4e9d-a3cf-9abd47eb4208" />


welldone

# note

sayang sekali kita tidak bisa membuat keygen untuk chall ini karena proses deskripsi menggunakan hash djb2 yangbersifat (irreversible). namun dari awal memang kita tidak perlu 
melakukannya karena program itu sudah melakukan decodenya saat akan membandingkan input kita. tinggal di leak saja pakai ltrace atau gdb.


