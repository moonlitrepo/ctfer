# ret2win-writeup

# step by step exploit
file attached : ret2win

gunakan gdb untuk melihat alur program dalam bahasa asembbly :

**fungsi yang ada : **
- main
- pwnme
- ret2win

fungsi ret2win adalah printflag namun fungsi ini tidak dipanggil sama sekali.

**vulnerable discover**
jika melihat ke fungsi `pwnme()` , ia menyiapkan buffer sebesar 0x20. namun terdapat fungsi read() yang akan membaca hingga 0x38. 

jika aku memasukkan karakter hingga lebih dari 20 byte misal 21 byte ke atas itu akan tetap valid namun akan terjadi buffer overflow 
dimana byte yang ku tulis akan menimpa alamat memori lain.

```Assembly
   0x00000000004006e8 <+0>:     push   rbp
   0x00000000004006e9 <+1>:     mov    rbp,rsp
   0x00000000004006ec <+4>:     sub    rsp,0x20
   .......................      ...    .........
   0x0000000000400737 <+79>:    mov    edx,0x38
   0x000000000040073c <+84>:    mov    rsi,rax
   0x000000000040073f <+87>:    mov    edi,0x0
   0x0000000000400744 <+92>:    call   0x400590 <read@plt>
```

namun kerentanan ini bisa digunakan untuk melakukan ret2win. rencananya aku akan menimpa return address dengan alamat memory fungsi `ret2win` agar saat fungsi pwnme() 
selesai dieksekusi, program akan melompat ke fungsi ret2win , bukan main. 

sebelum melakukannya perlu diperhatikan proteksi yang dimiliki program. 
```
pwndbg> checksec
File:     /home/rotalactf/reno/pwn/rop-emporium/ret2win/ret2win
Arch:     amd64
RELRO:      Partial RELRO
Stack:      No canary found
NX:         NX enabled
PIE:        No PIE (0x400000)
Stripped:   No
```
untungnya program ini tidak memiliki proteksi PIE sehingga alamat memory nya akan selalu sama, canary juga mati jadi progam ini benar benar rentan dengan buffer overflow.

aku membuat [skrip python](solver.py) untuk mengambil flagnya.

<p align ="center"><img width="854" height="433" alt="image" src="https://github.com/user-attachments/assets/f5e5558e-5340-410c-bdd2-a57689211fb2" />
 </p>
