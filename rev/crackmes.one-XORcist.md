# crackmes.one-XORcist

# overview
<img width="736" height="409" alt="image" src="https://github.com/user-attachments/assets/b3d067f2-d6ed-491d-8f09-8e51cf30818a" />

challenge ini akan memberikan file program yang meminta password, ada dua cara untuk mencari tahu passwordnya, dengan membuat keygen atau membypass anti debugger dan melakukan
dynamic analysis.

# analysis & exploit

chall ini memberikan 3 file utama : `compile.sh` , `xorcist` , and `xorcist.c`. dimana compile.sh adalah kompiler dari xorcist.c menjadi file biner xorcist.  
kebetulan sudah ada source codenya jadi aku tidak perlu repot repot decompile.  


source code :
```C
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <unistd.h>

#define KEY 0xA9

void decrypt(char *str) {
    for (int i = 0; str[i]; i++) {
        str[i] ^= KEY;
    }
}

int isDebuggerPresent() {
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) return 0;

    char line[256];
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "TracerPid:", 10) == 0) {
            int pid = atoi(line + 10);
            fclose(f);
            return pid != 0;
        }
    }

    fclose(f);
    return 0;
}

typedef struct {
    int id;
    char name[16];
    int (*check_fn)(const char *);
} Agent;

int validate(const char *input) {
    const char *enc = "\xdd\xda\xf6\xd9\xc4\xc6\xf6\xce\xc7\xce\xf6\xc0\xca\xc5";
    char temp[16];
    strcpy(temp, enc);
    decrypt(temp);
    return strcmp(input, temp) == 0;
}

int useless_branch(int x) {
    if (x == 1337) return 1;
    if (x % 7 == 0) return 0;
    if (x % 42 == 0) return 0;
    return x == 1234;
}

int main() {
    if (isDebuggerPresent()) {
        printf("Nooooooo. La Policiaaa.\n");
        return 1;
    }

    Agent ag;
    ag.id = (rand() % 100) + 1; // Make sure it's never 0
    strcpy(ag.name, "root");
    ag.check_fn = &validate;

    char input[32];
    printf("What's the password?\n");
    fgets(input, sizeof(input), stdin);
    input[strcspn(input, "\n")] = 0;

    char c = (rand() % (126 - 32 + 1)) + 32;
    char c_str[2];
    c_str[0] = c;

    srand(time(NULL));
    int rand_val = rand() % 6969 + 1;
    int distract = useless_branch(rand_val);

    if (ag.check_fn(input) && ag.id != 0) {
        printf("Logged in as %s.\n", ag.name);
    } else {
        printf("Nuh Uh Nuh Uh.\n");
    }

    return 0;
}
```

terlihat seperti enkripsi rumit, tapi beberapa fungsi seperti rand() dan fungsi pengecekan lain itu palsu dan tidak benar benar merubah alur atau memengaruhi enkripsi.   
selain itu aku juga menemukan string yang berkemungkinan di inisiasikan sebagai password :
```C
const char *enc = "\xdd\xda\xf6\xd9\xc4\xc6\xf6\xce\xc7\xce\xf6\xc0\xca\xc5";
```
karena string ini akan di decrypt lalu dicompare dengan input kita. 
```C
#define KEY 0xA9

void decrypt(char *str) {
    for (int i = 0; str[i]; i++) {
        str[i] ^= KEY;
    }
}
```

tapi jika dilihat lihat lagi ternyata fungsi ini hanya menjalankan proses decrypt sederhana. yaitu tiap bytes / karakter dari plaintext di xor kan dengan `0xa9`. 

# solve with keygen
berikut skrip python untuk mendecryptnya.
```Python
enc = "\xdd\xda\xf6\xd9\xc4\xc6\xf6\xce\xc7\xce\xf6\xc0\xca\xc5"
decrypt = [ord(enc[i])^0xa9 for i in range(len(enc))]
print("".join([chr(i) for i in decrypt]))
```
result
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(XORcist)
└> python3 exploit.py
ts_pmo_gng_icl
┌[rotalactf]-[LAPTOP-6QMID52F]-(XORcist)
└> ./xorcist
What's the password?
ts_pmo_gng_icl
Logged in as root.
```
logged in as root as usual hahahahhahha.


# solve with gdb

jika ingin melakukan dynamic analysis program akan mendeteksi bahwa kita melakukan debug saat menjalankannya dengan mengeluarkan print teks `Nooooooo. La Policiaaa.`
<img width="584" height="113" alt="image" src="https://github.com/user-attachments/assets/a87c03b0-2ad9-4346-97b0-20049e8c44cd" />

kenapa ini bisa terjadi?   
karena ini:
```C
int isDebuggerPresent() {
    FILE *f = fopen("/proc/self/status", "r");
    if (!f) return 0;

    char line[256];
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "TracerPid:", 10) == 0) {
            int pid = atoi(line + 10);
            fclose(f);
            return pid != 0;
        }
    }

    fclose(f);
    return 0;
}

```
```
    if (isDebuggerPresent()) {
        printf("Nooooooo. La Policiaaa.\n");
        return 1;
    }
```
jadi cara bypassnya gimana? mudah. lihat ke fungsi main dan hapus / ubah fungsi pemanggilan anti debugger ini agar dia tidak diekseskusi saat program dijalankan.
<img width="374" height="162" alt="image" src="https://github.com/user-attachments/assets/07e6b915-0115-4be0-b71d-7413720a12b6" />



nah lalu compile lagi saja file sourcenya. kebetulan kita juga diberi file kompilenya . bisa dengan `gcc -s -o xorcist xorcist.c` atau jalankan file sh dari chall `sh compile.sh`
jadi sekarang aku sudah bisa melakukan dynamic analisis dengan tenang.

```
pwndbg> info functions
All defined functions:

Non-debugging symbols:
0x0000000000001110  __cxa_finalize@plt
0x0000000000001120  strncmp@plt
0x0000000000001130  strcpy@plt
0x0000000000001140  puts@plt
0x0000000000001150  fclose@plt
0x0000000000001160  __stack_chk_fail@plt
0x0000000000001170  printf@plt
0x0000000000001180  strcspn@plt
0x0000000000001190  srand@plt
0x00000000000011a0  fgets@plt
0x00000000000011b0  strcmp@plt
0x00000000000011c0  time@plt
0x00000000000011d0  fopen@plt
0x00000000000011e0  atoi@plt
0x00000000000011f0  rand@plt
```
disini tidak ada fungsi main, hm jadi aku akan pasang breakpoint di fungsi penting seperti `strcmp@plt`   
```
pwndbg> b strcmp@plt
Breakpoint 1 at 0x11b0
pwndbg> r
```
<img width="842" height="406" alt="image" src="https://github.com/user-attachments/assets/db2bac44-068e-4a27-ab04-1defee68de23" />

nah iya kan, string tadi muncul. tapi gimana cara membuktikannya? ada 2 bukti kuat, yang pertama. dia ada di stack saat program sedang break di strcmp. STRcmp. semua string
yang terlibat harus dicurigai. bukti ke 2 adalah ini :

<img width="582" height="134" alt="image" src="https://github.com/user-attachments/assets/176e5067-1e68-48ed-8110-2933ab981140" />

done as usual.


