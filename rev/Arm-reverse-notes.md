# Arm-reverse-notes.md

cara menjalankan / run file arm di linux :

ARM 32-bit (armel):
`qemu-arm -L /usr/arm-linux-gnueabi ./nama_binary`

ARM 32-bit (armhf):
`qemu-arm -L /usr/arm-linux-gnueabihf ./nama_binary`

ARM 64-bit (aarch64):
`qemu-aarch64 -L /usr/aarch64-linux-gnu ./nama_binary`


# cara debug arm pakai gdb

1. buat server pakai qemu
  `qemu-arm -g 1234 -L /usr/arm-linux-gnueabi ./chall_arm32`
2. jalankan gdb lalu connect
   **note : lakuin di terminal baru**
   `gdb-multiarch ./chall_arm32`
   `target remote :1234`

it should work. 

# chall
buatan ai si, tapi lumayan untuk latihan compiling dan debugging 
```C
#include <stdio.h>
#include <unistd.h>
#include <string.h>

void check_register() {
    unsigned long reg_val = 0;

    // Membaca nilai dari register x19 di ARM64
    __asm__ volatile ("mov %0, x19" : "=r" (reg_val));

    if (reg_val == 0x1337) {
        printf("\n[+] Keren banget! Ini flag-nya: THPCTF{5l33p_byp4ss_4nd_r3g1st3r_m4n1pul4t10n}\n");
    } else {
        printf("\nSelamat sudah menunggu selama ini! Tapi sayang nilainya belum sesuai.\n");
    }
}

int main() {
    char nama[100];

    printf("Masukkan nama kamu: ");
    if (fgets(nama, sizeof(nama), stdin) != NULL) {
        // Hilangkan karakter newline di akhir string
        nama[strcspn(nama, "\n")] = 0;
    }

    printf("Halo, %s! Selamat datang.\n", nama);
    printf("Sedang memproses, mohon tunggu...\n");

    // Sleep selama 3600 detik (1 jam)
    sleep(3600);

    check_register();

    return 0;
}
```

cara compile :

aarch64 :
`aarch64-linux-gnu-gcc source.c -o binary`

sangat disarankan untuk melakukan split layar seperti dibawah ini, sebenernya beda tab gapapa si cuman biar cepet aja

<img width="960" height="600" alt="image" src="https://github.com/user-attachments/assets/e2d303a8-805f-454b-8b5d-e21b79275559" />

setelah melakukan target remote, harusnya kita bisa melakukan debugging seperti biasa, tapi perlu diingat, saat debuging remote tidak ada run, pakai continue. dan input output ada di panel server (punyaku yang kiri)yang kanan murni hanya untuk keperluan debugging.
