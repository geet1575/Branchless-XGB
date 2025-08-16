// Generated XGBoost prediction code
// Forest with 5 trees, 3 features
// Base score: 0.47877115

//NAIVE FOREST PREDICTION (INLINED):
//----------------------------------------
float predict_forest_naive(const float* features) {
    float result = 0.0f;
    float tree_result;

    // Tree 1
        if (features[2] < 0.89482737f) {
            if (features[1] < 0.96322256f) {
    tree_result = 0.0009047985f;
            } else {
    tree_result = 0.025288893f;
            }
        } else {
            if (features[0] < 0.77641296f) {
    tree_result = -0.021295076f;
            } else {
    tree_result = 0.027545137f;
            }
        }
    result += tree_result;

    // Tree 2
        if (features[2] < 0.72960615f) {
            if (features[1] < 0.9093204f) {
    tree_result = 0.0010435067f;
            } else {
    tree_result = 0.019555425f;
            }
        } else {
            if (features[0] < 0.69597423f) {
    tree_result = -0.016370552f;
            } else {
    tree_result = 0.007709425f;
            }
        }
    result += tree_result;

    // Tree 3
        if (features[2] < 0.06505159f) {
            if (features[2] < 0.010837652f) {
    tree_result = -0.013463572f;
            } else {
    tree_result = 0.017882913f;
            }
        } else {
            if (features[1] < 0.94476575f) {
    tree_result = -0.0032914106f;
            } else {
    tree_result = 0.015224355f;
            }
        }
    result += tree_result;

    // Tree 4
        if (features[2] < 0.72960615f) {
            if (features[1] < 0.9093204f) {
    tree_result = 0.0010176417f;
            } else {
    tree_result = 0.017028809f;
            }
        } else {
            if (features[0] < 0.69597423f) {
    tree_result = -0.014657666f;
            } else {
    tree_result = 0.0068807066f;
            }
        }
    result += tree_result;

    // Tree 5
        if (features[2] < 0.06505159f) {
            if (features[0] < 0.30461377f) {
    tree_result = 0.0029439072f;
            } else {
    tree_result = 0.021452973f;
            }
        } else {
            if (features[1] < 0.94476575f) {
    tree_result = -0.0028777833f;
            } else {
    tree_result = 0.013173106f;
            }
        }
    result += tree_result;

    return result + 0.47877115f;  // Add base score
}

//BRANCHLESS FOREST PREDICTION (INLINED):
//----------------------------------------
float predict_forest_branchless(const float* features) {
    float result = 0.0f;

    // Tree 1
        result += ((features[2] < 0.89482737f) && (features[1] < 0.96322256f)) * 0.0009047985f;
        result += ((features[2] < 0.89482737f) && (features[1] >= 0.96322256f)) * 0.025288893f;
        result += ((features[2] >= 0.89482737f) && (features[0] < 0.77641296f)) * -0.021295076f;
        result += ((features[2] >= 0.89482737f) && (features[0] >= 0.77641296f)) * 0.027545137f;

    // Tree 2
        result += ((features[2] < 0.72960615f) && (features[1] < 0.9093204f)) * 0.0010435067f;
        result += ((features[2] < 0.72960615f) && (features[1] >= 0.9093204f)) * 0.019555425f;
        result += ((features[2] >= 0.72960615f) && (features[0] < 0.69597423f)) * -0.016370552f;
        result += ((features[2] >= 0.72960615f) && (features[0] >= 0.69597423f)) * 0.007709425f;

    // Tree 3
        result += ((features[2] < 0.06505159f) && (features[2] < 0.010837652f)) * -0.013463572f;
        result += ((features[2] < 0.06505159f) && (features[2] >= 0.010837652f)) * 0.017882913f;
        result += ((features[2] >= 0.06505159f) && (features[1] < 0.94476575f)) * -0.0032914106f;
        result += ((features[2] >= 0.06505159f) && (features[1] >= 0.94476575f)) * 0.015224355f;

    // Tree 4
        result += ((features[2] < 0.72960615f) && (features[1] < 0.9093204f)) * 0.0010176417f;
        result += ((features[2] < 0.72960615f) && (features[1] >= 0.9093204f)) * 0.017028809f;
        result += ((features[2] >= 0.72960615f) && (features[0] < 0.69597423f)) * -0.014657666f;
        result += ((features[2] >= 0.72960615f) && (features[0] >= 0.69597423f)) * 0.0068807066f;

    // Tree 5
        result += ((features[2] < 0.06505159f) && (features[0] < 0.30461377f)) * 0.0029439072f;
        result += ((features[2] < 0.06505159f) && (features[0] >= 0.30461377f)) * 0.021452973f;
        result += ((features[2] >= 0.06505159f) && (features[1] < 0.94476575f)) * -0.0028777833f;
        result += ((features[2] >= 0.06505159f) && (features[1] >= 0.94476575f)) * 0.013173106f;

    return result + 0.47877115f;  // Add base score
}
