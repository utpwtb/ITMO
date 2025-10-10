#include <stdio.h>
#include <stdlib.h>

// Прототип функции шифрования
void encrypt(char *text, int key);
// Прототип функции дешифрования
void decrypt(char *text, int key);


int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Использование: ./caesar <строка> <ключ>\n");
        return 1;
    }

    char *text = argv[1];
    int key = atoi(argv[2]);

    printf("Исходный текст: %s\n", text);
    printf("Ключ: %d\n", key);

    // Вызываем функцию для выполнения шифрования
    encrypt(text, key);

    printf("Зашифрованный текст: %s\n", text);

    decrypt(text, key);

    printf("Расшифрованный текст: %s\n", text);

    return 0;
}

// Реализация функции шифрования
void encrypt(char *text, int key) {
    for (int i = 0; text[i] != '\0'; i++) {
        char currentChar = text[i];

        if (currentChar >= 'a' && currentChar <= 'z') {
            char shiftedChar = 'a' + (((currentChar - 'a' + key) % 26) + 26) % 26;
            text[i] = shiftedChar;
        } else if (currentChar >= 'A' && currentChar <= 'Z') {
            char shiftedChar = 'A' + (((currentChar - 'A' + key) % 26) + 26) % 26;
            text[i] = shiftedChar;
        }
    }
}

void decrypt(char *text, int key){
    encrypt(text, -key);
}
