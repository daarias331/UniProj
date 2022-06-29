

internet=["ACCESS-CM2","ACCESS-ESM1-5","BCC-CSM2-MR","CanESM5",
"CanESM5-CanOE","CMCC-ESM2","CNRM-CM6-1","CNRM-CM6-1-HR","CNRM-ESM2-1","EC-Earth3-Veg",
"EC-Earth3-Veg-LR","FIO-ESM-2-0","GFDL-ESM4","GISS-E2-1-G","GISS-E2-1-H",
"HadGEM3-GC31-LL","INM-CM4-8","INM-CM5-0","IPSL-CM6A-LR","MIROC-ES2L","MIROC6","MPI-ESM1-2-HR",
"MPI-ESM1-2-LR","MRI-ESM2-0","UKESM1-0-LL"]

print(len(internet))

gcms=["ACCESS-CM2","ACCESS-ESM1-5","BCC-CSM2-MR","CanESM5","CanESM5-CanOE","CMCC-ESM2","CNRM-CM6-1","CNRM-CM6-1-HR","CNRM-ESM2-1",\
      "EC-Earth3-Veg","EC-Earth3-Veg-LR","FIO-ESM-2-0","GFDL-ESM4","GISS-E2-1-G","GISS-E2-1-H","HadGEM3-GC31-LL",\
          "INM-CM4-8","INM-CM5-0","IPSL-CM6A-LR","MIROC-ES2L","MIROC6","MPI-ESM1-2-HR","MPI-ESM1-2-LR","MRI-ESM2-0","UKESM1-0-LL"]

print(len(gcms))

missing=[]

for i in internet:
    if i not in gcms:
        missing.append(i)

print(missing)