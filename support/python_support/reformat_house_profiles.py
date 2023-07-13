import os
import pandas as pd
from datetime import datetime
from pprint import pprint as pp

class player_object_format:

    def __init__(self):

        self.profiles_dir = "/home/deras/Desktop/Midrar_work/thesis_work/feeder_model/basecase/final_files"
        self.simulation_time = 180 # minutes
    
    def read_file(self, file):
        """
        The files are one week data. We grab the first 96 rows, that is one day. From the one day profiles, we only grab three hours.
        
        This function does the following:

            Read the files, resample them if needed, and change the time to our simulation time.
        """
        df = pd.read_csv(f"{self.profiles_dir}/{file}", names=['old_timestamp','watts'])
        df = df.head(16) # grab three hours. Well, almost four hours.
        df['old_timestamp'] = pd.to_datetime(df['old_timestamp'])
        # df.set_index('old_timestamp', inplace=True)
        # df = df.resample('15T').asfreq().fillna(method='ffill')
        # df = df.reset_index()
        df['old_timestamp'] = pd.to_datetime(df['old_timestamp'])
        df['old_timestamp'] = df['old_timestamp'].apply(lambda x: x.replace(year = 2023, month= 1, day= 1))
        self.df = df
    
    def ieeezipload_format(self):
        """
        We keep the first timestamp as the format yyyy-mm-dd hh:mm:ss. The rest of the rows are in gridapps-d format, that is the incrementing timestep
        (+1min, +15min, or whatever the user wants)
        """
        timestamp_list = self.df['old_timestamp'].values.tolist()
        new_timestamp = []

        for i in range(len(timestamp_list)):
            if i == 0:
                timestamp_list[i] = datetime.utcfromtimestamp(int(timestamp_list[0]/1e9)).strftime('%Y-%m-%d %H:%M:%S')
                new_timestamp.append(f"{timestamp_list[i]} UTC")
            else:
                timestamp_list[i] = '+15m'
                new_timestamp.append(timestamp_list[i])
        
        timestamp_col = pd.DataFrame({'timestamp':new_timestamp})
        new_df = pd.concat([self.df, timestamp_col], axis=1)
        new_df = new_df.drop(['old_timestamp'], axis=1)
        new_df = new_df.iloc[:,[1,0]]
        self.new_df = new_df
        return new_df

    # def create_headers_ieee_zipload(self):
    #     self.db = 'CREATE DATABASE proven\n'
    #     self.header1 = "# DML\n"
    #     self.header2 = "# CONTEXT-DATABASE: proven\n"
    #     self.header3 = "# CONTEXT-RETENTION-POLICY: autogen \n\n"
    
    # def strip_extra_characters (self, line):
    #     line = line.rstrip(" ")
    #     line = line.rstrip("\t")
    #     line = line.rstrip("\m")
    #     line = line.rstrip("\n")
    #     line = line.rstrip("\r")
    #     return line
    
    # def print_output_file_headers(self, var, file):
    #     print(var, file=file)

    def schedule_glm_format(self):
        '''
        Schedules format:
        minutes hours days months weekdays value

        Our siulation time is just 3 hours. 
        '''
        watts_list = self.df['watts'].values.tolist()
        time = self.df['old_timestamp'].tolist()

        for i in range(len(watts_list)-1):
            print(f'{str(time[i]).split(" ")[1].split(":")[1]}-{str(time[i+1]).split(" ")[1].split(":")[1]} {str(time[i]).split(" ")[1].split(":")[0]} 1 1 * {watts_list[i]}')
        print("\n\n=======\n\n")

    def open_output_file(self):
        self.player = open("ieeezipload_modified.player", "w")

    def write_to_output_file(self, df):
        
        self.open_output_file()

        for index, row in df.iterrows():
            print(f"{row[0]},{row[1]}")
        
                


load_profiles = player_object_format()

if "__main__" == __name__:
    """
    Main function. Call or remove methods to get desirable output. For example, uncomment schedule_glm_format() to get output in 
    glm schedule format.
    """

    for file in os.listdir(load_profiles.profiles_dir):
        if file.startswith("house"):
            
            load_profiles.read_file(file=file)
            
            df = load_profiles.ieeezipload_format()

            load_profiles.write_to_output_file(df)
            

            # load_profiles.schedule_glm_format()
