# crackmes.one-really easy
# overview
Author: ezloom
Language: C/C++
Difficulty: 1.0
Quality: 4.6

# analysis & exploit
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(really-easy)
└> ./simp-password
Enter password: password
Wrong try again.
```
program meminta password. aku coba buka pakai gdb untuk melihat isi programnya. 
```Assembly
   0x0000000000001209 <+64>:    mov    eax,0x0
   0x000000000000120e <+69>:    call   0x10d0 <__isoc99_scanf@plt>
   0x0000000000001213 <+74>:    lea    rax,[rbp-0x40]
   0x0000000000001217 <+78>:    lea    rdx,[rip+0xdfc]        # 0x201a
   0x000000000000121e <+85>:    mov    rsi,rdx
   0x0000000000001221 <+88>:    mov    rdi,rax
   0x0000000000001224 <+91>:    call   0x10c0 <strcmp@plt>
```
berikut adalah potongan program di fungsi main yang akan membandingkan string di `rbp-0x40` dengan string yang ada di `rip + 0xdfc`. ini adalah pengecekan passwordnya karena 
string yang disimpan di rbp-0x40 adalah input ku . maka aku harus me leak apa isinya. dan ini cukup mudah dengan gnu debugger.
```Assembly
   0x555555555217 <main+78>     lea    rdx, [rip + 0xdfc]    
```
karena isi rip + 0xdfc dimasukkan ke rdx jadi aku baca isi register rdxnya
```
pwndbg> i r $rdx
rdx            0x55555555601a
pwndbg> x/s 0x55555555601a
0x55555555601a: "iloveicecream"
```

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(really-easy)
└> ./simp-password
Enter password: iloveicecream
I love ice cream too!
```
