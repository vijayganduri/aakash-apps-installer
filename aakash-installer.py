#!/usr/bin/python

import os
import csv
import sys
import time
import subprocess
from subprocess import Popen, PIPE

mac_cmd = "sudo adb shell ip link show wlan0 | busybox awk '/ether/ {print $2}'"
adb_cmd = "sudo adb get-state"
curlftpfs_mount_dir = " /mnt/aakash "
curlftpfs_cmd = "sudo curlftpfs  %s"  + curlftpfs_mount_dir 
rsync_dest_dir = " ~/Desktop/ "
rsync_cmd = "sudo rsync -ra --delete " + curlftpfs_mount_dir + rsync_dest_dir
umount_dir = "sudo umount " + curlftpfs_mount_dir 
# unset proxy didn't work, need to find some better solution
unset_proxy = "unset http_proxy https_proxy ftp_proxy"
mac_addr = ''
logFileName = ''
flag_state = 1
mac_count = 0



def headerText():
    os.system('clear')
    print '\n'
    print '----------------------------------------------------------'
    print '|      Aakash  Installation  Log     (Version 1.0)       |' 
    print '----------------------------------------------------------\n\n'


def deviceFailureText():
    print "      ------------------------------------------"
    print "      |        *** NO DEVICE FOUND ***         |"
    print "      | Connect aakash and wait for 10 seconds |"
    print "      ------------------------------------------"


def statusText():
    print "\t     ------------------------------"
    print "\t     |  Aakash device connected   |"
    print "\t     ------------------------------\n"


def footerText():
    #subprocess.call("sudo adb shell busybox poweroff -f ",
    subprocess.call("sudo adb reboot ",\
                    stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    #print "\n\n -->  Poweroff aakash!!!"
    print "\n\n -->  Restart aakash!!!"
    print "\n\n========================================================================================"
    print "| If you wish to stop this program type 'Control + c' to exit                          |"
    print "| There are more options available, check aakash installer help by typing: aakash -h   |"
    print "========================================================================================"
    print "\n\n========================================================================================================"
    print "|   Task complete. Remove the USB cable and connect another device, don't cancel this program          |" 
    print "========================================================================================================"


def help():
    os.system('cat /usr/share/aakash/help.txt')


def getStdout(command):
    # returns stdout of command as string 
    return Popen(command, shell=True, stdout=PIPE).stdout.read().strip('\n')


def rsyncWithServer():
    if not os.path.isfile(os.getenv('HOME') + '/.aakash'):
        print "\n\n It seems you are running this program for first time. We need to know"
        print "your preferred ftp site to sync. Run"
        print "\n\t $ aakash -add ftp://your-ftp-site/aakash\n"
        print "Contact your system admin if you don't have one."
        sys.exit(0)
    else:
        ftp = open(os.getenv('HOME') + '/.aakash')
        ftp_addr = ftp.read().strip('\n')
    print "-->  Trying to contact %s for any update" %(ftp_addr) +'\n'
    subprocess.call(umount_dir,stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True) 
    subprocess.call("sudo mkdir -p %s %s" %(curlftpfs_mount_dir, rsync_dest_dir),\
                    stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    # A test must be done whether ftp is running or not, if not rsync should not take place
    # as it will empty the ~/Desktop/aakash directory which is in sync with /mnt/aakash
    # if error code (0 means no error)
    if subprocess.call(curlftpfs_cmd %(ftp_addr),stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True):
        print "Error connecting to ftp server, please check your URL & connection."
        print "If you are very sure that there is nothing to sync from server and you want to "
        print "force install the apps then use 'aakash' with '-f'(force install) flag:\n"
        print "$ aakash -f"
        print "\nNot recommended."
        print "\nQuitting application !"
        sys.exit(0)
    else:
        print "-->  Server found and ready for sync."
    if subprocess.call(rsync_cmd,stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True):
        print "\n\nftp server detected, but failed to sync. Please install 'rsync' and try again !"
        print "Quitting application !"
        sys.exit(0)
    else:
        print "\n-->  Syncing in progress. Keep patience. If you are syncing for first time it may take a while."
        
    subprocess.call(umount_dir,stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    os.system('sudo sync')
    print "\n-->  Syncing with server done, all latest apps present in ~/Desktop/aakash/ \n"
    time.sleep(4)


def updateListOfServerDirs():
    allServerPaths = []
    os.chdir(os.getenv('HOME') + '/Desktop/aakash/')
    if os.path.isfile('path_of_apks_and_data'):
        reader = csv.reader(open('path_of_apks_and_data', 'r'))
        for row in reader:
            allServerPaths.append(row)
    else:
        print '\n\nError, ' + os.getenv('HOME') + '/Desktop/aakash/path_of_apks_and_data' + " not found !"
        print "This is a rare occassion, ask your system admin to set aakash in the root of the ftp server."
        print "\nQuitting application !"
        sys.exit(0)
    return allServerPaths       

def installAPKs():
    #Remove uninstall if not needed
    unInstall()
    # converting relative paths to absolute for present user
    fullPathofAPK = []
    list_of_apk_dirs = []
    # allServerPaths contain a array of paths of both apk and data dirs of ~/Desktop/aakash
    allServerPaths = updateListOfServerDirs()
    for eachPath in allServerPaths:
        list_of_apk_dirs.append(eachPath[0])
    for eachdir in list_of_apk_dirs:
        fullPathofAPK.append(os.getenv('HOME') + '/Desktop/' + eachdir)
    for eachFullPath in fullPathofAPK:
        if os.path.isdir(eachFullPath):
            os.chdir(eachFullPath)
            print "\n\nInstalling apks from :  %s" %(eachFullPath)
            print "----------------------\n"
            for apks in os.listdir("."):
                if apks.endswith(".apk"):
                    if subprocess.call("sudo adb install -r %s" %(apks),\
                                        stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True):
                        print "-->  Can't install %s, please check if\
                               device is connected properly\n" %(apks)
                        print "Quitting !"       
                        sys.exit(0)       
                    else:
                        print "-->  Installed successfully %s\n" %(apks)
    # Execute wallpaper automatically                        
    subprocess.call("adb shell am start -a android.intent.action.MAIN -n com.blundell.tutorial/.ui.phone.MainActivity",\
                    stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)


def checkAndroidDirExistenceIfNotCreate(path):
    # As 'path' is full path so need to separate source & destination from csv row
    if '/' in path[0]:
        subprocess.call("adb shell busybox mkdir -p %s" %(path[1]),\
                        stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)


def pushData():
    # Will read 'path' file and push data to android
    fullPathofData = []
    list_of_data_dirs = []
    # allServerPaths contain a array of paths of both apk and data dirs of ~/Desktop/aakash
    allServerPaths = updateListOfServerDirs()
    for eachPath in allServerPaths:
        list_of_data_dirs.append(eachPath[1])
    for eachdir in list_of_data_dirs:
        fullPathofData.append(os.getenv('HOME') + '/Desktop/' + eachdir)
    for eachDataPath in fullPathofData:
        if os.path.isdir(eachDataPath):
            os.chdir(eachDataPath)
            print "\n\nPushing data from :  %s" %(eachDataPath)
            print "------------------\n"
            if os.path.isfile('path'):
                reader = csv.reader(open('path', 'r'))
                for row in reader:
                    # Must create dir if not present (make it default way)
                    checkAndroidDirExistenceIfNotCreate(row)
                    # on success os.system returns 0, so checking it state
                    if subprocess.call("sudo adb push %s" %('\t'.join(row)),stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True):
                        print "-->  Can't push file to destination,"
                        print "     please check if you have sufficient space in destination !\n"
                        print "     Quitting application !"
                    #    sys.exit(0)
                    else:
                        print "-->  Pushed %s to %s successfully \n" %(row[0], row[1])


def macIdLog(mac_addr):
    global logFileName, flag_state, mac_count
    # this will run only first time   
    if flag_state:
        logFileName = time.strftime("%a_%d_%b_%Y_%H_%M_%S") + '.csv'
        flag_state = 0
    with open(os.getenv('HOME') + '/Desktop/' + logFileName, 'a') as csvfile:
        macLog = csv.writer(csvfile)
        if mac_addr in open(os.getenv('HOME') + '/Desktop/' + logFileName).read():
            print "\n-->  ERROR ERROR ERROR !!!"
            print "     MAC Address already present, don't repeat devices,"
            print "     this instance is not updated in csv file\n"
            #sys.exit(0)
        else:    
            macLog.writerow([mac_addr])
            print "-->  MAC address updated successfully in %s !\n" \
            %(os.getenv('HOME') + '/Desktop/' + logFileName)
            #making a copy for worst case scenario
            mac_count = mac_count + 1
            print "-->  Total MAC addresses updated in csv file so far : %s\n" %(mac_count)
            os.system("sudo cp %s /usr/share/aakash" %(os.getenv('HOME') +\
            '/Desktop/' + logFileName)) 

def checkDeviceMacAddress():
    # Read the mac address with the mac_cmd functions
    print "-->  Turning on Wifi, please wait... \n"	
    subprocess.call("adb shell svc wifi enable", 
		    stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    time.sleep(5)	
    mac_addr = getStdout(mac_cmd)
    if int(len(mac_addr)) is 17:
        print '-->  MAC address of the device :  ' + mac_addr + '\n'
	macIdLog(mac_addr)
    else:
        headerText()
        statusText()
        print '-->  **NOTE :  Automatic Wifi detection failed, to view MAC address of the device just enable WiFi in Aakash,'
        print '          connection to WiFi is not required.\n'
    # Setting time
    os.environ['TZ'] = 'Asia/Kolkata'
    subprocess.call("adb shell date -s %s" %(time.strftime("%Y%m%d.%H%M%S")),\
                     stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    print "-->  Fixed system time, but can not fix the time zone.\n" 
    subprocess.call("adb shell svc wifi disable", \
	            stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    print "-->  Wifi tunrd off\n"	


def detectDevice():
    while True:
        time.sleep(0.5)
        # Checking the adb output for the following string, when detected the welcome
        # header text is handled in checkDeviceMacAddress function, just to save lines
        if 'device' in getStdout(adb_cmd):
            headerText()
            statusText()
            break    
        else:
            headerText()
            deviceFailureText()


def executeAll(*exceptThese):
    # All apps in default order present in listFunctions[], this
    # allows user to skip one or functions based on args
    listFunctions = ['detectDevice()', 'checkDeviceMacAddress()',
                     'rsyncWithServer()', 'installAPKs()',
                     'pushData()','footerText()']
    # Converting the tuple into list                     
    exceptThese = list(exceptThese)
    # If length is 0 means no args i.e run aakash in default mode
    if len(exceptThese) is 0:
        for eachFunction in listFunctions:
            exec(eachFunction)
    else:
    # Checking functions in exceptThese & removing them    
        for eachSkipFunction in exceptThese:
            listFunctions.remove(eachSkipFunction)                            
    # Executing new listFunctions with removed functions        
        for eachFunction in listFunctions:
            exec(eachFunction)


def waitForNewDevice():
    # Checking whether the cable is unplugged by waiting for adb response
    subprocess.call("adb wait-for-device",
                        stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    #while True:
        #time.sleep(1)
        #if 'unknown' in getStdout(adb_cmd):
        #    break
        

# hard coded for this moment, put the list of apks here
def unInstall():
    list_of_apks_to_be_uninstalled = [
    'com.iitb.blender.animation',
    'com.iitb.promitywifi',
    'com.iitb.proxymity',
    'com.org.spokentutorial',
    'in.ac.iitb.aakash.rc_dualscreen',
    'in.ac.iitb.aakash.robo',
    'com.aakash.apps',
    'com.aakash.lab',
    'com.aakash.pusthak.launch',
    'com.aakashdemo.apps',
    'com.iitb',
    'com.android.example',
    'com.blundell.tutorial',
    'air.AVCMobile'
    ]
    for each in list_of_apks_to_be_uninstalled:   
       if subprocess.call("sudo adb uninstall %s" %(each),\
                                        stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True):
           print "-->  Can't uninstall %s, please check if\
                       device is connected properly\n" %(each)
           print "Quitting !"       
       else:
           print "--> Un-installed successfully %s\n" %(each)

   


def  processArgs():
    args = sys.argv
    # All flags are resloved here, '-f' for force install, skipping the server sync
    if '-f' in args:
        executeAll('rsyncWithServer()')
        waitForNewDevice()
    # Skipping all, will show only mac address    
    elif '-m' in args:
	while True:
            executeAll('rsyncWithServer()','installAPKs()', 'pushData()')
	    waitForNewDevice()
    # Skip sending huge data again, only installs the apks    
    elif '-a' in args:
        executeAll('rsyncWithServer()','pushData()')
    # Quick help on commands    
    elif '-h' in args:
        help()
    # Show detailed offline help in web browser
    elif '-hb' in args:
        if int(len(args)) is 3:
            os.system("%s /usr/share/aakash/help.html" %(args[args.index('-hb') + 1]))
        else:
            print "Missing browser name. Example:"
            print "   $ aakash -hb firefox"
    elif '-add' in args:
        if int(len(args)) is 3 and args[-1].startswith('ftp://') and args[-1].endswith('/aakash'):
            ftp_url = open(os.getenv('HOME') + '/.aakash','w')
            ftp_url.write(args[-1])
            ftp_url.close()
            print "\nURL updated successfully.\nIf you want to modify URL again, repeat the previous procedure."
            print "\nNow run 'aakash' again." 
        else:
            print "\n\nNot a valid url, please check again."
            sys.exit(0)
    # The main execute loop, default application starts here        
    elif int(len(args)) is 1:
        while True:
            executeAll()
            waitForNewDevice()
    else:
        print "Wrong option. Please see help(-h)"
        print "   $ aakash -h"



if __name__=="__main__":
    processArgs()   
