# picoCTF2022-unpackme.md

hello guys welcome to my write up

challenge picoctf tahun 2022 bernama unpackme ini adalah chall dasar atau pembuka untuk mengenalkan pada para reverse engineers kepada upx. 
jadi kita diberi file program elf yang akan menananyakan apa nomor favorit dia. jelas kita gatau. jadi kita harus membongkar program untuk mencari tahu alur program 
dan tentu saja nomor favorit nya.



# tools
- upx
- ghidra
- gdb (opsional)

# recon
kita diberi file program elf x86-64, saat di jalankan dia meminta nomor. 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(unpackme)
└> file unpackme-upx
unpackme-upx: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), statically linked, no section header
┌[rotalactf]-[LAPTOP-6QMID52F]-(unpackme)
└> ./unpackme-upx
What's my favorite number? 676767
Sorry, that's not it!
```
dari commanf file terlihat kalau ini bukan file program biasa karena tertulis no section header, ini menandakan kalalu struktur asli program di sembunyikan atau dikompres


jika kita lihat di ghidra tampilannya akan abstrak, dan nama fungsinya di strip (dihilangkan) :

<img width="959" height="403" alt="image" src="https://github.com/user-attachments/assets/477456f7-5126-4cfa-a85d-47e54c0cef21" />

karena nama fungsinya berubah menjadi FUN_00455307 dan semacamnya, jadi aku harus mengunpacknya menggunakan tools upx.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(unpackme)
└> upx -d -o omaga unpackme-upx
                       Ultimate Packer for eXecutables
                          Copyright (C) 1996 - 2024
UPX 4.2.2       Markus Oberhumer, Laszlo Molnar & John Reiser    Jan 3rd 2024

        File size         Ratio      Format      Name
   --------------------   ------   -----------   -----------
   1006445 <-    379188   37.68%   linux/amd64   omaga

Unpacked 1 file.
```

dengan begini file programnya harusnya sudah kembali ke awal / bentuk aslinya. ayo cek pakai ghidra lagi.
<img width="662" height="388" alt="image" src="https://github.com/user-attachments/assets/47b18726-8031-42d7-ae25-334ff16f1791" />

nah dengan begini source code progam kembali terlihat dengan jelas. ada baris penting juga yang hanya mendeskripsi flag jika input = **754635**
jadi inilah angka favorit nya.  

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(unpackme)
└> ./unpackme-upx
What's my favorite number? 754635
picoCTF{up><_m3_f7w_e510a27f}
```

done
flag = **picoCTF{up><_m3_f7w_e510a27f}**

nah jadi itulah proses pengerjaan nya jika menggunakan ghidra. sangat mudah bukan? aku akan jelaskan gimana cara mengerjakan ini dengan gdb dan brute force. tapi sebelum itu 
aku akan bahas how it works , mengenai upxnya

# how it works

upx memiliki kepanjangan ultimate packer for executable. sesuai namanya dia bisa 'membungkus' file program hingga ukurannya menyusut dan dapat bekerja lebih efisien. dengan efek 
samping semua fungsi bahkan source code itu sendiri akan menghilang (stripped) dan tidak dapat terdeteksi jika di decompile atau bahkan jika di disassembly.

untuk melakukan pack bisa pakai tools upx yang bisa diinstall dengan  

```
sudo apt install upx
```
cara pakai 
```
upx <nama_file_elf/executable>

```
contoh : 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(unpackme)
└> upx omaga
                       Ultimate Packer for eXecutables
                          Copyright (C) 1996 - 2024
UPX 4.2.2       Markus Oberhumer, Laszlo Molnar & John Reiser    Jan 3rd 2024

        File size         Ratio      Format      Name
   --------------------   ------   -----------   -----------
   1002528 ->    379636   37.87%   linux/amd64   omaga

Packed 1 file.
```

jika cara me unpacknya, bisa pakai flag -d . atau ditambahi dengan -o untuk output file baru.
contoh : 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(unpackme)
└> upx -d omaga
                       Ultimate Packer for eXecutables
                          Copyright (C) 1996 - 2024
UPX 4.2.2       Markus Oberhumer, Laszlo Molnar & John Reiser    Jan 3rd 2024

        File size         Ratio      Format      Name
   --------------------   ------   -----------   -----------
   1006445 <-    379636   37.72%   linux/amd64   omaga

Unpacked 1 file.
```

kurang lebih begitu cara pakai upx nya.



# solve via gdb 

jika tertarik dengan tantangan dan suka bahasa assembly, boleh baca ini dikit.
pertama unpack dulu file programnya lalu baca hasil disassembly-nya , terutama fungsi main untuk melihat alur programnya
```assembly
pwndbg> file omaga
Reading symbols from omaga...
(No debugging symbols found in omaga)
pwndbg> disas main
Dump of assembler code for function main:
   0x0000000000401e43 <+0>:     endbr64
   0x0000000000401e47 <+4>:     push   rbp
   0x0000000000401e48 <+5>:     mov    rbp,rsp
   0x0000000000401e4b <+8>:     sub    rsp,0x50
   0x0000000000401e4f <+12>:    mov    DWORD PTR [rbp-0x44],edi
   0x0000000000401e52 <+15>:    mov    QWORD PTR [rbp-0x50],rsi
   0x0000000000401e56 <+19>:    mov    rax,QWORD PTR fs:0x28
   0x0000000000401e5f <+28>:    mov    QWORD PTR [rbp-0x8],rax
   0x0000000000401e63 <+32>:    xor    eax,eax
   0x0000000000401e65 <+34>:    movabs rax,0x4c75257240343a41
   0x0000000000401e6f <+44>:    movabs rdx,0x30623e306b6d4146
   0x0000000000401e79 <+54>:    mov    QWORD PTR [rbp-0x30],rax
   0x0000000000401e7d <+58>:    mov    QWORD PTR [rbp-0x28],rdx
   0x0000000000401e81 <+62>:    movabs rax,0x5f60643630486637
   0x0000000000401e8b <+72>:    mov    QWORD PTR [rbp-0x20],rax
   0x0000000000401e8f <+76>:    mov    DWORD PTR [rbp-0x18],0x37666132
   0x0000000000401e96 <+83>:    mov    WORD PTR [rbp-0x14],0x4e
   0x0000000000401e9c <+89>:    lea    rdi,[rip+0xb1161]        # 0x4b3004
   0x0000000000401ea3 <+96>:    mov    eax,0x0
   0x0000000000401ea8 <+101>:   call   0x410ba0 <printf>
   0x0000000000401ead <+106>:   lea    rax,[rbp-0x3c]
   0x0000000000401eb1 <+110>:   mov    rsi,rax
   0x0000000000401eb4 <+113>:   lea    rdi,[rip+0xb1165]        # 0x4b3020
   0x0000000000401ebb <+120>:   mov    eax,0x0
   0x0000000000401ec0 <+125>:   call   0x410d30 <__isoc99_scanf>
   0x0000000000401ec5 <+130>:   mov    eax,DWORD PTR [rbp-0x3c]
   0x0000000000401ec8 <+133>:   cmp    eax,0xb83cb
   0x0000000000401ecd <+138>:   jne    0x401f12 <main+207>
   0x0000000000401ecf <+140>:   lea    rax,[rbp-0x30]
   0x0000000000401ed3 <+144>:   mov    rsi,rax
   0x0000000000401ed6 <+147>:   mov    edi,0x0
   0x0000000000401edb <+152>:   call   0x401d85 <rotate_encrypt>
   0x0000000000401ee0 <+157>:   mov    QWORD PTR [rbp-0x38],rax
   0x0000000000401ee4 <+161>:   mov    rdx,QWORD PTR [rip+0xdd7e5]        # 0x4df6d0 <stdout>
   0x0000000000401eeb <+168>:   mov    rax,QWORD PTR [rbp-0x38]
   0x0000000000401eef <+172>:   mov    rsi,rdx
   0x0000000000401ef2 <+175>:   mov    rdi,rax
   0x0000000000401ef5 <+178>:   call   0x420980 <fputs>
   0x0000000000401efa <+183>:   mov    edi,0xa
   0x0000000000401eff <+188>:   call   0x420e20 <putchar>
   0x0000000000401f04 <+193>:   mov    rax,QWORD PTR [rbp-0x38]
   0x0000000000401f08 <+197>:   mov    rdi,rax
   0x0000000000401f0b <+200>:   call   0x42ec70 <free>
   0x0000000000401f10 <+205>:   jmp    0x401f1e <main+219>
   0x0000000000401f12 <+207>:   lea    rdi,[rip+0xb110a]        # 0x4b3023
   0x0000000000401f19 <+214>:   call   0x420c40 <puts>
   0x0000000000401f1e <+219>:   mov    eax,0x0
   0x0000000000401f23 <+224>:   mov    rcx,QWORD PTR [rbp-0x8]
   0x0000000000401f27 <+228>:   xor    rcx,QWORD PTR fs:0x28
   0x0000000000401f30 <+237>:   je     0x401f37 <main+244>
   0x0000000000401f32 <+239>:   call   0x45cba0 <__stack_chk_fail_local>
   0x0000000000401f37 <+244>:   leave
   0x0000000000401f38 <+245>:   ret
End of assembler dump.
```
seperti biasa assembly terlihat mengerikan, namun tidak perlu baca semua sampai pusing, cukup fokus ke bagian mana yang mengurusi input kita.
anggap saja kita belum tahu source c nya. jadi kemungkinan fungsi yang digunakan untuk membaca dan menyimpan input user adalah scanf, gets, fgets, read. dan sebagainya.
biasanya mereka adalah fungsi standart yang sering digunakan untuk urusan input.  

setelah mencari rupanya ada fungsi scanf di main+125
```assembly
   0x0000000000401ead <+106>:   lea    rax,[rbp-0x3c]
   0x0000000000401eb1 <+110>:   mov    rsi,rax
   0x0000000000401eb4 <+113>:   lea    rdi,[rip+0xb1165]        # 0x4b3020
   0x0000000000401ebb <+120>:   mov    eax,0x0
   0x0000000000401ec0 <+125>:   call   0x410d30 <__isoc99_scanf>
   0x0000000000401ec5 <+130>:   mov    eax,DWORD PTR [rbp-0x3c]
   0x0000000000401ec8 <+133>:   cmp    eax,0xb83cb
   0x0000000000401ecd <+138>:   jne    0x401f12 <main+207>
```
karena ini adalah program 64 bit , maka argumen akan ditangani olehregister seperti rdi, rsi, rdx , dan seterusnya. jika melihat ke barus main+106 dan main +110 . rsi berisi
alamat stack di rbp-0x3c. nah jadi kita tinggal fokus aja ke alamat ini. namun kenapa bisa rbp-0x3c? kok bisa tau dari mana? cara analisisnya akan ku jelaskan di how it works.

# exploit
sekarang adalah gimana cara kita nyari nomor favoritnya dan melakukan exploit. kita udah punya data bahwa input disimpan di rbp-0x3c. tinggal ikuti dulu gimana alur programnya
.rupanya tepat setelah scanf , stack yang menyimpan input kita sudah dipanggil lagi.
```assembly
   0x0000000000401ec5 <+130>:   mov    eax,DWORD PTR [rbp-0x3c]
   0x0000000000401ec8 <+133>:   cmp    eax,0xb83cb
   0x0000000000401ecd <+138>:   jne    0x401f12 <main+207>
```
isi input kita akan dimasukkan ke registers eax lalu compare dengan **0xb83cb** dibawahnya jika eax tidak sama dengan nilai tersebut mana program akan melompat ke main+207
dimana main+207 menuju akhir program dan hanya melakukan print, tidak melakukan rotate_encrypt. bisa disimpulkan bahwa program ingin kita menginput nilai 0xb83cb ini agar kita
bisa mentrigger fungsi rotate_encrypt tersebut. 0xb83cb dalam desimal adalah 754635. angka inilah yang kita input

```
pwndbg> r
Starting program: /home/rotalactf/reno/rev/unpackme/omaga
What's my favorite number? 754635
picoCTF{up><_m3_f7w_e510a27f}
[Inferior 1 (process 7307) exited normally]
pwndbg>
```
done as usual


# how it works?
```assembly
   0x0000000000401ead <+106>:   lea    rax,[rbp-0x3c]
   0x0000000000401eb1 <+110>:   mov    rsi,rax
   0x0000000000401eb4 <+113>:   lea    rdi,[rip+0xb1165]        # 0x4b3020
   0x0000000000401ebb <+120>:   mov    eax,0x0
   0x0000000000401ec0 <+125>:   call   0x410d30 <__isoc99_scanf>
```
ini adalah proses pemanggilan scanf standart. seperti yang kita tahu scanf memiliki 2 argumen, yaitu format string dan alamat memory / variabel  
**scanf("penentu_format", &nama_variabel);**  

nah dalam bahasa assembly jika program ingin memanggil fungsi yang membutuhkan argumen seperti scanf ini, ia harus memasukkan nilainya ke register dulu. untuk argumen
1 dan 2, register yang digunakan adalah rdi dan rsi. jadi nilai atau value argumen harus ada didalam register itu sebelum program melakukan call fungsi. 

argumen 2
```assembly
   0x0000000000401ead <+106>:   lea    rax,[rbp-0x3c]
   0x0000000000401eb1 <+110>:   mov    rsi,rax
```
assembly ini memasukkan nilai alamat dari rbp-0x3c ke dalam rax lalu rax dimasukkan kedalam rsi. maka rsi = rbp-0x3c (ini alamat kosong / variabel kosong untuk input)  
kenapa tau kalau kosong. karena rbp-0x3c merupakan area di stack yang sudah di deklarasikan sebagai tempat variabel yang akan menerima input kita.  

argumen 1
```assembly
   0x0000000000401eb4 <+113>:   lea    rdi,[rip+0xb1165]        # 0x4b3020
```
kalau yang ini adalah format stringnya. karena ada di argumen pertama , maka rdi = [rip+0xb1165]  . kok tau kalo ini format string? kita bisa cari tau ini isinya apa di gdb 
```
pwndbg> x/s $rip+0xb1165
0x4b3020:       "%d"
```
isinya "%d" . nah jadi jelas sekarang rdi = %d dan rsi = variabel, dengan gini scanf nya akan jadi fungsi yang valid untuk di panggil karena kedua argumennya sudah terpenuhi. dimana variabel 
= rbp-0x3c

# solve via brute-force

