function data = load_h5_data(PM_file)

F = hdf5info(PM_file);

for dname = F.GroupHierarchy.Datasets
    data.(dname.Name(2:end)) = hdf5read(PM_file, dname.Name);
end
