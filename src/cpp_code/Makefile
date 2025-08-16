# Makefile for XGBoost prediction benchmarking
# Builds both naive and branchless variants

CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra
BENCHMARK_DIR = ./benchmark
BENCHMARK_LIBS = -L$(BENCHMARK_DIR)/build/src -lbenchmark_main -lbenchmark -lpthread
BENCHMARK_INCLUDES = -I$(BENCHMARK_DIR)/include

# Source files
SOURCES = main.cpp

# Executables
NAIVE_TARGET = predictor_naive
BRANCHLESS_TARGET = predictor_branchless
BENCHMARK_NAIVE_TARGET = benchmark_naive
BENCHMARK_BRANCHLESS_TARGET = benchmark_branchless

# Default target
all: $(NAIVE_TARGET) $(BRANCHLESS_TARGET) $(BENCHMARK_NAIVE_TARGET) $(BENCHMARK_BRANCHLESS_TARGET)

# Benchmark targets
benchmarks: $(BENCHMARK_NAIVE_TARGET) $(BENCHMARK_BRANCHLESS_TARGET)

# Naive implementation
naive: $(NAIVE_TARGET)

$(NAIVE_TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) -DPRED_NAIVE -o $@ $<
	@echo "Built naive predictor: $@"

# Branchless implementation  
branchless: $(BRANCHLESS_TARGET)

$(BRANCHLESS_TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) -DPRED_BRANCHLESS -o $@ $<
	@echo "Built branchless predictor: $@"

# Benchmark naive implementation
benchmark_naive: $(BENCHMARK_NAIVE_TARGET)

$(BENCHMARK_NAIVE_TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(BENCHMARK_INCLUDES) -DBENCHMARK_NAIVE $(BENCHMARK_LIBS) -o $@ $<
	@echo "Built naive benchmark: $@"

# Benchmark branchless implementation
benchmark_branchless: $(BENCHMARK_BRANCHLESS_TARGET)

$(BENCHMARK_BRANCHLESS_TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) $(BENCHMARK_INCLUDES) -DBENCHMARK_BRANCHLESS $(BENCHMARK_LIBS) -o $@ $<
	@echo "Built branchless benchmark: $@"

# Test both implementations
test: $(NAIVE_TARGET) $(BRANCHLESS_TARGET)
	@echo "Running naive predictor..."
	./$(NAIVE_TARGET)
	@echo ""
	@echo "Running branchless predictor..."
	./$(BRANCHLESS_TARGET)
	@echo ""
	@echo "Comparing outputs..."
	@if [ -f "../../data/naive_outputs.csv" ] && [ -f "../../data/branchless_outputs.csv" ]; then \
		echo "Both output files created successfully"; \
		wc -l ../../data/naive_outputs.csv ../../data/branchless_outputs.csv; \
	else \
		echo "Error: Output files missing"; \
	fi

# Clean build artifacts
clean:
	rm -f $(NAIVE_TARGET) $(BRANCHLESS_TARGET) $(BENCHMARK_NAIVE_TARGET) $(BENCHMARK_BRANCHLESS_TARGET)
	rm -f ../../data/naive_outputs.csv ../../data/branchless_outputs.csv
	@echo "Cleaned build artifacts and output files"

# Help
help:
	@echo "Available targets:"
	@echo "  all               - Build both naive and branchless predictors"
	@echo "  naive             - Build only the naive predictor"
	@echo "  branchless        - Build only the branchless predictor"
	@echo "  benchmarks        - Build both benchmark executables"
	@echo "  benchmark_naive   - Build naive benchmark executable"
	@echo "  benchmark_branchless - Build branchless benchmark executable"
	@echo "  test              - Build and run both predictors, compare outputs"
	@echo "  clean             - Remove all build artifacts and output files"
	@echo "  help              - Show this help message"
	@echo ""
	@echo "To run benchmarks with performance counters:"
	@echo "  ./benchmark_naive --benchmark_perf_counters=CYCLES,INSTRUCTIONS,BRANCH-MISSES"
	@echo "  ./benchmark_branchless --benchmark_perf_counters=CYCLES,INSTRUCTIONS,BRANCH-MISSES"

.PHONY: all naive branchless benchmarks benchmark_naive benchmark_branchless test clean help