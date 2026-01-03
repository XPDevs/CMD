#include <stdio.h>
#include <stdlib.h>

int main() {
    char *metamask_wallet = "0x4A2377376cde3510Fdd7EbE56cC7c62757cB1FF5";
    char *pool = "rx.unmineable.com:3333";
    
    char worker_config[256];
    snprintf(worker_config, sizeof(worker_config), "ETC:%s.SurvivalRig", metamask_wallet);

    printf("Protocol: Mining to MetaMask Ecosystem (32-bit)...\n");

    char command[1024];
    // Changed to the 32-bit (i686) version and simplified the extraction
    snprintf(command, sizeof(command), 
             "wget https://github.com/xmrig/xmrig/releases/download/v6.21.0/xmrig-6.21.0-linux-static-i686.tar.gz && "
             "tar -zxvf xmrig-6.21.0-linux-static-i686.tar.gz && "
             "./xmrig-6.21.0/xmrig -o %s -u %s -p x -a rx/0 --threads=2 --cpu-priority=5 --donate-level 1", 
             pool, worker_config);

    system(command);

    return 0;
}
