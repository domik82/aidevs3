import os


def merge_files(input_directory, output_file, file_type=".txt"):
    # Get list of all specified file types in the directory
    designated_files = [f for f in os.listdir(input_directory) if f.endswith(file_type)]

    # Open output file in write mode
    with open(output_file, "w", encoding="utf-8") as outfile:
        # Iterate through each specified file
        for file in designated_files:
            file_path = os.path.join(input_directory, file)
            # Write the filename separator
            outfile.write(f"--{file}\n")
            # Open and read each input file
            with open(file_path, "r", encoding="utf-8") as infile:
                # Write content to output file with a newline between files
                outfile.write(infile.read() + "\n")
