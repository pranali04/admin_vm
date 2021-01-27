# Title
Virtual Machine Reservation System

* Main project is in 'VM_Reservation' Directory

###Assumptions
* Admin has list of VM data, VM ID is mandatory  and no VM is allocated to any of the user
yet
* Admin also has list of users in an organization 
* User Data and VM data can be collected from Admin in the format as per excel sheet under path
/VM_Reservation/VMAdminData/VM_Users_List.xlsx


### Prerequisites
* Python, IDE/Terminal to run .py files
* install requirements file to install dependencies :  
pip install -r requirements.txt

## How System works
* For the first time use , admin to prepare data sheet in the format as per excel sheet at path:/VM_Reservation/VMAdminData/VM_Users_List.xlsx
* Load data from excel to sqlite DB by running VM_Reservation/VMAdminData/load_db_data.py file. This will load data in  db file VM_Reservation/VMAdminData/vm_data_sqlite.db
* After above steps, if in future if admin wants to add/delete more records then he can directly do that in load_db_data.py file itself.
* All operations supported by the system are listed in VM_Reservation/SystemOperations/Operations/systemOperations.py module
* To run system run python script file --> VM_Reservation/SystemOperations/RunSystem.py 
\
 python RunSystem.py
* system will run in terminal with interactive way. User will need to provide necessary inputs based on that operations will be performed.
* Only admin can view all VMs including reserved and available VMs
* Other users can view only available VMs and allocated VM to them
* It supports multiple threads as well 

