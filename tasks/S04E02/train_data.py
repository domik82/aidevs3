import os
import random
import json

base_path = os.getcwd()
images_path = os.path.join(base_path, "lab_data")
correct = os.path.join(images_path, "correct.txt")
incorrect = os.path.join(images_path, "incorrect.txt")


def read_file_lines(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines()]


def create_message_dict(data_line, label):
    return {
        "messages": [
            {"role": "system", "content": "Classify data"},
            {"role": "user", "content": data_line},
            {"role": "assistant", "content": str(label)},
        ]
    }


def write_jsonl(filename, data):
    with open(filename, "w") as f:
        for item in data:
            json_line = json.dumps(item)
            f.write(json_line + "\n")


# Read data from files
correct_data = read_file_lines(correct)
incorrect_data = read_file_lines(incorrect)

# Shuffle data
random.shuffle(correct_data)
random.shuffle(incorrect_data)

# Split data for training and verification
train_correct = correct_data[:150]
train_incorrect = incorrect_data[:150]
verify_correct = correct_data[150:180]
verify_incorrect = incorrect_data[150:180]

# Prepare training data
training_data = []
for line in train_correct:
    training_data.append(create_message_dict(line, 1))
for line in train_incorrect:
    training_data.append(create_message_dict(line, 0))

# Prepare verification data
verification_data = []
for line in verify_correct:
    verification_data.append(create_message_dict(line, 1))
for line in verify_incorrect:
    verification_data.append(create_message_dict(line, 0))

# Shuffle final datasets
random.shuffle(training_data)
random.shuffle(verification_data)

# Write to files
write_jsonl("training_data.jsonl", training_data)
write_jsonl("verification_data.jsonl", verification_data)
