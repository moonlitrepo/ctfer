# Phun-Cing

# deskripsi
  Ok I'll wait until this CTF ends so that I will get the flag right? But why I couldn't
  run it on my machine? It works in author's machine ...

  author: aseng

**file attached** 

# analysis & exploit step by step

- melakukan identifikasi file dengan melihat metadata nya
<p align="center"><img  width="75%" height="70" alt="image" src="https://github.com/user-attachments/assets/e02db60a-7901-4190-99ea-71aa094274d0" /> </p>

file tersebut merupakan file binary dengan arsitektur **arm** . terlihat juga dari metadatanya tertulis `not stripped`, maka simbol yang ada di file binary tidak disembunyikan
dan akan terbaca dengan jelas oleh debugger atau decompiler.


- menjalankan file

<p align="center"> <img width="493" height="174" alt="image" src="https://github.com/user-attachments/assets/bc9b233f-3b35-42be-aeeb-69c1a3e2bac7" /> <p>

karena arsitektur arm memiliki instruksi yang berbeda dengan arsitektur x86 , untuk menjalankannya membutuhkan tools tambahan : `QEMU` 

namun file binary ini hanya melakukan print teks dan tidak melakukan apapun. untuk melannjutkan analisis dan mencari tahu apa yang sebenarnya dilakukan program , aku mendecompilenya dan melihat ke fungsi main :

```C
int __fastcall main(int argc, const char **argv, const char **envp)
{
  puts("Wait for a moment ... I promise I'll give you the flag in a moment ");
  sleep(0x2A30u);
  if ( ready_1 == 0 )
    getFlag_part_0();
  printf("Ok nice get your flag for this super ez one -> : %s\n", plain_0);
  return 0;
}
```
ternyata program ini melakukan sleep selama `0x2A30` (10800 dalam desimal) jadi setelah program dieksekusi, 3 jam kemudian ia akan memberikan flagnya. 

namun demi menyingkat waktu cukup lakukan patching dengan gdb

jalankan program secara lokal di port bebas :
`qemu-arm -L /usr/arm-linux-gnueabi -g 2222 ./wud`

buka terminal lain dan jalankan gdb
`gdb-multiarch`

hubungkan gdb ke server lokal 
`target remote localhost:2222`

selanjutnya adalah patching / merubah alur program sehingga ia tidak mengeksekusi sleep dan langsung melakukan print flag. untuk melakukannya dibutuhkan alamat target jump.

GDB  
`disas main`
```Assembly
   0x004004dc <+12>:    bl      0x4004ac <puts@plt>
   0x004004e0 <+16>:    ldr     r0, [pc, #56]   @ 0x400520 <main+80>
   0x004004e4 <+20>:    bl      0x4004a0 <sleep@plt>
   0x004004e8 <+24>:    ldr     r3, [pc, #52]   @ 0x400524 <main+84>
   0x004004ec <+28>:    add     r3, pc, r3
   0x004004f0 <+32>:    ldr     r3, [r3, #32]
   0x004004f4 <+36>:    cmp     r3, #0
   0x004004f8 <+40>:    bne     0x400500 <main+48>
   0x004004fc <+44>:    bl      0x400698 <getFlag.part.0>
```

maka target ku adalah jump ke alamat setelah sleep selesai dipanggil :
`   0x004004e8 <+24>:    ldr     r3, [pc, #52]` ----> `0x004004e8`

GDB
```
b main
c
j *0x004004e8
```

<p align="center"><img width="75%" height="90" alt="image" src="https://github.com/user-attachments/assets/6419087f-ec14-46ab-8e51-53c2bdd3079e" /> </p>


FLAG : LKS{.......................}



