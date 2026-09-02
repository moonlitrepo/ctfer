# picoCTF2024-Format string 0
hello guys welcome back to my write up
# overview
challenge pico kali ini adalah chall yang sangat sederhana dan hanya membutuhkan fundamental dalam ctf kategori binary exploitation. program ini akan menanyakan makanan apa yang cocok
untuk patrick, dan program ini juga memiliki beberapa kerentanan yang dapat menuju ke kondisi print flag. mari kita pwnini

# tools
- pwntools python libc (opsional)

# recon
<img width="503" height="404" alt="image" src="https://github.com/user-attachments/assets/b83f4d06-8bb4-46e8-8ce3-3d9309bb9228" />

disini ada file program , source code, dan dan koneksi ke servernya. langsung saja aku download semua dan analisis mulai dari metadata file dan menjalankannya.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string0)
└> ls
format-string-0  format-string-0.c
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string0)
└> file format-string-0
format-string-0: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=73480d84a806aebddd86602609fcab2052c8fa13, for GNU/Linux 3.2.0, not stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string0)
└> ./format-string-0
Please create 'flag.txt' in this directory with your own debugging flag.
```
hem untuk menjalankan programnya kita harus punya file flag.txt di directory yang sama dengan file program. itu bukan masalah besar, di meta data program juga tidak
ada yang aneh. 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string0)
└> touch flag.txt ; echo flag{fake_flag} >> flag.txt
┌[rotalactf]-[LAPTOP-6QMID52F]-(format-string0)
└> ./format-string-0
Welcome to our newly-opened burger place Pico 'n Patty! Can you help the picky customers find their favorite burger?
Here comes the first customer Patrick who wants a giant bite.
Please choose from the following burgers: Breakf@st_Burger, Gr%114d_Cheese, Bac0n_D3luxe
Enter your recommendation: Breakf@st_Burger
Breakf@st_BurgerPatrick is still hungry!
Try to serve him something of larger size!
```
oke program berhasil berjalan dengan mulus setelah aku membuat file flag.txt . disini program meminta rekomendasi burger untuk patrick. aku coba pilih acak dan sepertinya patrick
agak rakus wkwkwkwkwk. daripada memberi makan patrick lebih baik aku lanjutkan dengan membaca source codenya agar bisa mengetahui bagaimana cara program bekerja.

```C
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <sys/types.h>

#define BUFSIZE 32
#define FLAGSIZE 64

char flag[FLAGSIZE];

void sigsegv_handler(int sig) {
    printf("\n%s\n", flag);
    fflush(stdout);
    exit(1);
}

int on_menu(char *burger, char *menu[], int count) {
    for (int i = 0; i < count; i++) {
        if (strcmp(burger, menu[i]) == 0)
            return 1;
    }
    return 0;
}

void serve_patrick();

void serve_bob();


int main(int argc, char **argv){
    FILE *f = fopen("flag.txt", "r");
    if (f == NULL) {
        printf("%s %s", "Please create 'flag.txt' in this directory with your",
                        "own debugging flag.\n");
        exit(0);
    }

    fgets(flag, FLAGSIZE, f);
    signal(SIGSEGV, sigsegv_handler);

    gid_t gid = getegid();
    setresgid(gid, gid, gid);

    serve_patrick();

    return 0;
}

void serve_patrick() {
    printf("%s %s\n%s\n%s %s\n%s",
            "Welcome to our newly-opened burger place Pico 'n Patty!",
            "Can you help the picky customers find their favorite burger?",
            "Here comes the first customer Patrick who wants a giant bite.",
            "Please choose from the following burgers:",
            "Breakf@st_Burger, Gr%114d_Cheese, Bac0n_D3luxe",
            "Enter your recommendation: ");
    fflush(stdout);

    char choice1[BUFSIZE];
    scanf("%s", choice1);
    char *menu1[3] = {"Breakf@st_Burger", "Gr%114d_Cheese", "Bac0n_D3luxe"};
    if (!on_menu(choice1, menu1, 3)) {
        printf("%s", "There is no such burger yet!\n");
        fflush(stdout);
    } else {
        int count = printf(choice1);
        if (count > 2 * BUFSIZE) {
            serve_bob();
        } else {
            printf("%s\n%s\n",
                    "Patrick is still hungry!",
                    "Try to serve him something of larger size!");
            fflush(stdout);
        }
    }
}

void serve_bob() {
    printf("\n%s %s\n%s %s\n%s %s\n%s",
            "Good job! Patrick is happy!",
            "Now can you serve the second customer?",
            "Sponge Bob wants something outrageous that would break the shop",
            "(better be served quick before the shop owner kicks you out!)",
            "Please choose from the following burgers:",
            "Pe%to_Portobello, $outhwest_Burger, Cla%sic_Che%s%steak",
            "Enter your recommendation: ");
    fflush(stdout);

    char choice2[BUFSIZE];
    scanf("%s", choice2);
    char *menu2[3] = {"Pe%to_Portobello", "$outhwest_Burger", "Cla%sic_Che%s%steak"};
    if (!on_menu(choice2, menu2, 3)) {
        printf("%s", "There is no such burger yet!\n");
        fflush(stdout);
    } else {
        printf(choice2);
        fflush(stdout);
    }
}
```
okay mungkin terlihat cukup merepotkan tapi kita cukup fokus pada beberapa bagian pentingnya saja. nah tidak perlu waktu lama aku sudah menemukan ini 
```C
void sigsegv_handler(int sig) {
    printf("\n%s\n", flag);
    fflush(stdout);
    exit(1);
}
```
ini apa? jadi ini adalah fungsi bernama sigsegv_handler. fungsi ini melakukan printflag jika dipanggil. sekarang kita perlu nyari tahu dimana program akan memanggil fungsi ini
```C
    fgets(flag, FLAGSIZE, f);
    signal(SIGSEGV, sigsegv_handler);
```
nah aku menemukan ini di fungsi main,tepat dibawah fungsi fgets. flag. signal(SIGSEGV, sigsegv_handler) akan mengeksekusi sigsegv_handler jika program mencapai kondisi error
dengan kode SIGSEGV (Segmentation Fault). 

nah jadi tujuan kita sekarang adalah memaksa program agar ia error dengan kode SIGSEGV dan melakukan print flag.

# exploit
pertama kita coba kerentanan paling basic di binary exploitation, yaitu **buffer overflow**, ini adalah kerentanan yang paling wajib dicoba karena buffer overrflow dapat membuat program
crash dengan kode SIGSEGV. saat memberi rekomendasi burger ke patrick , input kita disimpan di variabel choice1. dimana **variabel ini memiliki ukuran sebesar 32 byte**.  

namun jika hanya menginput sebanyak 33 byte itu belum cukup untuk mentrigger buffer overflow. karena dibawah input kita masih ada register saved rbp dan saved rip. jika saved
rbp tertimpa input kita, itu tidak akan terjadi crash, sementara jika saved rip yang tertimpa baru terjadi crash. pada program elf 64 bit ukuran saved rbp adalah 8 byte. tapi 
karena tujuan ku hanya memancing crash tidak perlu presisi. input aja langsung 50 karakter:
<img width="908" height="158" alt="image" src="https://github.com/user-attachments/assets/1d27cffa-fbc3-4404-839c-49f7ade25a2d" />

done flag : picoCTF{..................................}

# conclusion
harusnya chall ini adalah chall yang mengenalkan kita dengan kerentanan format string , namun sepertinya cara ku mengerjakan tidak menyinggung format string sama sekali, tapi 
no problem, aku akan membahasnya di chall lain. see ya
