import os

from bakerydemo.settings.dev import *  # noqa: F403, F401

ROOT_URLCONF = "overrides.urls"

INSTALLED_APPS += [  # noqa: F405
    "wagtail_extended_search",
    "overrides.patching",
]

OPENSEARCH_URL = os.environ.get("OPENSEARCH_URL")

ELASTICSEARCH_DSL = {
    "default": {
        "hosts": OPENSEARCH_URL,
    },
}

WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail_extended_search.backends.backend.CustomSearchBackend",
        "AUTO_UPDATE": True,
        "ATOMIC_REBUILD": True,
        "URLS": [OPENSEARCH_URL],
        "INDEX": "wagtail",
        "TIMEOUT": 60,
        "OPTIONS": {},
        "INDEX_SETTINGS": {
            "settings": {
                "index": {
                    "number_of_shards": 1,
                },
                "analysis": {
                    "filter": {
                        "english_snowball": {
                            "type": "snowball",
                            "language": "english",
                        },
                        "remove_spaces": {
                            "type": "pattern_replace",
                            "pattern": "[ ()+]",
                            "replacement": "",
                        },
                    },
                    "analyzer": {
                        "snowball": {
                            "tokenizer": "standard",
                            "filter": [
                                "english_snowball",
                                "stop",
                                "lowercase",
                                "asciifolding",
                            ],
                        },
                        # Used for keyword fields like acronyms and phone
                        # numbers - use with caution (it removes whitespace and
                        # tokenizes everything else into a single token)
                        "no_spaces": {
                            "tokenizer": "keyword",
                            "filter": "remove_spaces",
                        },
                    },
                },
            }
        },
    }
}

SEARCH_EXTENDED = {
    "boost_parts": {
        "extras": {
            # "page_tools_phrase_title_explicit": 2.0,
            # "page_guidance_phrase_title_explicit": 2.0,
        },
        "query_types": {
            "phrase": 20.5,
        },
    }
}
SEARCH_ENABLE_QUERY_CACHE = False
