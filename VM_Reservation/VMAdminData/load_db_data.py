#Assumption - before loading data in DB, VMs are not yet allocated to anyone
import pandas as pd
import sqlite3
from sqlite3 import Error
import time


def create_connection():
    retry_flag = True
    retry_count = 0
    conn = None
    while retry_flag and retry_count < 2:
        try:
            conn = sqlite3.connect("vm_data_sqlite.db")
            retry_flag = False
            return conn
        except Error as e:
            if 'CONNECTION' in str(e).upper() and retry_count == 0:
                time.sleep(5)
                retry_count +=1
            else:
                raise e
    return conn


def load_excel_to_db(conn, file_path):
    retry_flag = True
    retry_count = 0
    while retry_flag and retry_count < 2:
        try:
            dfs = pd.read_excel(file_path, sheet_name=None)
            for table, df in dfs.items():
                df.to_sql(table, conn, if_exists='replace')
            retry_flag = False
        except Exception as e:
            if 'FILE' not in str(e).upper() and retry_count == 0:
                retry_count += 1
                conn.close()
                time.sleep(5)
                conn = create_connection()
            else:
                raise Exception(e)


def main():
    conn = create_connection()
    if conn is not None:
        load_excel_to_db(conn, 'VM_Users_List.xlsx')
        print('data loaded to DB')
        conn.close()
    else:
        raise Exception('Unable to establish DB connection')
    conn.close()


if __name__ == '__main__':
    main()
















