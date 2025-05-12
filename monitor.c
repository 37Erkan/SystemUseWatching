// monitor.c
#include <stdio.h>
#include <unistd.h>
#include <string.h>

double get_cpu_usage() {
    FILE* file;
    unsigned long long int user, nice, system, idle, iowait, irq, softirq;
    unsigned long long int total1, total2, idle1, idle2;

    file = fopen("/proc/stat", "r");
    fscanf(file, "cpu %llu %llu %llu %llu %llu %llu %llu",
           &user, &nice, &system, &idle, &iowait, &irq, &softirq);
    fclose(file);
    idle1 = idle + iowait;
    total1 = user + nice + system + idle1 + irq + softirq;

    sleep(1);

    file = fopen("/proc/stat", "r");
    fscanf(file, "cpu %llu %llu %llu %llu %llu %llu %llu",
           &user, &nice, &system, &idle, &iowait, &irq, &softirq);
    fclose(file);
    idle2 = idle + iowait;
    total2 = user + nice + system + idle2 + irq + softirq;

    return 100.0 * (total2 - total1 - (idle2 - idle1)) / (total2 - total1);
}

double get_ram_usage() {
    FILE* file = fopen("/proc/meminfo", "r");
    unsigned long mem_total = 1, mem_free = 1;
    char label[64];
    while (fscanf(file, "%s %lu kB\n", label, &mem_total) == 2) {
        if (strcmp(label, "MemTotal:") == 0) break;
    }
    while (fscanf(file, "%s %lu kB\n", label, &mem_free) == 2) {
        if (strcmp(label, "MemAvailable:") == 0) break;
    }
    fclose(file);

    double used = mem_total - mem_free;
    return (used / mem_total) * 100.0;
}

int main() {
    double cpu = get_cpu_usage();
    double ram = get_ram_usage();
    printf("%.2f %.2f\n", cpu, ram); // stdout çıktısı (sadece rakamlar)
    return 0;
}

