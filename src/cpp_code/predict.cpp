// Generated XGBoost prediction code
// Forest with 5 trees, 8 features
// Base score: 0.48952213

//NAIVE FOREST PREDICTION (INLINED):
//----------------------------------------
float predict_forest_naive(const float* features) {
    float result = 0.0f;
    float tree_result;

    // Tree 1
        if (features[0] < 0.64203167f) {
    tree_result = -0.0051195514f;
        } else {
    tree_result = 0.00986812f;
        }
    result += tree_result;

    // Tree 2
        if (features[6] < 0.9243962f) {
    tree_result = -0.0021175693f;
        } else {
    tree_result = 0.02167265f;
        }
    result += tree_result;

    // Tree 3
        if (features[0] < 0.64203167f) {
    tree_result = -0.0045622657f;
        } else {
    tree_result = 0.00882847f;
        }
    result += tree_result;

    // Tree 4
        if (features[6] < 0.9243962f) {
    tree_result = -0.0018898702f;
        } else {
    tree_result = 0.019461524f;
        }
    result += tree_result;

    // Tree 5
        if (features[0] < 0.08483771f) {
    tree_result = -0.014708278f;
        } else {
    tree_result = 0.0022925434f;
        }
    result += tree_result;

    return result + 0.48952213f;  // Add base score
}

//BRANCHLESS FOREST PREDICTION (INLINED):
//----------------------------------------
float predict_forest_branchless(const float* features) {
    float result = 0.0f;

    // Tree 1
        result += ((features[0] < 0.64203167f)) * -0.0051195514f;
        result += ((features[0] >= 0.64203167f)) * 0.00986812f;

    // Tree 2
        result += ((features[6] < 0.9243962f)) * -0.0021175693f;
        result += ((features[6] >= 0.9243962f)) * 0.02167265f;

    // Tree 3
        result += ((features[0] < 0.64203167f)) * -0.0045622657f;
        result += ((features[0] >= 0.64203167f)) * 0.00882847f;

    // Tree 4
        result += ((features[6] < 0.9243962f)) * -0.0018898702f;
        result += ((features[6] >= 0.9243962f)) * 0.019461524f;

    // Tree 5
        result += ((features[0] < 0.08483771f)) * -0.014708278f;
        result += ((features[0] >= 0.08483771f)) * 0.0022925434f;

    return result + 0.48952213f;  // Add base score
}
