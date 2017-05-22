import wget

print "Downloading drug exposures..."
for i in range(0,55):
    url = 'http://stash.osgconnect.net/+rvanguri/AEOLUS_all_reports_'+str(i)+'.npy'
    print wget.download(url)

print "Downloading outcomes..."
url = 'http://stash.osgconnect.net/+rvanguri/AEOLUS_all_reports_alloutcomes.mtx'
print wget.download(url)

print "Downloading report ids..."
url = 'http://stash.osgconnect.net/+rvanguri/all_reportids.npy'

print "Downloading age vector..."
url = 'http://stash.osgconnect.net/+rvanguri/all_ages.npy'
