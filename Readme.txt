Github error:
http://stackoverflow.com/questions/18356502/github-failed-to-connect-to-github-443-windows-failed-to-connect-to-github

Well I did following steps
1.
Google the error

2.
Got to SO Links(here(http://stackoverflow.com/questions/496277/git-error-fatal-unable-to-connect-a-socket-invalid-argument), here(http://stackoverflow.com/questions/3512202/github-https-access)) which suggested the same thing, that I have to update the Git Config for proxy setting 

3.
Damn, can not see proxy information from control panel. IT guys must have hidden it. I can not even change the setting to not to use proxy.

4.
Found this wonderful tutorial(http://superuser.com/questions/346372/how-do-i-know-what-proxy-server-im-using) of finding which proxy your are connected to

5.
Updated the http.proxy key in git config by following command



git config --global http.proxy http[s]://userName:password@proxyaddress:port
6.
Error - could not resolve proxy some@proxyaddress:port. It turned out my password had @ symbol in it. 

7.
Encode @ in your password to %40 because git splits the proxy setting by @



git config --global http.proxy http[s]://userName:password(encoded)@proxyaddress:port

Baam ! It worked !

Note - I just wanted to answer this question for souls like me, who would come looking for answer on SO :D
