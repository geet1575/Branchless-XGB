# Makefile for XGBoost prediction benchmarking
# Builds both naive and branchless variants

CXX = g++
CXXFLAGS = -O3 -std=c++11 -Wall -Wextra

# Source files
SOURCES = main.cpp

# Executables
NAIVE_TARGET = predictor_naive
BRANCHLESS_TARGET = predictor_branchless

# Default target
all: $(NAIVE_TARGET) $(BRANCHLESS_TARGET)

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
	rm -f $(NAIVE_TARGET) $(BRANCHLESS_TARGET)
	rm -f ../../data/naive_outputs.csv ../../data/branchless_outputs.csv
	@echo "Cleaned build artifacts and output files"

# Help
help:
	@echo "Available targets:"
	@echo "  all        - Build both naive and branchless predictors"
	@echo "  naive      - Build only the naive predictor"
	@echo "  branchless - Build only the branchless predictor"
	@echo "  test       - Build and run both predictors, compare outputs"
	@echo "  clean      - Remove all build artifacts and output files"
	@echo "  help       - Show this help message"

.PHONY: all naive branchless test clean help