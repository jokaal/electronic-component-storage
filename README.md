# electronic-component-storage

This repository is for a web-based user application for small-scale electronic component storage. Can be used as a general storage tracking application however features and titles are not generic. **This application is not meant for large scale deployment as it lacks any sort of authentication & security features.**

## Installation

### Prerequisites:

>Python ([Download](https://www.python.org/downloads/))

### Step by step guide:

1. Clone the repository:
```
git clone https://github.com/jokaal/electronic-component-storage.git
```
2. Configure the config.json file as you see fit. SQLite is used by default, the other solution is MySQL or MariaDB. MySQL and MariaDB require the database name, server, username and password. The resulting URL will look something like this:
```
mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}
```
3. Install the required frameworks and libraries. Requirements are found in the requirements.txt file, to install them make sure you are located in your cloned repository:

> NOTE! If you are not installing the application on a server and don't want to install the required libraries on your global Python interpreter then create and use a virtual environment ([Documentation](https://docs.python.org/3/library/venv.html)).

```
pip install -r requirements.txt
```

4. Run the automatic tests and make sure that everything passes:
```
pytest
```

5. Start the application server:
```
waitress-serve --host 127.0.0.1 --port 8001 --call website:create_app
```

6. Your application can now be found by going to http://127.0.0.1:8001 (or whatever address you set it to).


## Development

For development it is recommended to use the built-in server as it allows for debugging and automatically refreshes after saving a file. Running the development server is done by running the code found in *main.py*.

### TODO list:

1. ~~BOM importing for projects~~
2. ~~Copy project to new project~~
3. Export and import current storage state

This is a very minimalistic solution for component storage tracking and as such it is missing many features that other solutions might have. To make developing easier for the future, code is kept well documented and application architecture has to be solid.


