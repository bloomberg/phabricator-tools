#include <iostream.h>

int main(const int argc, const char* argv[])
{
    cout << "Hello World!";
    int* p = 0;
    *p = 0xbad;

    const char *s = argv[0];
    char c = s[0];
    if (0 != s) {
        cout << "oops, already crashed.";
    }

    return 0;
}
