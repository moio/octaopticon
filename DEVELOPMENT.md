## Dependencies

This project uses `pip` for dependency management. To refresh all dependencies:

* Activate the [virtual environment](https://docs.python.org/3/library/venv.html):
  * macOS and Linux: `source venv/bin/activate`
  * Windows: `venv\Scripts\activate`

```sh
cp unversioned_requirements.txt requirements.txt
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

## Run tests

From an activated virtual environment:
```sh
python -m pytest -v -s
```

## Run linter

From an activated virtual environment:
```sh
flake8
```

## Run in Docker from source

```sh
docker build -t ghcr.io/moio/octaopticon:devel .
docker run -it ghcr.io/moio/octaopticon:devel
```
