#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>

// Include the prediction functions
#include "predict.cpp"

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