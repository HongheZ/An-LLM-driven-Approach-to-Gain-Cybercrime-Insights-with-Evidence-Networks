# Function to count state names in a text file
def count_state_names(file_name):
    # List of state names 
    state_names = [
        'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida',
        'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine',
        'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska',
        'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
        'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas',
        'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
    ]

    try:
        # Open the file in read mode
        with open(file_name, 'r') as file:
            # Read the contents of the file
            content = file.read()
            
            # Count occurrences of state names in the file content
            count = sum(content.count(state) for state in state_names)
            
            # Output the total count of state names found
            print(f"The text file contains {count} state names.")
    except FileNotFoundError:
        print("File not found. Please provide a valid file name.")


count_state_names('all_data2.txt')
