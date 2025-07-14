from socket import gethostname, gethostbyname, gethostbyname_ex

hostname = gethostname()

ip_list = gethostbyname_ex(hostname)[2]
for i in ip_list:
    print(i)

