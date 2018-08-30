# ansible-progress
Making progress with Ansible modules and playbooks

# Ansible Callback Plugins
To start using the plugins, copy the ```callback_plugins``` folder and its contents from this repository into your working Ansible playbook directory. Some plugins may also need additional configuration as noted in their sections below.

## Progress Dot Display (Default)
This plugin is an extension of the default Ansible callback plugin to modify the default look of the displayed output to display indeterminate progress dots while retaining the default log output.

* To enable this plugin place you will also have to create/modify the ```ansible.cfg``` file located in your working Ansible playbook directory. Add or set the following property in the ```[defaults]``` section:
```
[defaults]
stdout_callback = progress_default
```

* The current version just prints a dot every 1 second that passes after each task starts and an abbreviated task result indicator as hosts complete the task on the same line. Failures will still print the default display. Here is a sample of the display output (color coding not shown as it would in the terminal):
```
PLAY [Finding all installed packages] ******************************************

TASK [Gathering Facts] *********************************************************
. . centos1[=] centos2[=] centos3[=] 
TASK [Get list of installed packages] ******************************************
. . centos1[=] . centos3[=] centos2[=] 

PLAY [Setup postgres server] **********************************************

TASK [Gathering Facts] *********************************************************
. . centos2[=] 
TASK [Install Postgres server] *************************************************
. . . . . . . . . . . . . centos2[~] 

PLAY [Setup php web server] ***********************************************

TASK [Gathering Facts] *********************************************************
. . centos3[=] 
TASK [Install PHP server] ******************************************************
. . . . . . . . . . . . . . . . . . . . . . . centos3[~]
```
Legend:
* ```centos1, centos2, centos3``` are sample inventory names
* ```[=]``` (green) indicates "OK", "SUCCESS", or no change
* ```[~]``` (yellow) indicates "CHANGED"
* ```[>]``` (cyan) indicates "SKIPPED"
* ```[!]``` (red) indicates "FAILED"
