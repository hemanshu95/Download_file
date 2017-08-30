import urllib2
import os, ssl
import shutil
import timeit, sys
from multiprocessing.dummy import Pool as ThreadPool 

#some_url = "https://dl.pagal.link/upload_file/5570/6757/Latest%20Bollywood%20Hindi%20Mp3%20Songs%20-%202017/Haseena%20Parkar%20%282017%29%20Hindi%20Movie%20Mp3%20Songs/01%20Tere%20Bina%20-%20Haseena%20Parkar%20%28Arijit%20Singh%29%20190Kbps.mp3"

some_url = "https://dl.pstmn.io/download/latest/linux64"
if(len(sys.argv)>1):
	some_url = sys.argv[1]
num_parts = 8
if(len(sys.argv)>2):
	num_parts = int(sys.argv[2])

context = ssl._create_unverified_context()
request = urllib2.Request(some_url)#'https://dl.pagal.link/upload_file/5570/6757/Latest%20Bollywood%20Hindi%20Mp3%20Songs%20-%202017/Haseena%20Parkar%20%282017%29%20Hindi%20Movie%20Mp3%20Songs/01%20Tere%20Bina%20-%20Haseena%20Parkar%20%28Arijit%20Singh%29%20190Kbps.mp3')
request.get_method = lambda : 'HEAD'
response = urllib2.urlopen(request, context = context)

print response.info()
file_size = int(response.info().getheaders("Content-Length")[0])
print response.info().getheaders("Accept-Ranges"[0])
MULTI = False
last_speeds = [0 for i in range(10)]
speed_num = 0
speed_sums = 0
last_speed = 0
def report_hook(bytes_so_far, speed = 0):
	global MULTI, all_speeds, speed_sums, speed_num, last_speeds, last_speed
	os.system('clear')
	if(MULTI):
		speed = sum(all_speeds)
	speed_sums -= float(last_speeds[speed_num])/float(10)
	speed_sums += float(speed)/float(10)
	last_speeds[speed_num] = speed
	speed_num = (speed_num+1)%10
	speed = speed_sums
	units = "bytes"
	if(speed_num==0):
		last_speed = speed_sums
	speed = last_speed/8
	if(speed>1024):
		speed/=1024
		units = "Kb"
	if(speed>1024):
		speed/=1024
		units = "Mb"
	units+="/sec"
	print str(float(bytes_so_far*100)/float(file_size)) + "%  Download Speed : " + str(round(speed,2)) + " "+ units 


file_pos = [[0,file_size,i] for i in range(num_parts)]
for i in range(1,num_parts):
	file_pos[i][0] = file_pos[i-1][0] + (file_size/num_parts)
	file_pos[i-1][1] = file_pos[i][0] - 1


##Use This For Single download
'''
start2 = timeit.default_timer()
bytes_so_far = 0
def single_download(url):
	global bytes_so_far
	chunk_size = 8192
	try:
		req = urllib2.Request(url)
		filehandle = urllib2.urlopen(req, context=context)
    # Open our local file for writing
		last_time = 10000
		with open(os.path.basename(url), "wb") as local_file:
			while 1:
				start_time = timeit.default_timer()
				chunk = filehandle.read(chunk_size)
				bytes_so_far += len(chunk)
				if not chunk:
					break
				report_hook(bytes_so_far, float(chunk_size)/float(last_time))
				print "doing" 
				local_file.write(chunk)
				stop_time = timeit.default_timer()
				last_time = stop_time - start_time
    #handle errors
	except urllib2.HTTPError, e:
		print "HTTP Error:", e.code, url
	except urllib2.URLError, e:
		print "URL Error:", e.reason, url
#single_download(some_url)
stop2 = timeit.default_timer()
'''


bytes_so_far = 0
MULTI = True
all_speeds = [0 for i in range(num_parts)]

def dowload_parts(l):
	global bytes_so_far
	start_bytes = l[0]
	end_bytes = l[1]
	chunk_size = 8192
	try:
		req = urllib2.Request(some_url)
		req.add_header('Range', 'bytes=' +str(start_bytes) +'-' + str(end_bytes))
		filehandle = urllib2.urlopen(req, context=context)
	
		last_time = 10000
		with open(os.path.basename(some_url)+'x'+str(l[2]), "wb") as local_file:
			while 1:
				start_time = timeit.default_timer()
				chunk = filehandle.read(chunk_size)
				bytes_so_far += len(chunk)
				if not chunk:
					break

				all_speeds[l[2]] = float(chunk_size)/float(last_time)
				report_hook(bytes_so_far )
				print "doing" 
				local_file.write(chunk)
				stop_time = timeit.default_timer()
				last_time = stop_time - start_time 
    #handle errors
	except urllib2.HTTPError, e:
		print "HTTP Error:", e.code, some_url
	except urllib2.URLError, e:
		print "URL Error:", e.reason, some_url

start1 = timeit.default_timer()
def multi_download():	
	pool = ThreadPool(num_parts) 
	results = pool.map(dowload_parts, file_pos)
	pool.close()
	pool.join()
	file_name = os.path.basename(some_url)
	destination = open(file_name,'wb')
	for i in range(num_parts):
		with open(file_name+'x'+str(i), "rb") as local:
			destination.write(local.read())
		os.remove(file_name+'x'+str(i))
	destination.close()
multi_download()
stop1 = timeit.default_timer()
print stop1-start1
#print stop2-start2
