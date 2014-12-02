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



In addition to the web server configuration, there are w few options you can set in lconfig.py.  Bear in mind that when you are changing values in this file,
you are actually changing python source code, so python syntax should be adhered to.  Just follow the examples in the file

HMEDIR is a string that is set to the directory where you have HME installed.  Note this is the HME directory, not the vidmgr directory.  It is assumed that
vidmgr will be a subdirectory of the directory specified here

HOMELINK and HOMELABEL are used to link this CGI script into any other web sites you may have.  HOMELINK is the relative path to where this applicaiton will
go when you exit.  If you set this to None (without quotes) no home link will appear on the page.  HOMELABEL is the text that will appear in the link.

TITLE is the title text that goes on the top of the pages.

The remaining options are all for security purposes - for restricting pushing and/or deleting to specified IP addresses or subnets.  The comments in the file explain
how these fields are used.


