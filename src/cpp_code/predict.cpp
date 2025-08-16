// Generated XGBoost prediction code
// Forest with 10 trees, 10 features
// Base score: 0.50532687

//NAIVE FOREST PREDICTION (INLINED):
//----------------------------------------
float predict_forest_naive(const float* features) {
    float result = 0.0f;
    float tree_result;

    // Tree 1
        if (features[4] < 0.6094937f) {
            if (features[8] < 0.23344819f) {
    tree_result = -0.008813708f;
            } else {
    tree_result = 0.008400265f;
            }
        } else {
            if (features[9] < 0.41117814f) {
    tree_result = -0.016983598f;
            } else {
    tree_result = -0.0028125115f;
            }
        }
    result += tree_result;

    // Tree 2
        if (features[4] < 0.6094937f) {
            if (features[8] < 0.23344819f) {
    tree_result = -0.007966236f;
            } else {
    tree_result = 0.0075683943f;
            }
        } else {
            if (features[6] < 0.90927035f) {
    tree_result = -0.005687143f;
            } else {
    tree_result = -0.03033845f;
            }
        }
    result += tree_result;

    // Tree 3
        if (features[4] < 0.6094937f) {
            if (features[2] < 0.84639347f) {
    tree_result = 0.0068780184f;
            } else {
    tree_result = -0.008006944f;
            }
        } else {
            if (features[4] < 0.7077552f) {
    tree_result = -0.017414099f;
            } else {
    tree_result = -0.0028686228f;
            }
        }
    result += tree_result;

    // Tree 4
        if (features[8] < 0.21119617f) {
            if (features[1] < 0.333892f) {
    tree_result = 0.0063373903f;
            } else {
    tree_result = -0.017879514f;
            }
        } else {
            if (features[5] < 0.09792376f) {
    tree_result = -0.01677846f;
            } else {
    tree_result = 0.004607348f;
            }
        }
    result += tree_result;

    // Tree 5
        if (features[2] < 0.28209704f) {
            if (features[1] < 0.10966777f) {
    tree_result = -0.02306216f;
            } else {
    tree_result = 0.012649201f;
            }
        } else {
            if (features[9] < 0.61031866f) {
    tree_result = -0.008440881f;
            } else {
    tree_result = 0.004932979f;
            }
        }
    result += tree_result;

    // Tree 6
        if (features[8] < 0.34891397f) {
            if (features[8] < 0.00978332f) {
    tree_result = 0.01718685f;
            } else {
    tree_result = -0.008737755f;
            }
        } else {
            if (features[5] < 0.09792376f) {
    tree_result = -0.013194159f;
            } else {
    tree_result = 0.0052630957f;
            }
        }
    result += tree_result;

    // Tree 7
        if (features[4] < 0.6094937f) {
            if (features[3] < 0.77261335f) {
    tree_result = 0.0061485586f;
            } else {
    tree_result = -0.0067271753f;
            }
        } else {
            if (features[3] < 0.20456028f) {
    tree_result = -0.01644339f;
            } else {
    tree_result = -0.0025242993f;
            }
        }
    result += tree_result;

    // Tree 8
        if (features[2] < 0.28209704f) {
            if (features[1] < 0.10966777f) {
    tree_result = -0.02050435f;
            } else {
    tree_result = 0.011243848f;
            }
        } else {
            if (features[9] < 0.61031866f) {
    tree_result = -0.0076393313f;
            } else {
    tree_result = 0.0045639556f;
            }
        }
    result += tree_result;

    // Tree 9
        if (features[4] < 0.6094937f) {
            if (features[7] < 0.90127385f) {
    tree_result = 0.0015955999f;
            } else {
    tree_result = 0.019275187f;
            }
        } else {
            if (features[6] < 0.90927035f) {
    tree_result = -0.00368464f;
            } else {
    tree_result = -0.025959304f;
            }
        }
    result += tree_result;

    // Tree 10
        if (features[8] < 0.21119617f) {
            if (features[1] < 0.333892f) {
    tree_result = 0.00623232f;
            } else {
    tree_result = -0.014989987f;
            }
        } else {
            if (features[5] < 0.09792376f) {
    tree_result = -0.0133864125f;
            } else {
    tree_result = 0.0036718913f;
            }
        }
    result += tree_result;

    return result + 0.50532687f;  // Add base score
}

//BRANCHLESS FOREST PREDICTION (INLINED):
//----------------------------------------
float predict_forest_branchless(const float* features) {
    float result = 0.0f;

    // Tree 1
        result += ((features[4] < 0.6094937f) & (features[8] < 0.23344819f)) * -0.008813708f;
        result += ((features[4] < 0.6094937f) & (features[8] >= 0.23344819f)) * 0.008400265f;
        result += ((features[4] >= 0.6094937f) & (features[9] < 0.41117814f)) * -0.016983598f;
        result += ((features[4] >= 0.6094937f) & (features[9] >= 0.41117814f)) * -0.0028125115f;

    // Tree 2
        result += ((features[4] < 0.6094937f) & (features[8] < 0.23344819f)) * -0.007966236f;
        result += ((features[4] < 0.6094937f) & (features[8] >= 0.23344819f)) * 0.0075683943f;
        result += ((features[4] >= 0.6094937f) & (features[6] < 0.90927035f)) * -0.005687143f;
        result += ((features[4] >= 0.6094937f) & (features[6] >= 0.90927035f)) * -0.03033845f;

    // Tree 3
        result += ((features[4] < 0.6094937f) & (features[2] < 0.84639347f)) * 0.0068780184f;
        result += ((features[4] < 0.6094937f) & (features[2] >= 0.84639347f)) * -0.008006944f;
        result += ((features[4] >= 0.6094937f) & (features[4] < 0.7077552f)) * -0.017414099f;
        result += ((features[4] >= 0.6094937f) & (features[4] >= 0.7077552f)) * -0.0028686228f;

    // Tree 4
        result += ((features[8] < 0.21119617f) & (features[1] < 0.333892f)) * 0.0063373903f;
        result += ((features[8] < 0.21119617f) & (features[1] >= 0.333892f)) * -0.017879514f;
        result += ((features[8] >= 0.21119617f) & (features[5] < 0.09792376f)) * -0.01677846f;
        result += ((features[8] >= 0.21119617f) & (features[5] >= 0.09792376f)) * 0.004607348f;

    // Tree 5
        result += ((features[2] < 0.28209704f) & (features[1] < 0.10966777f)) * -0.02306216f;
        result += ((features[2] < 0.28209704f) & (features[1] >= 0.10966777f)) * 0.012649201f;
        result += ((features[2] >= 0.28209704f) & (features[9] < 0.61031866f)) * -0.008440881f;
        result += ((features[2] >= 0.28209704f) & (features[9] >= 0.61031866f)) * 0.004932979f;

    // Tree 6
        result += ((features[8] < 0.34891397f) & (features[8] < 0.00978332f)) * 0.01718685f;
        result += ((features[8] < 0.34891397f) & (features[8] >= 0.00978332f)) * -0.008737755f;
        result += ((features[8] >= 0.34891397f) & (features[5] < 0.09792376f)) * -0.013194159f;
        result += ((features[8] >= 0.34891397f) & (features[5] >= 0.09792376f)) * 0.0052630957f;

    // Tree 7
        result += ((features[4] < 0.6094937f) & (features[3] < 0.77261335f)) * 0.0061485586f;
        result += ((features[4] < 0.6094937f) & (features[3] >= 0.77261335f)) * -0.0067271753f;
        result += ((features[4] >= 0.6094937f) & (features[3] < 0.20456028f)) * -0.01644339f;
        result += ((features[4] >= 0.6094937f) & (features[3] >= 0.20456028f)) * -0.0025242993f;

    // Tree 8
        result += ((features[2] < 0.28209704f) & (features[1] < 0.10966777f)) * -0.02050435f;
        result += ((features[2] < 0.28209704f) & (features[1] >= 0.10966777f)) * 0.011243848f;
        result += ((features[2] >= 0.28209704f) & (features[9] < 0.61031866f)) * -0.0076393313f;
        result += ((features[2] >= 0.28209704f) & (features[9] >= 0.61031866f)) * 0.0045639556f;

    // Tree 9
        result += ((features[4] < 0.6094937f) & (features[7] < 0.90127385f)) * 0.0015955999f;
        result += ((features[4] < 0.6094937f) & (features[7] >= 0.90127385f)) * 0.019275187f;
        result += ((features[4] >= 0.6094937f) & (features[6] < 0.90927035f)) * -0.00368464f;
        result += ((features[4] >= 0.6094937f) & (features[6] >= 0.90927035f)) * -0.025959304f;

    // Tree 10
        result += ((features[8] < 0.21119617f) & (features[1] < 0.333892f)) * 0.00623232f;
        result += ((features[8] < 0.21119617f) & (features[1] >= 0.333892f)) * -0.014989987f;
        result += ((features[8] >= 0.21119617f) & (features[5] < 0.09792376f)) * -0.0133864125f;
        result += ((features[8] >= 0.21119617f) & (features[5] >= 0.09792376f)) * 0.0036718913f;

    return result + 0.50532687f;  // Add base score
}
