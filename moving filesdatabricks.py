def move_files_dbx(source_path, destination_path): 

    ls = [] 

    for dir_path in dbutils.fs.ls(source_path): 
        file_name = dir_path.name 
        ls.append(file_name) 
        dest = f'{destination_path}{file_name}'
        dbutils.fs.cp(dir_path.path, dest, recurse = True)


date_list = ['2024-06-10', '2024-06-12', '2024-06-14']


for date in date_list: 
    source_path = 's3://somelocation/location/dt={date}'
    destination_path = 's3://somelocation/location/dt=2024-06-24'
