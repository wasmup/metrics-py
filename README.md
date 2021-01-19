# metrics-py

Available Memory, CPU Usage, CPU Temperature, CPU Frequency on Linux

sample output:  
5375MB 4% 59°C 1341MHz

### Install from source

    cd metrics-py/
    sudo install ./metrics.py /usr/local/bin/metrics.py

#### Run

    /usr/bin/python3 /usr/local/bin/metrics.py

## For Xfce4, to show this metrics in panel:

### Install

    sudo apt-get install xfce4-genmon-plugin

Then Right-click on xfce panel (e,g.: top bar) and select `Panel` then press `Add New Items`.
Search for `Generic Monitor` then select `Generic Monitor` and click `Add` button then click `Close`.
Right click on the Generic Monitor Plugin item added to your xfce panel, and click `Properties`.
add `Command` e.g. (for no notification):

    /usr/bin/python3 /usr/local/bin/metrics.py

Or for low memory notification on 512MB set the command to:

    /usr/bin/python3 /usr/local/bin/metrics.py -lmt 512

set the font and size (e.g.: Ubuntu Mono Regular 22), set `Period(s)` (e.g. 10), and unchech `Label`.

