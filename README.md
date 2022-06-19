# homepage
Code to generate page with links to commonly used sites

## Requirements
- Python (3.6 or greater)
- node

## Installation

### 1. Create virtualenv

`python3 -m venv homepage-venv`

### 2. Clone Repo

`git clone https://github.com/jocassid/homepage.git`

### 3. Activate the virtualenv

In Linux / Unix /Mac OS

`source homepage-venv/bin/activate`

Windows (Powershell)

`& homepage-venv\Scripts\activate.ps1`

### 4. Install Python dependencies

```bash
cd homepage
pip install -r requirements.txt
```

### 5. Install JavaScript (Node) dependencies

Run this command within the `homepage` directory

`npm install`

## Using the homepage script

Using example.yaml as a template, create your own `.yaml` file with the links
and other page elements you wish to include.  If you want your yaml file to 
reside within the `homepage` directory created a `homepage/private` directory
and store your `.yaml` file there.

The syntax for running the script is:

`./homepage.py PATH_TO_YAML_FILE OUTPUT_DIRECTORY`

On Windows systems you typically need to use the following command

`python3 .\homepage.py PATH_TO_YAML_FILE OUTPUT_DIRECTORY`



