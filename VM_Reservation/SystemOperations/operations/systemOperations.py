import pandas as pd
import sqlite3
from sqlite3 import Error
import time
import collections
from pathlib import Path
import threading


class SystemOps:
    def __init__(self,user_id):
        self.user_id = user_id
        self.db_conn = None
        self.user_vm_map = {}
        self.available_VM_ids = []
        self.all_vm_ids = []

    def connect_vm_data_db(self):
        path = Path(__file__).parent / "../../VMAdminData/vm_data_sqlite.db"

        self.db_conn = sqlite3.connect(path)

    def update_db_record(self,task):
        sql = '''UPDATE VM_TRACK SET Reserved_IND = ?, Reserved_User = ?
                  WHERE VM_ID = ?'''
        cur = self.db_conn.cursor()
        cur.execute(sql, task)
        self.db_conn.commit()

    def synchronized(func):
        func.__lock__ = threading.Lock()

        def synced_func(*args, **kws):
            with func.__lock__:
                return func(*args, **kws)

        return synced_func

    def vm_clean_up(self):
        print("***VM Release process started***\n")
        print(f'***cleaning log files for host with IP : {self.user_vm_map["VMIP"]}, host name : {self.user_vm_map["VMHOST"]}, user : {self.user_vm_map["VMUSERNAME"]} and password: {self.user_vm_map["VMUSERNAME"]}***\n')

    @synchronized
    def checkout(self):
        #The same VM cannot be checked out by two clients at the same time.
        # more than one VM allocation not allowed. return if VM is already assigned
        self.view_allocated_vm()
        if 'VMID' in self.user_vm_map:
            if self.user_vm_map['VMID'] != None:
                print("***You have already VM assigned. Please select another option***\n")
                return

        #show all VM IDs
        vm_all_df_a = pd.read_sql_query("select * from VM_TRACK", self.db_conn, )
        self.all_vm_ids = vm_all_df_a["VM_ID"].tolist()
        if not self.all_vm_ids:
            print("***No VMs are present in system. Please retry.***\n")
            return

        # show available VMid
        self.view_available()
        if not self.available_VM_ids:
            return

        #take user input for VM ID
        retry_flag = True
        retry_count = 0
        while retry_flag and retry_count < 3:
            try:
                user_vm_id = int(input("***Enter VM ID***\n"))
                if user_vm_id in self.available_VM_ids:
                    # update DB to allocate VM for user
                    self.update_db_record(('Y', self.user_id, user_vm_id))
                    # view allocated VM
                    self.view_allocated_vm()
                    retry_flag = False
                else:
                    print("***Please enter VM ID from available list only***\n")
                    retry_count +=1
                    if retry_count == 3:
                        print("***max limit exceeded***\n")
            except Exception as e:
                print("***Please enter valid VM ID and from available list only***\n")
                retry_count += 1
                if retry_count == 3:
                    print("***max limit exceeded***\n")
        #synchronize and threading

    @synchronized
    def checkin(self):
        #A VM checked out by one client cannot be checked in by some other client.
        # show allocated VM id .. if none then return from function
        self.view_allocated_vm()
        if 'VMID' not in self.user_vm_map:
            print("***You don't have VM assigned to you. There is nothing to release. Please select another option***\n")
            return

        #get VM ID to be checked in from client
        retry_flag = True
        retry_count = 0
        while retry_flag and retry_count < 3:
            try:
                user_vm_id = int(input("***Enter VM ID allocated to you and to be released***\n"))
                if user_vm_id == self.user_vm_map["VMID"]:
                    # Clean up VM
                    self.vm_clean_up()
                    # update DB to allocate VM for user
                    self.update_db_record(('N', "", user_vm_id))
                    # view allocated VM
                    self.view_allocated_vm()
                    retry_flag = False
                else:
                    print("***Please enter VM ID allocated to you only and to be released***\n")
                    retry_count += 1
                    if retry_count == 3:
                        print("***max limit exceeded. Please retry after sometime***\n")
            except Exception as e:
                print("***Please enter valid VM ID and allocated to you only and to be released***\n")
                retry_count += 1
                if retry_count == 3:
                    print("***max limit exceeded. Please retry after sometime***\n")


    def view_all(self):
        #only admin can view all VMs
        vm_all_df = pd.read_sql_query("select * from VM_TRACK", self.db_conn, )
        if not self.all_vm_ids:
            self.all_vm_ids = vm_all_df["VM_ID"].tolist()
        if self.user_vm_map["ISADMIN"] == 'N':
            print("***Only Admin can view all VMs allocation details.***\n")
            return
        if vm_all_df.empty:
            print("***VM Data is empty. Please load VM Data in DB.***\n")
        else:
            print(vm_all_df)

    def view_available(self):
        #view all available VMs
        vm_available_df = pd.read_sql_query("select * from VM_TRACK where Reserved_IND = (?);", self.db_conn,
                                  params=('N',))
        if vm_available_df.empty:
            print("***No VMs are available currently. Please retry in Sometime.***\n")
        else:
            self.available_VM_ids = vm_available_df.loc[vm_available_df['Reserved_IND'] == 'N'][
                'VM_ID'].tolist()
            print("***Below is list of all available VM IDs***\n")
            print(self.available_VM_ids)

    def view_allocated_vm(self):
        vm_allocated_df = pd.read_sql_query("select * from VM_TRACK where Reserved_User = (?) AND Reserved_IND = (?);", self.db_conn,
                                            params=(self.user_id,'Y'))
        if vm_allocated_df.empty:
            #release VM for the current user if present in map
            p_vmid = self.user_vm_map.pop('VMID','')
            p_vmip = self.user_vm_map.pop('VMIP','')
            p_vmhost = self.user_vm_map.pop('VMHOST','')
            p_vmuser = self.user_vm_map.pop('VMUSERNAME','')
            p_vmpass = self.user_vm_map.pop('VMPASSWORD','')
            if p_vmid:
                print(f'***Released VM details for {self.user_vm_map["USERNAME"]}are id:{p_vmid}, ip:{p_vmip}, host:{p_vmhost}, user:{p_vmuser}, pass:{p_vmpass}***\n')
            else:
                print("***VMs are not yet allocated to you***\n")
        else:
            self.user_vm_map["VMID"] = vm_allocated_df["VM_ID"][0]
            self.user_vm_map["VMIP"] = vm_allocated_df["VM_IP"][0]
            self.user_vm_map["VMHOST"] = vm_allocated_df["VM_Host"][0]
            self.user_vm_map["VMUSERNAME"] = vm_allocated_df["VM_Username"][0]
            self.user_vm_map["VMPASSWORD"] = vm_allocated_df["VM_Password"][0]
            print(f'***VM details for the user {self.user_vm_map["USERNAME"]} are {self.user_vm_map}***\n')

    def login(self):
        user_df = pd.read_sql_query("select * from USER where USER_ID = (?);", self.db_conn,
                                  params=(self.user_id,))
        if user_df.empty:
            print("***Invalid user access. Please enter valid user id***")
            return False
        self.user_vm_map["USER_ID"] = user_df["User_ID"][0]
        self.user_vm_map["USERNAME"] = user_df["Username"][0]
        self.user_vm_map["ISADMIN"] = user_df["Is_Admin"][0]
        print(f'***logged in successfully. Welcome {self.user_vm_map["USERNAME"]}***')
        return True

    def logout(self):
        self.user_vm_map.clear()
        self.available_VM_ids.clear()
        self.all_vm_ids.clear()
        print("User logged out.\n")



    def close_vm_data_db(self):
        self.db_conn.close()






