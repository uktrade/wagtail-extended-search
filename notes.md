# Wagtail core code

- Improvements to indexing
  - Multi-field indexing
- Improvements to query classes (Only fields, etc.)
- Improvements to query parsing
  - Stuff in a queryset filter turning into the search fields)
  - Query batching due to parsing?
- Indexing fields by different config at different model levels

What will conceptually get into wagtail:
- Structural and cross search backend compatible improvements.
- Better override hooks and capabilities.

## Known issues

- Relational fields in search
- Class MRO (diverging tree)
- Removing a field from the search index if a parent class indexes it and a child class doesn't want to

## Things to look into more

- Fields indexing based on which model has configured it
- Combining searches into fewer calls to Opensearch/Search backend
  - Example: merging count queries?
- Search facets and filtering
- Query caching
  - Currently done in python, but each search backend might have its own caching mechanism
  - Look into building OpenSearch templates at build time and then reusing them at runtime

# Package code

- Multi dimensional search
  - Configuring the dimensions
    - Fields
    - Analysers
    - Query type (and/or)
  - Building of the query
- Wagtail admin settings
- Wagtail admin search explore page
- Search vector concept?

Think about splitting the package up into different "sub-packages" that contain full concepts (hopefully making it easier to open RFCs/PRs to Wagtail)

# Intranet code

Anything specific to the project level structure and code.
Implementation of the package code in the project.