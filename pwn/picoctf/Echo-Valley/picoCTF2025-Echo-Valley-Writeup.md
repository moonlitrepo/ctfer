# picoCTF2025-Echo-Valley-Writeup

# chall info
name : Echo Valley   
category : Binary Exploitation   | Medium   
descryption :  

The echo valley is a simple function that echoes back whatever you say to it.

But how do you make it respond with something more interesting, like a flag?

file and nc connection attached

# recon & analysis
first download file binary dan source code yang terlampir. 

aku mulai static analysis dengan melihat metadata file , mengecek proteksi yang digunakan, dan menjalankan programnya.

<p align = "center"> <img width="1876" height="739" alt="image" src="https://github.com/user-attachments/assets/aecac151-bd09-4110-a16b-e53df7c3f9e1" />
</p>

program ini adalah elf 64 bit, dan ia menyediakan semacam layanan echo ,selain itu terdapat kerentanan format string pada layanan tersebut. ini dibuktikan dengan di cetaknya suatu alamat
memory random saat aku menginput %p. 

untuk melanjutkan analisis aku membaca source code terlampir.
```C
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void print_flag() {
    char buf[32];
    FILE *file = fopen("/home/valley/flag.txt", "r");

    if (file == NULL) {
      perror("Failed to open flag file");
      exit(EXIT_FAILURE);
    }

    fgets(buf, sizeof(buf), file);
    printf("Congrats! Here is your flag: %s", buf);
    fclose(file);
    exit(EXIT_SUCCESS);
}

void echo_valley() {
    printf("Welcome to the Echo Valley, Try Shouting: \n");

    char buf[100];

    while(1)
    {
        fflush(stdout);
        if (fgets(buf, sizeof(buf), stdin) == NULL) {
          printf("\nEOF detected. Exiting...\n");
          exit(0);
        }

        if (strcmp(buf, "exit\n") == 0) {
            printf("The Valley Disappears\n");
            break;
        }

        printf("You heard in the distance: ");
        printf(buf);
        fflush(stdout);
    }
    fflush(stdout);
}

int main()
{
    echo_valley();
    return 0;
}
```

semakin jelas bahwa kerentanan format string itu ada karena kesalahan pada fungsi echo_valley printf `printf(buf);`. 

program ini memiliki fungsi print_flag() namun tidak memanggilnya. maka aku tidak akan mendapatkan flag jika hanya dengan menjalankan program dengan alur normal.
maka aku harus memaksa memindah alur progam agar ia mengeksekusi printf itu.

aku bisa melakukannya dengan memanfaatkan kerentanan format string yang ada di fungsi echo_valley(). dengan me leak memory address stack / fungsi dan menghitung offsetnya.

leak data tersebut akan ku gunakan untuk menimpa return address dengan alamat memori print_flag() dan mendapatkan flagnya.






# step by step exploit

**gdb analaysis** 

aku coba buka gdb dan pasang breakpoint di fungsi echo_valley() karena target return address yang akan di timpa adalah return address dari fungsi tersebut.

setelah itu aku coba lihat frame dan coba leak beberapa alamat melalui format string. kabar baiknya terdapat alamat memory yang hanya berjarak 8 byte dari return address fungsi 
tersebut. itu adalah index ke 20. 

<p align="center"> <img width="949" height="365" alt="image" src="https://github.com/user-attachments/assets/1bded58a-9edf-4e78-ac09-17705d0f766b" />
</p>

target leak return address : `[leak index 20] - 8 byte`
ini akan berguna untuk skrip exploit akhir nanti.

**leak return address with python script**

aku melakukan otomasi dengan skrip python :
<p align = "center"><img width="395" height="239" alt="image" src="https://github.com/user-attachments/assets/c30da8d2-1adb-4e01-af0a-00cf8deca40e" />
 </p>

bonusnya dengan skrip python ini aku juga mendapatkan pie address dari main. cukup berguna untuk menghitung offset ke fungsi print_flag()


**menghitung offset print_flag()**   

aku kembali ke gdb untuk mencari alamat main dan print_flag() lalu menghitung offset / selisihnya

offset = main - print_flag

offset = 0x1401 - 0x1307 

offset = 250

**menghitung input index**

<img width="955" height="113" alt="image" src="https://github.com/user-attachments/assets/4d1d6ab5-4c72-47e2-9a7b-596f20dfdff4" />



 
