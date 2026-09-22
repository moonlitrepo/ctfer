# picoCTF2019-Forky-Writeup


# deskripsi
In this program, identify the last integer value that is passed as parameter to the function doNothing().

**hints : 
The flag is picoCTF{IntegerYouFound}. For example, if you found that the last integer passed was 1234, the flag would be picoCTF{1234}**

# analysis and exploit step by step

flag adalah parameter dari fungsi doNothing().

```
└> file vuln
vuln: ELF 32-bit LSB pie executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2,
 BuildID[sha1]=897dc1ea5877a9afff491aab96aa61503875e6bc, for GNU/Linux 3.2.0, not stripped

```

**ELF 32-bit** 
pada arsitektur ini, saat akan melakukan pemanggilan fungsi, argumennya akan diletakkan di stack melalui instruksi (biasanya) push registers. 

**target : leak value dari register yang di push tepat sebelum fungsi doNothing di panggil**

untuk melakukan dynamic analysis gunakan gdb :

main() : 

```Assembly
   0x00001287 <+125>:   sub    esp,0xc
   0x0000128a <+128>:   push   eax
   0x0000128b <+129>:   call   0x11ed <doNothing>
```
ternyata value dari parameter doNothing berasal dari register eax. maka telah terjadi perhitungan sebelumnya karena eax adalah register yang menyimpan return value dari suatu
fungsi.

aku akan pasang breakpoint di main+125 dan menjalankan instruksi hingga main+129.
```Assembly
   0x56556287 <+125>:   sub    esp,0xc
   0x5655628a <+128>:   push   eax
=> 0x5655628b <+129>:   call   0x565561ed <doNothing>
```
nice, sekarang value eax sudah ada di stack . lebih tepatnya di stack pointer saat ini. untuk me leak isinya bisa gunakan `stack` jika pakai gdb+pwntools atau `x/d $esp`

```
pwndbg> stack
00:0000│ esp 0xffffcf30 ◂— 0xd4faf720
01:0004│-024 0xffffcf34 —▸ 0xf7ffcb60 (_rtld_global_ro) ◂— 0

pwndbg> p/d 0xd4faf720
$1 = -721750240

pwndbg> x/d $esp
0xffffcf30:     -721750240
```

value parameter : `-721750240`

maka jika flag adalah picoCTF{value_parameter} maka 

**flag = picoCTF{-721750240}**
