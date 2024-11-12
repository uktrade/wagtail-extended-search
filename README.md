# Wagtail Extended Search

Improve the default Wagtail search behaviour by adding support for more complex indexing and querying.
This work is heavily based on the [extended_search](https://github.com/uktrade/digital-workspace-v2/tree/2cecde1de6c790b0176ef79cab76f88d173cf244/src/extended_search) application from the [uktrade/digital-workspace-v2](https://github.com/uktrade/digital-workspace-v2/) project.

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

## Search changes

The search behaviour we are aiming for with this package is based on the [How GitHub Docs' new search works](https://github.blog/engineering/how-github-docs-new-search-works/) blog.

Some of the changes in this package are only compatible with an ElasticSearch backend, while others should be cross-compatible.

### Indexing

The default Wagtail search allows for indexing fields in a 1-to-1 manner.

This package expands the Wagtail behaviour to allow a field to be indexed in a 1-to-many manner. This unlocks the ability to index a field in different ways so that you can build more complex behaviours.

### Querying

The default Wagtail search behaviour works for ElasticSearch uses some really simple logic. For each indexable model, indexable page content is concatenated into a single `_all_text` field. Then the search query does a simple search against that indexed field.

This package brings a custom query builder object that looks over the indexed models and builds a query for the relevant models so that we can have a more targeted search.

## Running local development

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
