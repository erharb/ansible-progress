# ansible-progress
Making progress with Ansible modules and playbooks

# Ansible Callback Plugins
To start using the plugins, copy the ```callback_plugins``` folder and its contents from this repository into your working Ansible playbook directory. Some plugins may also need additional configuration as noted in their sections below.

## Progress Default
```callback_plugins/progress_default.py```: This plugin is an extension of the default Ansible callback plugin to modify the look of the displayed output to show abbreviated task results on the same line while retaining the default Ansible log output.

* To enable this plugin you will need to modify/create the ```ansible.cfg``` file located in your working Ansible playbook directory. Set the following properties in the ```[defaults]``` section:

```
[defaults]
callback_plugins = ./callback_plugins
stdout_callback = progress_default
```

* As each task host returns with non-failed results they will be printed in an abbreviated format on the same line. Failures will still print the default to display. Here is a sample of the display output when combined with the 'Progress Dots' plugin referenced below (color coding not shown as it would in the terminal):

```
PLAY [Finding all installed packages] ******************************************

TASK [Gathering Facts] *********************************************************
. . centos1[=] centos2[=] centos3[=]
TASK [Get list of installed packages] ******************************************
. . centos1[=] . centos3[=] centos2[=]

PLAY [Setup postgres server] ***************************************************

TASK [Gathering Facts] *********************************************************
. . centos2[=]
TASK [Install Postgres server] *************************************************
. . . . . . . . . . . . . centos2[~]

PLAY [Setup php web server] ****************************************************

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

## Progress Dots
```callback_plugins/progress_dots.py```: This plugin prints a dot on the same line every 2 seconds (customizable) that passes after each task starts as the work is being performed. This plugin can also be used with the default Ansible provided stdout callback.

* To enable this plugin you will need to modify/create the ```ansible.cfg``` file located in your working Ansible playbook directory. Make sure the following property is set in the ```[defaults]``` section:

```
[defaults]
callback_plugins = ./callback_plugins
```

* Each time a new task is started it will start a background loop thread that will wait the default of 2 seconds before printing a dot and every 2 seconds after. If a task takes less then 2 seconds a dot will not be printed.

* To set a custom loop time, the environment variable ```PROGRESS_TIME``` can be set to a number prior to running ansible (must be able to cast as float). For example, to set a 5 second loop time:

```
$ export PROGRESS_TIME=5
$ ansible-playbook ...
...
TASK [set_fact] ****************************************************************
ok: [deployTarget -> localhost]

TASK [Get host details] ********************************************************
. . . . . . . . . . . . . . ok: [deployTarget]

TASK [Process host details] ****************************************************
. . . ok: [deployTarget -> localhost]
```
