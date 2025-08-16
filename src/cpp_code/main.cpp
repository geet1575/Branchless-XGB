#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <chrono>
#include <iomanip>

#if defined(BENCHMARK_NAIVE) || defined(BENCHMARK_BRANCHLESS)
#include <benchmark/benchmark.h>
#endif

#if defined(MY_BENCHMARK_NAIVE) || defined(MY_BENCHMARK_BRANCHLESS)
#include <cstdint>
#ifdef __x86_64__
#include <x86intrin.h>
#else
#include <chrono>
#endif
#endif

// Include the prediction functions
#include "predict.cpp"

// Global data for benchmarking
std::vector<std::vector<float>> g_inputData;
bool g_dataLoaded = false;

// Function to read CSV file into a 2D vector
std::vector<std::vector<float>> readCSV(const std::string& filename) {
    std::vector<std::vector<float>> data;
    std::ifstream file(filename);
    std::string line;
    
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        return data;
    }
    
    // Skip header line
    std::getline(file, line);
    
    // Read data lines
    while (std::getline(file, line)) {
        std::vector<float> row;
        std::stringstream ss(line);
        std::string cell;
        
        while (std::getline(ss, cell, ',')) {
            row.push_back(std::stof(cell));
        }
        
        if (!row.empty()) {
            data.push_back(row);
        }
    }
    
    file.close();
    std::cout << "Loaded " << data.size() << " samples from " << filename << std::endl;
    return data;
}

// Function to write predictions to CSV file
void writeCSV(const std::vector<float>& predictions, const std::string& filename) {
    std::ofstream file(filename);
    
    if (!file.is_open()) {
        std::cerr << "Error: Could not write to file " << filename << std::endl;
        return;
    }
    
    file << "prediction" << std::endl;
    for (const float& pred : predictions) {
        file << pred << std::endl;
    }
    
    file.close();
    std::cout << "Wrote " << predictions.size() << " predictions to " << filename << std::endl;
}

#if defined(BENCHMARK_NAIVE) || defined(BENCHMARK_BRANCHLESS)
// Load data for benchmarking
void loadBenchmarkData() {
    if (!g_dataLoaded) {
        std::string inputFile = "../../data/inputs.csv";
        g_inputData = readCSV(inputFile);
        g_dataLoaded = true;
    }
}

#ifdef BENCHMARK_NAIVE
// Benchmark naive prediction
static void BM_PredictNaive(benchmark::State& state) {
    loadBenchmarkData();
    if (g_inputData.empty()) return;
    
    for (auto _ : state) {
        // Process entire dataset in each iteration
        for (size_t i = 0; i < g_inputData.size(); i++) {
            float prediction = predict_forest_naive(g_inputData[i].data());
            benchmark::DoNotOptimize(prediction);
        }
    }
}
BENCHMARK(BM_PredictNaive);
#endif

#ifdef BENCHMARK_BRANCHLESS
// Benchmark branchless prediction
static void BM_PredictBranchless(benchmark::State& state) {
    loadBenchmarkData();
    if (g_inputData.empty()) return;
    
    for (auto _ : state) {
        // Process entire dataset in each iteration
        for (size_t i = 0; i < g_inputData.size(); i++) {
            float prediction = predict_forest_branchless(g_inputData[i].data());
            benchmark::DoNotOptimize(prediction);
        }
    }
}
BENCHMARK(BM_PredictBranchless);
#endif

#elif defined(MY_BENCHMARK_NAIVE) || defined(MY_BENCHMARK_BRANCHLESS)

#ifdef __x86_64__
// RDTSC timing functions for x86_64
inline uint64_t rdtsc_start() {
    unsigned int dummy;
    return __rdtscp(&dummy);  // Serializing RDTSC
}

inline uint64_t rdtsc_end() {
    unsigned int dummy;
    return __rdtscp(&dummy);
}
#endif

// Function to write timing data to file
void writeTimingData(const std::vector<uint64_t>& times, const std::string& filename) {
    std::ofstream file(filename);
    
    if (!file.is_open()) {
        std::cerr << "Error: Could not write to file " << filename << std::endl;
        return;
    }
    
    for (const uint64_t& time : times) {
        file << time << std::endl;
    }
    
    file.close();
    std::cout << "Wrote " << times.size() << " timing measurements to " << filename << std::endl;
}

int main() {
    // Read input data from CSV
    std::string inputFile = "../../data/inputs.csv";
    std::vector<std::vector<float>> inputData = readCSV(inputFile);
    
    if (inputData.empty()) {
        std::cerr << "Error: No data loaded from " << inputFile << std::endl;
        return 1;
    }
    
    std::vector<uint64_t> times;
    times.reserve(inputData.size());
    
#ifdef MY_BENCHMARK_NAIVE
#ifdef __x86_64__
    std::cout << "Running MY_BENCHMARK_NAIVE - measuring individual prediction times (RDTSC cycles)" << std::endl;
    
    // Process each sample and measure time
    for (const auto& sample : inputData) {
        uint64_t start = rdtsc_start();
        float prediction = predict_forest_naive(sample.data());
        uint64_t end = rdtsc_end();
        
        uint64_t cycles = end - start;
        times.push_back(cycles);
        
        // Prevent optimization from removing the prediction call
        volatile float dummy = prediction;
        (void)dummy;
    }
#else
    std::cout << "Running MY_BENCHMARK_NAIVE - measuring individual prediction times (nanoseconds)" << std::endl;
    
    // Fallback to chrono for non-x86_64 platforms
    for (const auto& sample : inputData) {
        auto start = std::chrono::high_resolution_clock::now();
        float prediction = predict_forest_naive(sample.data());
        auto end = std::chrono::high_resolution_clock::now();
        
        uint64_t duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
        times.push_back(duration);
        
        // Prevent optimization from removing the prediction call
        volatile float dummy = prediction;
        (void)dummy;
    }
#endif
    
    writeTimingData(times, "naive_times.txt");
    
#elif defined(MY_BENCHMARK_BRANCHLESS)
#ifdef __x86_64__
    std::cout << "Running MY_BENCHMARK_BRANCHLESS - measuring individual prediction times (RDTSC cycles)" << std::endl;
    
    // Process each sample and measure time
    for (const auto& sample : inputData) {
        uint64_t start = rdtsc_start();
        float prediction = predict_forest_branchless(sample.data());
        uint64_t end = rdtsc_end();
        
        uint64_t cycles = end - start;
        times.push_back(cycles);
        
        // Prevent optimization from removing the prediction call
        volatile float dummy = prediction;
        (void)dummy;
    }
#else
    std::cout << "Running MY_BENCHMARK_BRANCHLESS - measuring individual prediction times (nanoseconds)" << std::endl;
    
    // Fallback to chrono for non-x86_64 platforms
    for (const auto& sample : inputData) {
        auto start = std::chrono::high_resolution_clock::now();
        float prediction = predict_forest_branchless(sample.data());
        auto end = std::chrono::high_resolution_clock::now();
        
        uint64_t duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
        times.push_back(duration);
        
        // Prevent optimization from removing the prediction call
        volatile float dummy = prediction;
        (void)dummy;
    }
#endif
    
    writeTimingData(times, "branchless_times.txt");
    
#else
    std::cerr << "Error: No my benchmark algorithm specified. Use -DMY_BENCHMARK_NAIVE or -DMY_BENCHMARK_BRANCHLESS" << std::endl;
    return 1;
#endif
    
    std::cout << "Timing measurement completed successfully!" << std::endl;
    return 0;
}

#else
// Regular main function for prediction
int main() {
    // Read input data from CSV
    std::string inputFile = "../../data/inputs.csv";
    std::vector<std::vector<float>> inputData = readCSV(inputFile);
    
    if (inputData.empty()) {
        std::cerr << "Error: No data loaded from " << inputFile << std::endl;
        return 1;
    }
    
    std::vector<float> predictions;
    predictions.reserve(inputData.size());
    
#ifdef PRED_NAIVE
    std::cout << "Using NAIVE prediction algorithm" << std::endl;
    std::string outputFile = "../../data/naive_outputs.csv";
    
    // Process each sample using naive prediction
    for (const auto& sample : inputData) {
        float prediction = predict_forest_naive(sample.data());
        predictions.push_back(prediction);
    }
    
#elif defined(PRED_BRANCHLESS)
    std::cout << "Using BRANCHLESS prediction algorithm" << std::endl;
    std::string outputFile = "../../data/branchless_outputs.csv";
    
    // Process each sample using branchless prediction
    for (const auto& sample : inputData) {
        float prediction = predict_forest_branchless(sample.data());
        predictions.push_back(prediction);
    }
    
#else
    std::cerr << "Error: No prediction algorithm specified. Use -DPRED_NAIVE or -DPRED_BRANCHLESS" << std::endl;
    return 1;
#endif
    
    // Write predictions to output file
    writeCSV(predictions, outputFile);
    
    std::cout << "Prediction completed successfully!" << std::endl;
    return 0;
}
#endif