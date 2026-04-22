#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

#define DURATION 10.0  /* Duración del benchmark en segundos */

/* Microbenchmark para medir rendimiento de un core
 * Se ejecuta durante 10 segundos
 */

double benchmark_arithmetic() {
    clock_t start = clock();
    double result = 0.0;
    long iterations = 0;
    double elapsed = 0.0;
    
    while (elapsed < DURATION / 2) {
        result += (double)iterations * 1.5;
        result -= (double)iterations * 0.5;
        result *= 1.00001;
        iterations++;
        
        /* Verificar tiempo cada 100000 iteraciones para evitar overhead */
        if (iterations % 100000 == 0) {
            clock_t current = clock();
            elapsed = (double)(current - start) / CLOCKS_PER_SEC;
        }
    }
    
    clock_t end = clock();
    elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("Arithmetic Operations:\n");
    printf("  Duration: %.2f seconds\n", elapsed);
    printf("  Iterations: %ld\n", iterations);
    printf("  Result: %.2f\n", result);
    printf("  GFLOPS: %.2f\n\n", ((double)iterations * 3.0) / (elapsed * 1e9));
    
    return elapsed;
}

double benchmark_computation() {
    clock_t start = clock();
    double result = 1.0;
    long iterations = 0;
    double elapsed = 0.0;
    
    while (elapsed < DURATION / 2) {
        result = sqrt(result * (double)(iterations + 1));
        result = result * result;
        iterations++;
        
        /* Verificar tiempo cada 10000 iteraciones */
        if (iterations % 10000 == 0) {
            clock_t current = clock();
            elapsed = (double)(current - start) / CLOCKS_PER_SEC;
        }
    }
    
    clock_t end = clock();
    elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    
    printf("Computation (sqrt, power):\n");
    printf("  Duration: %.2f seconds\n", elapsed);
    printf("  Iterations: %ld\n", iterations);
    printf("  Result: %.2f\n", result);
    printf("  Operations/sec: %.2e\n\n", (double)iterations / elapsed);
    
    return elapsed;
}


int main() {
    printf("========================================\n");
    printf("  Single Core Microbenchmark Suite\n");
    printf("  Duration: %.0f seconds per test\n", DURATION);
    printf("========================================\n\n");
    
    printf("System Information:\n");
    printf("  CLOCKS_PER_SEC: %ld\n\n", CLOCKS_PER_SEC);
    
    benchmark_arithmetic();
    benchmark_computation();
    
    printf("========================================\n");
    printf("  Benchmark completed\n");
    printf("========================================\n");
    
    return 0;
}
