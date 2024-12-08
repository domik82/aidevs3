import json
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.optimizers import Adam


# read source data
def read_features(file):
    with open(file, "r") as f:
        content = f.read().rstrip()

    lines = content.split("\n")

    features = []
    for line in lines:
        features.append(line.split(","))

    return features


correct_features = read_features("lab_data/correct.txt")
incorrect_features = read_features("lab_data/incorrect.txt")
correct_sets_count = len(correct_features)
incorrect_sets_count = len(incorrect_features)
correct_targets = [1] * correct_sets_count
incorrect_targets = [0] * incorrect_sets_count

training_features = np.array(
    correct_features[0 : correct_sets_count - 25]
    + incorrect_features[0 : incorrect_sets_count - 25],
    dtype=np.int64,
)
training_targets = np.array(
    correct_targets[0 : correct_sets_count - 25]
    + incorrect_targets[0 : incorrect_sets_count - 25],
    dtype=np.int64,
)
validation_features = np.array(
    correct_features[correct_sets_count - 25 : correct_sets_count]
    + incorrect_features[incorrect_sets_count - 25 : incorrect_sets_count],
    dtype=np.int64,
)
validation_targets = np.array(
    correct_targets[correct_sets_count - 25 : correct_sets_count]
    + incorrect_targets[incorrect_sets_count - 25 : incorrect_sets_count],
    dtype=np.int64,
)

test_features = read_features("lab_data/verify_no_index.txt")
print(json.dumps(test_features, indent=4))
test_features = np.array(test_features, dtype=np.int64)

activation_function = "relu"
regularizer = "l2"
model = Sequential(
    [
        Dense(units=16, activation=activation_function, kernel_regularizer=regularizer),
        Dense(units=4, activation=activation_function, kernel_regularizer=regularizer),
        Dense(units=1, activation="sigmoid"),
    ]
)
model.compile(optimizer=Adam(learning_rate=0.01), loss=BinaryCrossentropy())
model.fit(
    training_features,
    training_targets,
    epochs=500,
    verbose=1,
    shuffle=True,
    validation_data=(validation_features, validation_targets),
)

test_targets = model.predict(test_features)
print(json.dumps(test_targets.tolist(), indent=4))

# Prediction Interpretation
# High Probabilities (close to 1)
# Values like 0.997, 0.997, and 0.992 indicate that the model is very confident these entries match the patterns found in your "correct" training data.
# Low Probabilities (close to 0)
# Values like 1.06e-12, 7.47e-29, and 0.0 indicate that the model is very confident these entries match the patterns found in your "incorrect" training data.
# Classification Results
# Using the standard threshold of 0.5, your test data is classified as follows:
# 3 entries are classified as "correct" (probabilities > 0.5)
# 7 entries are classified as "incorrect" (probabilities < 0.5)
# Technical Details
# The model uses a sigmoid activation function in its final layer, which outputs values between 0 and 1. This is typical for binary classification problems where:
# Values closer to 1 indicate strong confidence in the "correct" class
# Values closer to 0 indicate strong confidence in the "incorrect" class
# The model appears to be quite confident in its predictions, as most values are either very close to 1 or very close to 0, suggesting clear decision boundaries in your feature space.
