## Installation

Add with your package manager of choice:
`pip install wagtail-extended-search`

Add to your installed apps:
```python
INSTALLED_APPS = [
    ...
    'wagtail_extended_search',
    ...
]
```

Set the search backend to `wagtail_extended_search.backends.ExtendedSearch` in your settings:
```python
WAGTAILSEARCH_BACKENDS = {
    'default': {
        'BACKEND': 'wagtail_extended_search.backends.ExtendedSearch',
    },
}
```

## Running locally

We use the [Wagtail Bakery Demo](https://github.com/wagtail/bakerydemo) as a base Wagtail project to run the package locally for testing purposes.

### Set up

These commands can be used to get set up:

```bash
# Clone the repository
make bakery-setup
# Build and initialise the docker containers
make bakery-init
# Wait around 10 seconds
# Run the project
make bakery-start
```

The bakery demo should now be running at [http://localhost:8000](http://localhost:8000).

### Updating/Resetting

To update the bakery demo to the latest version, you can down the containers and pull the latest version.
Or run the following to clean up the bakery demo and start from scratch:

```bash
# Down the containers and delete the `bakerydemo` directory
make bakery-clear
# Follow the set up commands above
```
