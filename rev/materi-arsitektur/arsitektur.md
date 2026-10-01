# arsitektur

## perbedaan arsitektur x86 dengan ARM 

source code untuk bahan analisis dibuat menggunakan bahasa C. hanya program dengan rumus sederhana yaitu **(a+b*c)** : 

- calc.c
```C
#include <stdio.h>

int add(int a, int b, int c) {
    return a + b * c;
}

int main(void) {
    int r = add(2, 3, 4);
    printf("hasil = %d\n", r);
    return 0;
}
```

## compile x86 & x86-64
```
gcc -m32 -O0 -fno-pie -no-pie -o calc_x86 calc.c  # x86 32-bit (cdecl)
gcc -O0 -fno-pie -no-pie -o calc_x64 calc.c # # x86-64 (System V)
```

## compile arm & arm64
```
arm-linux-gnueabihf-gcc -O0 -static -o calc_arm32 calc.c   # ARM32
aarch64-linux-gnu-gcc   -O0 -static -o calc_arm64 calc.c   # ARM64
```
___
# analysis calling convention cdecl | x86
main()
```Assembly
   0x0804918a <+17>:    push   0x4
   0x0804918c <+19>:    push   0x3
   0x0804918e <+21>:    push   0x2
   0x08049190 <+23>:    call   0x8049166 <add>
```
semua argumen akan di taruh di stack berurutan dari kanan ke kiri, jadi argumen pertama akan di push terakhir. : `add(2, 3, 4);` > push 4 , 3,baru  2.
add()
```Assembly
   0x08049169 <+3>:     mov    eax,DWORD PTR [ebp+0xc]
   0x0804916c <+6>:     imul   eax,DWORD PTR [ebp+0x10]
   0x08049170 <+10>:    mov    edx,eax
   0x08049172 <+12>:    mov    eax,DWORD PTR [ebp+0x8]
   0x08049175 <+15>:    add    eax,edx
```
argumen argumen yang di push akan masuk secara berurutan dari ebp+8 sebagai arg1, lalu ebp + 0xc sebagai arg2, dan ebp+0x10 sebagai arg3, dan seterusnya.

dimulai dari ebp+0x8 karena di ebp+0 ada saved ebp berukuran 4 byte, lalu ebp+0x4 ada eip, return address nya dan ini 4 byte juga, finally di ebp + 0x8 ada baru mulai argumen

setelah itu program ini akan memindah value di ebp + offset argumen itu ke eax untuk nanti dihitung dengan instruksi imul(kali) dan add(tambah).

```
mov    eax,DWORD PTR [ebp+0xc] <- argumen 2, artinya menyimpan nilai int 3 yang di pindah ke reg eax, eax = 3
imul   eax,DWORD PTR [ebp+0x10] <- argumen 3, menyimpan int 4, eax dikali 4 = 3 * 4 = 12, hasilnya disimpan di eax
mov    edx,eax <- 12 dipindah ke edx, edx = 12
mov    eax,DWORD PTR [ebp+0x8] <- eax yang tadi berisi 12 di timpa dengan value di arg1 yaitu int 2
add    eax,edx <- finally eax + edx = 2 + 12 = 14
```
prove 
```
pwndbg> c
Continuing.
hasil = 14
[Inferior 1 (process 6226) exited normally]
```

kesimpulan menurutku : pada arsitektur x86 , program akan menggunakan stack untuk mengisi argumen , argumen terakhir di push terlelbih dahulu dan argumen pertama di push terakhir
, di dalam fungsi penerima argumen, arg1 akan dimasukan mulai dari ebp + 0x8, tidak dari nol karena 8 byte sebelumnya ada saved ebp, dan eip. tiap argumen memiliki ukuran 4 byte.
jadi argumen 2 disimpan di ebp+0x8+4 , arg3 ebp+0x8+8, dan seterusnya. karena argumen disimpan di stack, maka proses perhitungan aritmatikanya langsung melibatkan stack.
contoh : `imul   eax,DWORD PTR [ebp+0x10]`.

___
# analysis calling convention system V | x86-64

main()
```Assembly
   0x0000000000401163 <+12>:    mov    edx,0x4
   0x0000000000401168 <+17>:    mov    esi,0x3
   0x000000000040116d <+22>:    mov    edi,0x2
   0x0000000000401172 <+27>:    call   0x401136 <add>
```
beda dengan cdecl, disini system V menggunakan register untuk argumen, jadi stack akan bersih dari argumen. maybe. nah disini sebenarnya gaada urutan pasti apakah harus edx dulu
rdi dulu atau esi dulu yang diisi, intinya saat fungsi dipanggil, jika fungsi butuh argumen maka register tersebut akan otomatia dianggap sebagai value argumen nya.
untuk urutan penginisiasiannya memang boleh bebas, tapi value nya tidak . 

urutan argumen di register
```
rdi > rsi > rdx > rcx > r8 > r9
```
namun jika value argumen ga gede gede amat maka yang dipake bukan rdi tapi edi, (32 bit) , biar hemat memory aja sih. tapi fungsinya masih sama, cuma beda ukuran.

sebagai penekanan , jika edi = 0x2 , maka angka 0x2 adalah argumen 1.  
add()
```asembbly
   0x000000000040113e <+8>:     mov    DWORD PTR [rbp-0x4],edi
   0x0000000000401141 <+11>:    mov    DWORD PTR [rbp-0x8],esi
   0x0000000000401144 <+14>:    mov    DWORD PTR [rbp-0xc],edx

   0x0000000000401147 <+17>:    mov    eax,DWORD PTR [rbp-0x8]
   0x000000000040114a <+20>:    imul   eax,DWORD PTR [rbp-0xc]
   0x000000000040114e <+24>:    mov    edx,eax
   0x0000000000401150 <+26>:    mov    eax,DWORD PTR [rbp-0x4]
   0x0000000000401153 <+29>:    add    eax,edx
```
kurang lebih pada system V isi instruksi nya tidak jauh beda dengan cdecl, hanya saja argumen ini disimpan di stack variabel lokal (offset minus) edi / arg1 disimpan di ebp-0x4
lalu esi di ebp-0x8 dan arg3 edx di ebp-0xc

sisanya sama.

kesimpulan : pada arsitektur x86-64, standart calling conventions nya adalah system V, dimana argumen fungsi akan menggunakan register bukan stack, dari rdi hingga r9, saat masuk
ke sebuah fungsi, argumen2 tersebut akan disimpan di stack, sesuai ukuran tipe data. karena int berukuran 4 byte ya disitu tiap argumen int nya bakal makan offset 4 byte per argumen

# analysis calling conventions ARM Procedure Call Standard | arm32

main()
```assembly
   0x0040052e <+6>:     movs    r2, #4
   0x00400530 <+8>:     movs    r1, #3
   0x00400532 <+10>:    movs    r0, #2
=> 0x00400534 <+12>:    bl      0x400504 <add>
```
di arm32 itu untuk urusan argumen sudah pakai register, disini r0 sebagai arg1 , lalu r1 sebagai arg2 dan seterusnya. untuk pemanggilan fungsi disini menggunakan
instruksi bl (branch with link) instruksi ini akan melompat ke fungsi tujuan dan otomatis menyimpan alamat pulang.

add()
```asembbly
   0x0040050a <+6>:     str     r0, [r7, #12]
   0x0040050c <+8>:     str     r1, [r7, #8]
   0x0040050e <+10>:    str     r2, [r7, #4]
   0x00400510 <+12>:    ldr     r3, [r7, #8]
   0x00400512 <+14>:    ldr     r2, [r7, #4]
   0x00400514 <+16>:    mul.w   r2, r3, r2
   0x00400518 <+20>:    ldr     r3, [r7, #12]
   0x0040051a <+22>:    add     r3, r2
   0x0040051c <+24>:    mov     r0, r3
   0x0040051e <+26>:    adds    r7, #20
```
nah di sini banyak perbedaan karena nama registernya beda, tapi sebenernya tujuannya sama aja si. tadi r0 menyimpan arg1 , yaitu 2, lalu r1 = 3 dan r2 = 4

instruksi str akan menyalin value register ke stack, disini stack nya r7+#12 untuk r0. lalu arg2 di r1 akan di store ke r7+8, terakhir arg 3 si r2 akan disimpen di r7+4,
lalu ada instruksi ldr, yaitu menyalin value di stack ke register, pertama program akan menyalin r7+4 dan r7+8 yang menyimpan angka 3 dan 4. lalu di kali dengan instruksi mul
lalu hasilperkaliannya disimpan di r2. maka r2 = r3*r2, r2 = 12,

program melakukan ldr lagi untuk menimpa value r3 yang sebelumnya bernilai 3 jadi ditimpa dengan 2 (value di r7+12), dan register r3 dan r2 dijumlah. maka 2 + 12 = 14

r3 dipindah ke r0 sebagai return value lalu stack di tutup (adds r7, 20) 
```
└> qemu-arm -L /usr/arm-linux-gnueabihf -g 2222 ./calc_arm32
hasil = 14
```
welldone

# analysis calling conventions ARM Procedure Call Standard | arm64 / aarch64

main()
```assembly
   0x00000000004007e4 <+8>:     mov     w2, #0x4                        // #4
   0x00000000004007e8 <+12>:    mov     w1, #0x3                        // #3
   0x00000000004007ec <+16>:    mov     w0, #0x2                        // #2
   0x00000000004007f0 <+20>:    bl      0x4007b0 <add>
```
kurang lebih sama , hanya saja nama register yang digunakan berbeda, pada arm64 bit, register berukuran full 64 bit menggunakan huruf w, sedangkan setengah alias 32 bit bukan r tapi
x, entah kenapa ga dibuat sama kek 32 bit, tapi aturannya begitu

add()
```assembly
   0x00000000004007b0 <+0>:     sub     sp, sp, #0x10
   0x00000000004007b4 <+4>:     str     w0, [sp, #12]
   0x00000000004007b8 <+8>:     str     w1, [sp, #8]
   0x00000000004007bc <+12>:    str     w2, [sp, #4]
   0x00000000004007c0 <+16>:    ldr     w1, [sp, #8]
   0x00000000004007c4 <+20>:    ldr     w0, [sp, #4]
   0x00000000004007c8 <+24>:    mul     w1, w1, w0
   0x00000000004007cc <+28>:    ldr     w0, [sp, #12]
   0x00000000004007d0 <+32>:    add     w0, w1, w0
   0x00000000004007d4 <+36>:    add     sp, sp, #0x10
   0x00000000004007d8 <+40>:    ret
```
ini adalah keseluruhan dari add function nya, cukup ringkas menurutku sehingga aku bisa mengcopynya disini.

disini rbp nya adalah sp, nama yang lebih jelas daripada r7 haha. terlihat di awal fungsi program ini menyiapkan stack berukuran 0x10 byte, kalau tidak salah ini 16 dalam desimal
lalu seperti biasa, program melakukan store register , menyimpan semua value argumen ke stack, masih sama untuk arg1 di sp+12, arg2 di sp+8 dan arg3 di sp+4. selisih 4 byte karena
int memang merupakan tipe data berukuran 4 byte.

lalu program mengambil value dari stack sp+8 dan +4 dan menyimpannya di w0 dan w1 untuk di kali, hasilnya akan disimppan di w1, jadi w1 = w1*w0. jika w1 adalah arg2 dam w0 arg3
maka w1 = 3*4 = 12

terakhir program load lagi dari sp+12 , ini arg1 bernilai 2. dan melakukan add. w0 = w1 + w0, maka w0 = 12 + 2 = 14

prove:
```
└> qemu-arm64 -L /usr/arm-linux-gnueabihf -g 2222 ./calc_arm64
hasil = 14
```


kesimpulan : walaupun tiap calling conventions menggunakan cara nya sendiri dalam mengelola data terutama argumen, tujuan utama mereka tetap sama yaitu ya memasukkan argumen ke dalam
fungsi dengan benar dan sesuai aturan nya.

# argumen pada x86-64 | system V
sederhana, untuk 6 argumen , system V menggunakan beberapa register mulai dari :
```
rdi : register destination, ini jadi arg 1
rsi : register source , ini jadi arg 2
rdx : jujur lupa, tapi dipake jadi arg3
rcx : counter ga si? buat loop atau lupa gw, ini arg4
r8 : general register  , arg 5
r9 : general register, arg 6

rax : ini untuk menyimpan hasil / return value dari fungsi atau perhitungan aritmatika
rip : register instruction pointer, register ini menunjuk ke bagian baris mana di asm yang sedang di eksekusi , dan saat itu terjadi ia menyimpan alamat setelah baris itu
(register yang menyimpan data 'mau kemana')
rbp : register base pointer, jadi base stack. klaim zona di memori
rsp : register stack pointer, ini mennunjuk ke rbp awalnya, jika stack membutuhkan suatu tempat berukuran tertentu, rsp akan dikurangi dan ia akan menunjuk ke ujung stack, sebagai
batas ujung stack. tapi biasanya jadi alamat awal input karena buffer biasanya disimpan dari akhir stack (alamat terkecil stack)
```

# epilog x86 & 64 bit
```asembbly
   0x000000000040115b <+4>:     push   rbp
   0x000000000040115c <+5>:     mov    rbp,rsp
   0x000000000040115f <+8>:     sub    rsp,0x10
```
sederhana, di awal fungsi , program sealu meletakkan register rbp untuk menandai awal stack, lalu memindah rsp agar menunjuk ke stack tersebut . terakhir menyiapkan ukuran stack
sesuai kebutuhan program . pada kasus ini rsp di kurangi 0x10, artinya rsp yang awalnya mennunjuk ke rbp akan turun ke rbp-0x10 / ujung stack sebagai pembatas bahwa alamat di rbp-0 hingga
rbp - 0x10 sudah dijadikan stack. ini penting agar program tidak melakukan timpa alamat yang sama yang dipakai stack ketika sedang menjalankan instruksi di stack lain.

# perbedaan utama x86 dan ARM 
perbedaan utama nya yang paling jelas adalah register tentunya. register yang digunakan memiliki nama yang berbeda walaupun fungsinya sama persis. misal jika di x86-64 register 
untuk argumen 1adalah rdi, di arm register tersebut dinamai r0, atau w0 jika di aarch 64. selain register perbedaan mencolok lainnya adalah namainstruksi dan cara kerjanya.
di x86-64 menggunakan mov dan menyalin value dari kanan ke kiri, sedangkan di arm untuk mengelola value register - stack menggunakan str dan ldr, str sendiri walaupun di bahasa 
assembly, tapi instruksinya lawan arah, dia menyalin value register di kiri ke kanan (stack) (str  r0,[r7,#8]). dan untuk memindah value dari stack ke register menggunakan instruksi
yang berbeda yaitu ldr (load register). 

## cdecl
ini standart calling conventions pada binary compile an C , x86. dimana semua argumen yang akan dimasukkan ke fungsi akan di masukkan ke stack dari kanan ke kiri, misal ada 3 argumen
maka argumen terakhir (3) akan di push dulu baru argumen 2 dan argumen pertama di push ke stack paling terakhir sebelum akhirnya call functions

## stdcall
ini versi jadulnya cdecl, biasanya dipake windows api, dan masih sama dia akan memasukkan argumen ke stack dari kanan kekiri sebelum melakukan call functions.

## fastcall
ini akan memasukkan arg1 dan arg2 ke register rcx dan rdx, jika lebih dari 2 sisanya dimasukkan ke stack.

