### Setup Virtual env

```
python3.9 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

### Usage
python main.py [config file]

see `configs/example.yml` for config file options

### VSCode setup to run

To debug with the testing config files, 
add the following config to `.vscode/launch.json`

```        
        {
            "name": "Collect Process",
            "type": "python",
            "request": "launch",
            "program": "collect.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "args": ["configs/test-collect.yml"],
            "env": {"LOG_LEVEL": "DEBUG"}
        },
        {
            "name": "Post Process",
            "type": "python",
            "request": "launch",
            "program": "post.py",
            "console": "integratedTerminal",
            "justMyCode": true,
            "args": ["configs/test-post.yml"],
            "env": {"LOG_LEVEL": "DEBUG"}
        },
```

### MQTT Topics

`/ping/<asset>` all ping tags from all machines.   

`/<asset>/counter/#` all counter tags for one asset

### Environment Variables

Set `LOG_LEVEL` to desired level.  Default is INFO

Set `LOG_LOC` to log file directory. If not set, no log files generated

### Changes
#### 23/11/22
  - Moving to seperate collect and post processes.  This will allow using mqtt or direct db writes based on config files
  - collect.py will now write entries to files in a directory and post.py will poll it and push to the db.

#### 24/01/26
  - Added Dockerfile and docker-compose files.  Can now run on server for modbus applications