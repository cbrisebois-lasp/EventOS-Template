#include "os/os.h"

int main(void)
{
    os_Init();

    while (1) {
        os_Exec();
    }
}
