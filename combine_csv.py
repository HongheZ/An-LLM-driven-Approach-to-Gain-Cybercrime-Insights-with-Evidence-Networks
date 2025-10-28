import pandas as pd
import glob


def combine_preprocessed_data(database_wait_analyze_path,xml_wait_analyze_path,output_path):
    # Load the CSV files into dataframes
    database_csv = database_wait_analyze_path  # Replace with the path to your first CSV file
    xml_csv = xml_wait_analyze_path  # Replace with the path to your second CSV file

    # Read the CSV files
    df_database = pd.read_csv(database_csv)
    df_xml = pd.read_csv(xml_csv)

    # Merge the dataframes based on common columns
    concatenated_df = pd.concat([df_database, df_xml], axis=0, ignore_index=True)

    # Save the merged dataframe to a new CSV file
    concatenated_df.to_csv(output_path, index=False)




def combine_llm_result(input_csv_directory_path,output_combine_csv_path):
    # Define the directory where your CSV files are stored
    directory_path = input_csv_directory_path

    # Get a list of all CSV files in the directory
    csv_files = glob.glob(f"{directory_path}/*.csv")

    # Initialize an empty list to store individual DataFrames
    df_list = []

    # Loop through each CSV file
    for file in csv_files:
        # Read the CSV file
        df = pd.read_csv(file)
        
        # # Identify the request_evidence_type column (the last column)
        # request_evidence_type = df.columns[-1]
        
        # # Rename the request_evidence_type column to its specific name
        # df = df.rename(columns={request_evidence_type: request_evidence_type})
        
        # Append the DataFrame to the list
        df_list.append(df)

    # Merge all DataFrames in the list on common columns
    combined_df = df_list[0]
    for df in df_list[1:]:
        combined_df = pd.merge(combined_df, df, on=['line_text_number','line_text_content','row_number','table_name', 'storage_path'], how='outer')

    # Save the combined DataFrame to a new CSV file
    combined_df.to_csv(output_combine_csv_path, index=False)
    


