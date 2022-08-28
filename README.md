# Automated-Repo
Clone/Update/Backup a configurable list of git repositories with one command!

## Installation
Just install the requirements
```
pip3 install -r requirements.txt
```

## Configuration
The repo contains an example `repos.json`. Every repo can have a custom name and a subdirectory to organize the repos.

This is the structure of the JSON file:
```json
[
    {
        "name": "test", // If the name is empty, it'll use the name of the url
        "url": "https://github.com/whatever",
        "tags": ["RCE", "SSTI"],
        "subfolder": "" // If empty, download in the current dir.
    }
]
```

## Usage
After configuring the repo, you have three different actions:
- `clone`: Clone every repo (-f to update the existing ones)
- `pull`: Update every cloned repo (-f to clone the non-existing ones)
- `backup`: Save every repo as tar (-f to download every repo fresh before archiving)

The parameters allowed are:
- `-t`: Tags that will get elaborated
- `-r`: Repo that will get elaborated
- `-nt`: Tags that will get ignored
- `-nr`: Repo that will get ignored
