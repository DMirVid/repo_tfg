#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

#define ITERATIONS 1000000000

/* Microbenchmark para medir rendimiento de un core
 * Realiza operaciones CPU-intensivas simples
 */

double benchmark_arithmetic() {
    clock_t start = clock();
    double result = 0.0;
    
    for (long i = 0; i < ITERATIONS; i++) {
        result += (double)i * 1.5;
        result -= (double)i * 0.5;
        result *= 1.00001;
    }
    
    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("Arithmetic Operations:\n");
    printf("  Iterations: %ld\n", ITERATIONS);
    printf("  Time: %.4f seconds\n", elapsed);
    printf("  Result: %.2f\n", result);
    printf("  GFLOPS: %.2f\n\n", (ITERATIONS * 3) / (elapsed * 1e9));
    
    return elapsed;
}

double benchmark_computation() {
    clock_t start = clock();
    double result = 1.0;
    
    for (long i = 1; i < ITERATIONS / 10; i++) {
        result = sqrt(result * i);
        result = result * result;
    }
    
    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("Computation (sqrt, power):\n");
    printf("  Iterations: %ld\n", ITERATIONS / 10);
    printf("  Time: %.4f seconds\n", elapsed);
    printf("  Result: %.2f\n", result);
    printf("  Operations/sec: %.2e\n\n", (ITERATIONS / 10) / elapsed);
    
    return elapsed;
}

double benchmark_memory_access() {
    int size = 1000000;
    int *array = (int *)malloc(size * sizeof(int));
    
    clock_t start = clock();
    int sum = 0;
    
    for (long i = 0; i < ITERATIONS / 100; i++) {
        sum += array[i % size];
    }
    
    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("Memory Access Pattern:\n");
    printf("  Array size: %d elements\n", size);
    printf("  Iterations: %ld\n", ITERATIONS / 100);
    printf("  Time: %.4f seconds\n", elapsed);
    printf("  Accesses/sec: %.2e\n\n", (ITERATIONS / 100) / elapsed);
    
    free(array);
    return elapsed;
}

int main() {
    printf("========================================\n");
    printf("  Single Core Microbenchmark Suite\n");
    printf("========================================\n\n");
    
    printf("System Information:\n");
    printf("  CLOCKS_PER_SEC: %ld\n\n", CLOCKS_PER_SEC);
    
    benchmark_arithmetic();
    benchmark_computation();
    benchmark_memory_access();
    
    printf("========================================\n");
    printf("  Benchmark completed\n");
    printf("========================================\n");
    
    return 0;
}
