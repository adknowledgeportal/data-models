
import os
import pandas as pd
import argparse


# Function to recursively find all CSV files in a directory
def find_csv_files(directory):
    csv_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files



# Function to combine CSV files into one DataFrame
def combine_csv_files(csv_files):
    combined_df = pd.DataFrame()
    for file in csv_files:
        df = pd.read_csv(file)
        combined_df = pd.concat([combined_df, df], ignore_index = True)
    sorted_df = combined_df.sort_values(by = ['Parent', 'Attribute'], key = lambda col: col.str.lower()) 
    return sorted_df



# Main function
def main(args):
    input_directory = args.input_directory
    output_file = args.output_file

    csv_files = find_csv_files(input_directory)
    if not csv_files:
        print(f"No CSV files found in the directory: {input_directory}")
        return

    combined_df = combine_csv_files(csv_files)

    combined_df.to_csv(output_file, index=False)
    print(f"Combined CSV files saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine CSV files in a directory.")
    parser.add_argument("input_directory", help="Input directory containing CSV files")
    parser.add_argument("output_file", help="Output CSV file name")

    args = parser.parse_args()
    main(args)


