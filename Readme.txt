This is a CGI-based web interface to video manager 2.

These files need to be installed into your CGI scripts directory, and python needs to be enabled within your web browser for CGI Execution.  As an example,
here is my configuration for my apache 1 server on my ReadyNAS

Alias "/web" "/c/web"
<Location "/web">
  Options Indexes ExecCGI
  Order allow,deny
  Allow from all
</Location>

LoadModule python_module /usr/lib/apache2/modules/mod_python.so
    AddIcon /images/Icons/p.gif .pl .py
    AddHandler cgi-script .cgi .sh .pl .py




Also, the pytivo shares need to be configured into your web server so that the video artwork can be served.  As an example, Here is the
configuration information I had to add:


Alias "/My_Podcasts" "/c/media/Videos/Podcasts"
<Location "/My_Podcasts">
  Options Indexes
  Order allow,deny
  Allow from all
</Location>

Alias "/My_Movies" "/c/media/Videos/Movies"
<Location "/My_Movies">
  Options Indexes
  Order allow,deny
  Allow from all
</Location>

Alias "/My_Recorded_TV" "/c/media/Videos/TV"
<Location "/My_Recorded_TV">
  Options Indexes
  Order allow,deny
  Allow from all
</Location>


