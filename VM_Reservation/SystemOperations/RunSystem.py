from operations.systemOperations import SystemOps
import sys

options_available = [1,2,3,4,5,6,7] #allowed operations
def operation_selection():
    user_selection = 0
    a = '''Please enter ID of the next operation which you want to perform from below list\n
                    1: View All VMs (This will list reserved and available VMs. only Admin user can use it.)
                    2: View available VMs
                    3: View allocated VM
                    4: Reserve VM (checkout VM)
                    5: Release VM (Checkin VM)
                    6: Logout (only user will be logged out)
                    7: Exit Application (exit from entire application)\n'''
    try:
        user_selection = int(input(a))  # prompt for action which user wants to perform
        while user_selection not in options_available:
            user_selection = int(input("Invalid option selected. Please enter valid option only\n"))
    except Exception as e:
        print("Invalid option selected. Please enter valid option only\n")
        while user_selection not in options_available:
            user_selection = int(input("Invalid option selected. Please enter valid option only\n"))
    return user_selection


def main():
    print("Welcome to the VM reservation system")
    while True:
        A = SystemOps(input("Enter User ID\n")) #take user id as input
        A.connect_vm_data_db()
        state = A.login() #user authentication
        if state == False:
            continue
        option = operation_selection()
        while True:
            if option==1:
                A.view_all()
            elif option==2:
                A.view_available()
            elif option==3:
                #need to read valid VM id
                A.view_allocated_vm()
            elif option==4:
                A.checkout()
            elif option==5:
                A.checkin()
            elif option==6:
                A.logout()
                break
            else:
                A.close_vm_data_db()
                sys.exit()
            option = operation_selection()






if __name__ == '__main__':
    main()