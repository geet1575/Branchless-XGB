#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <cstdlib>

extern "C" {
    #include "../c_output_demo/xgb_predictor_src/xgb_predictor/header.h"
}

struct CSVData {
    std::vector<std::vector<float>> features;
    int num_rows;
    int num_features;
};

// Function to load all CSV data into memory
CSVData load_csv_data(const std::string& filename) {
    CSVData data;
    std::ifstream file(filename);
    std::string line;
    
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        data.num_rows = 0;
        return data;
    }
    
    // Skip header line
    std::getline(file, line);
    
    // Read all data lines
    while (std::getline(file, line)) {
        std::vector<float> row_features;
        std::stringstream ss(line);
        std::string value;
        
        while (std::getline(ss, value, ',')) {
            row_features.push_back(std::stof(value));
        }
        
        data.features.push_back(row_features);
    }
    
    data.num_rows = data.features.size();
    data.num_features = data.num_rows > 0 ? data.features[0].size() : 0;
    
    file.close();
    return data;
}

int main() {
    const std::string input_file = "inputs/inputs.csv";
    const std::string output_file = "outputs/tl2cgen.csv";
    
    std::cout << "Loading CSV data from " << input_file << "..." << std::endl;
    
    // Load all data into memory
    CSVData csv_data = load_csv_data(input_file);
    
    if (csv_data.num_rows == 0) {
        std::cerr << "Error: No data loaded from CSV file" << std::endl;
        return 1;
    }
    
    std::cout << "Loaded " << csv_data.num_rows << " rows with " 
              << csv_data.num_features << " features each" << std::endl;
    
    // Check expected number of features from TL2cgen
    int expected_features = get_num_feature();
    std::cout << "TL2cgen model expects " << expected_features << " features" << std::endl;
    
    if (csv_data.num_features != expected_features) {
        std::cerr << "Error: Feature count mismatch! CSV has " << csv_data.num_features 
                  << " features, but model expects " << expected_features << std::endl;
        return 1;
    }
    
    // Create outputs directory
    system("mkdir -p outputs");
    
    // Open output file
    std::ofstream output(output_file);
    if (!output.is_open()) {
        std::cerr << "Error: Could not create output file " << output_file << std::endl;
        return 1;
    }
    
    // Write CSV header
    output << "prediction" << std::endl;
    
    // Allocate memory for TL2cgen data structures
    union Entry* data = new union Entry[csv_data.num_features];
    float result = 0.0f;
    
    std::cout << "Processing predictions..." << std::endl;
    
    // Process each row
    for (int row = 0; row < csv_data.num_rows; row++) {
        // Convert row features to Entry format
        for (int feat = 0; feat < csv_data.num_features; feat++) {
            data[feat].missing = 0; // Set missing first (union shares memory with fvalue)
            data[feat].fvalue = csv_data.features[row][feat]; // Then set fvalue
        }
        
        // Initialize result
        result = 0.0f;
        
        // Call TL2cgen prediction function
        predict(data, 0, &result); // pred_margin = 0 for normal prediction
        
        // Optional debug output for first few predictions
        if (row < 3) {
            std::cout << "Row " << row << " -> prediction=" << result << std::endl;
        }
        
        // Write prediction to output file
        output << result << std::endl;
        
        // Progress indicator
        if ((row + 1) % 50 == 0) {
            std::cout << "Processed " << (row + 1) << " rows..." << std::endl;
        }
    }
    
    std::cout << "Completed processing " << csv_data.num_rows << " rows" << std::endl;
    std::cout << "Predictions saved to " << output_file << std::endl;
    
    // Cleanup
    delete[] data;
    output.close();
    
    return 0;
}