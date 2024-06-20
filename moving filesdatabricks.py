source_path = 's3://somelocation/location/dt=2024-05-14'
destination_path = 's3://somelocation/location/dt=2024-05-24'


ls = [] 

for dir_path in dbutils.fs.ls(source_path): 
    file_name = dir_path.name 
    ls.append(file_name) 
    dest = f'{destination_path}{file_name}'
    dbutils.fs.cp(dir_path.path, dest, recurse = True)