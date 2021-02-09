# Surface Estimator

## API

How to install the requirements and launch the API to be called from the frontend client

### Install requirements

```bash
pip3 install -r requirements.txt
```

### Server Documentation

<${baseURL}/docs#/>

### Launch server

The server is launched by default on port 8000.
Please be sure to have filled the `surface.config` file with the desired values before launching the server.

```bash
uvicorn main:app --reload
```

To change the port of the server you can simply add these lines at the end of `main.py`:

```python=
if __name__ == "__main__":
    uvicorn.run(app, port=8000)
```

then run

```bash
python3 main.py
```

## CLI

### Lauch tests

Work in progress

### Launch batch computation

It is also possible to use the module for a quick computation of a batch of coordinates registered in a file.
You'll then have to indicate the corresponding input and output paths in the `[Batch]` section of the configuration file.

```bash
python3 batchs.py -c path/to/config/file.config
```

The input file should be formatted as follows

```csv
Latitude1;Longitude1
Latitide2;Longitude2
...;...
```

To know more about the format of the output please refer to the `SolutionCombiner` object and its overwritten `str` method
