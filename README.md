Title:    Scripts-1  
Author:    Diego Orellana  
Base Header Level:    2  

# Introduction #

These are one of the latest scripts I made that were actually used by a company.

## Email filter ##

This script was written in Python. The purpose of this script was to filter Information from certain emails. These emails were identified by their title, and all of them contained a table with a certain format and information. What this script does is to connect to the email server find the right emails then read the information from the table which is a list of IPs and macs. Then we connect to the API of a web page that gives us the vendor given the mac, with this information we create a third list of vendors. Once we obtain the 3 lists we proceed to filter information from this table. We can know what information to filter by checking some files that will be stored in a given path, these files are one for Macs, one for IPs, and one for vendors. Each client will have its own set of filter files, therefore, for each client, we will have 3 filter files.

![diagram]

Once we get the filtered information we proceed to send it by email to a given destination. We used a cron job to execute this script periodically.


You need to set the credential of the server and the email addresses inside the script. The paths to the filter files and the filtered information are given as parameters.

Then in the crontab, you need to set your script in a way that you may register the exceptions and logs (all the prints commands).

Below we can find a example that tells us how to execute this script:

          python unmanage.py -i /root/unmanaged_filtro -m /root/unmanaged_filtro -v /root/unmanaged_filtro -d /root/unmanaged"


You must customize the following lines with your own information:

	mail=imaplib.IMAP4("192.168.xx.x", ###)
	mail.login("username","password")
	result, data = mail.uid('search', None, '(UNSEEN)','(HEADER Subject "Computer Detected without Symantec Client Software")')
	s.sendmail('diego.orellana@akainix.com','xxxxx@akainix.com',msg.as_string())
	s.sendmail('diego.orellana@akainix.com','diego.orellana@akainix.com',msg.as_string())

Also, the regex should be customized to fit your needs:

	macip=re.findall('(width3D"10%">[0-9]+(?:\.[0-9]+){3})<\/td><td (width3D"20%">[0-9a-f]{2}(?:-[0-9a-f]{2}){5})',raw_email3) #juntos

And any other line in order to fit your particular context.

### I hope you find this script useful. Let me know if you have any question. ###


[diagram]:	https://github.com/diegoorellanaga/Scripts-1/blob/master/Scriptdiagram.jpg




