import os

def check_directories(root_directory):
    missing_directories = []

    # Recursively iterate over all directories and subdirectories
    for root, directories, files in os.walk(root_directory):
        # Check if "Interviewee_Cap.txt" exists in the current directory
        if "Interviewee_Cap.txt" not in files:
            missing_directories.append(root)

    return missing_directories

# Example usage
root_directory = "/home/boris/DataDisk/51-100-transcript/handle"

# Check directories under the root directory for the presence of "Interviewee_Cap.txt"
missing_dirs = check_directories(root_directory)

# Print the directories where the file is missing
# for directory in missing_dirs:
#     print(f"File not found in directory: {directory}")