import os
import csv
import platform
import operator 

def write_to_file(target_file, text_list):
    file1 = open(target_file, 'w')
    file1.writelines(text_list)
    
# Function to read a CSV file
def read_file(command, file):
    path = os.path.join(os.getcwd(), file)

    if os.path.isfile(path):
        rows = []
        with open(path, 'r') as data:
            
            for line in csv.reader(data):
                rows.append(line)
        #write to a file
        #write_to_file(path, ''.join(rows))
        if not rows == []:
            return rows
    else:
        response = None
        return response


# Function to prompt the user to run a command if file doesn't exist
def prompt_and_run_command(file_name, command, test_mode=True):
    #Read file or prompt user
    content= read_file(command,file_name)
    print(content)
    
    
	#Run the command an read the output
   # if test_mode == True :
     #   print(content, "<<<")
   #     print(f"{file_name} does not exist.")
        #Read results from files (which are used in dev/test mode)
       # print(f"Reading dve/test file content...{file_name}")
        #print('File empty: Run command to generate file for dev/test: ' + command + ">" + file_name)
      #  return content
    
    #Prompt dev/tester to generate missing file    
    if test_mode == True and content == None:
            run_confirmation = input("Dev file " + file_name + " empty or missing.\n" + "Do you want to run the command now? (y/n): ").strip().lower()
            
			#Prompt engineer if file is empty or missing
            if run_confirmation == 'y':
                print(f"Running command: {command}")
                
				#Run command based on OS
                if "Linux" in platform.system():
                    content = os.system(command + '| sudo tee /proc/sys/vm/drop_caches >/dev/null 2>&1')  # or subprocess.call(command, shell=True)
                else:
                    content = os.system(command)  # or subprocess.call(command, shell=True)
                    print("command results", content)
                if content == 1:
                    text = "Command cannot be ran on this OS: " + platform.system() + " " + platform.release() + " version: " +platform.version()
                    text = text + ". Run command >>> " + command + ">" + file_name
                    if os.path.exists(file_name):
                        os.remove(file_name)
                        
                    #Write results to file
                    write_to_file(file_name,text)
                    
                    
                    
                    return text
            elif run_confirmation == 'n':
                return "Nope"        
		
    #Dynamically run command and return content        
    elif test_mode == False and content == None:
        print('Running command live - without file')
    
        text = "Command cannot be ran on this OS: " + platform.system() + " " + platform.release() + " version: " +platform.version()
        text = text + ". Run command >>> " + command + ">" + file_name
        return text

# Load STIG data
stig_data = {
    "V-204419": {
        "check_cmd": "awk -F: '$4 < 1 {print $1 \",\" $4}' /etc/shadow",
        "fix_cmd": "chage -m 1 [user]",
        "placeholder": "[user]",
        "returns_list": True,
        "returned_placeholder": 1,
        "dev_commands": ["awk -F: '$5 > 60 {print $1 \",\" $3}' /etc/passwd | grep [user]"],
        "expected_value": 1000,
        "comparison_op": operator.gt,
        "test_mode": False,
        "rollback": False,
        "fix": True,
        "guidance": "If any results are returned that are not associated with a system account, this is a finding. Ensure that system accounts are reserved for UIDs below 1000.",
        "Applicability": ['Does not apply','Applies'],
        "fix_command" : "echo testing"
        },
         "V-204421": {
        "check_cmd": "awk -F: '$5 > 60 {print $1 \",\" $5}' /etc/shadow",
        "fix_cmd": "chage -M 60 [user]",
        "placeholder": "[user]",
        "returns_list": True,
        "returned_placeholder": 1,
        "dev_commands": ["awk -F: '$5 > 60 {print $1 \",\" $3}' /etc/passwd | grep [user]"],
        "expected_value": 1000,
        "comparison_op": operator.gt,
        "test_mode": True,
        "rollback": False,
        "fix": True,
        "guidance": "Configure non-compliant accounts to enforce a 60-day maximum password lifetime restriction. If any results are returned that are not associated with a system account, this is a finding. Ensure that system accounts are reserved for UIDs below 1000.",
        "Applicability": ['Does not apply','Applies'],
        "fix_command" : "echo testing"
        },
         "V-204429": {
        "check_cmd": "awk -F: '$4 < 1 {print $1 \",\" $4}' /etc/shadow",
        "fix_cmd": "chage -m 1 [user]",
        "placeholder": "[user]",
        "returns_list": True,
        "returned_placeholder": 1,
        "dev_commands": ["awk -F: '$5 > 60 {print $1 \",\" $3}' /etc/passwd | grep [user]"],
        "expected_value": 1000,
        "comparison_op": operator.gt,
        "test_mode": True,
        "rollback": False,
        "fix": True,
        "guidance": "If any results are returned that are not associated with a system account, this is a finding. Ensure that system accounts are reserved for UIDs below 1000.",
        "Applicability": ['Does not apply','Applies'],
        "fix_command" : "echo testing"
        }
}

# Process each STIG
print("Processing " + str(len(stig_data.items())) + " stigs.")
for stig_id, stig_info in stig_data.items():
    
    check_cmd = stig_info['check_cmd']
    test_mode = stig_info['test_mode']
    guidance = stig_info['guidance']
    file_name = f"{stig_id}_pre-check.txt"
    
    #Set text
    if test_mode == True:
        text = "Dev/Test Mode: "
    else:
        text = "Live Mode: "

    
    
    #Process using dev/test files
    if test_mode == True:
   
        print(f"+ Processing {stig_id} in " + text + check_cmd)
		#Check stig
        command_result = prompt_and_run_command(file_name, check_cmd,test_mode)
        print("Result",command_result)
        

        
		
    elif test_mode == False:
    #Dynamically run commands
        print(f"+ Processing {stig_id} in " + text + check_cmd)
        command_result = prompt_and_run_command(file_name, check_cmd,test_mode)
       # for line in command_result:
         #   print(line)
 #
            
        
