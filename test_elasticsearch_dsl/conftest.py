# -*- coding: utf-8 -*-

import os

from elasticsearch.helpers.test import get_test_client, SkipTest
from elasticsearch.helpers import bulk

from pytest import fixture, skip
from mock import Mock

from .test_integration.test_data import DATA, create_git_index

_client_loaded = False

@fixture(scope='session')
def client(request):
    # inner import to avoid throwing off coverage
    from elasticsearch_dsl.connections import connections
    # hack to workaround pytest not caching skip on fixtures (#467)
    global _client_loaded
    if _client_loaded:
        skip()

    _client_loaded = True
    try:
        client = get_test_client(nowait='WAIT_FOR_ES' not in os.environ)
        connections.add_connection('default', client)
        return client
    except SkipTest:
        skip()

@fixture
def write_client(request, client):
    def cleanup():
        client.indices.delete('test-*')
    request.addfinalizer(cleanup)
    return client

@fixture
def mock_client(request):
    # inner import to avoid throwing off coverage
    from elasticsearch_dsl.connections import connections

    def reset_connections():
        c = connections
        c._conn = {}
        c._kwargs = {}
    request.addfinalizer(reset_connections)

    client = Mock()
    client.search.return_value = dummy_response()
    connections.add_connection('mock', client)
    return client

@fixture(scope='session')
def data_client(request, client):
    # create mappings
    create_git_index(client, 'git')
    # load data
    bulk(client, DATA, raise_on_error=True, refresh=True)
    # make sure we clean up after ourselves
    request.addfinalizer(lambda: client.indices.delete('git'))
    return client

@fixture
def dummy_response():
    return {
      "_shards": {
        "failed": 0,
        "successful": 10,
        "total": 10
      },
      "hits": {
        "hits": [
          {
            "_index": "test-index",
            "_type": "company",
            "_id": "elasticsearch",
            "_score": 12.0,

            "_source": {
              "city": "Amsterdam",
              "name": "Elasticsearch",
            },
          },
          {
            "_index": "test-index",
            "_type": "employee",
            "_id": "42",
            "_score": 11.123,
            "_parent": "elasticsearch",

            "_source": {
              "name": {
                "first": "Shay",
                "last": "Bannon"
              },
              "lang": "java",
              "twitter": "kimchy",
            },
          },
          {
            "_index": "test-index",
            "_type": "employee",
            "_id": "47",
            "_score": 1,
            "_parent": "elasticsearch",

            "_source": {
              "name": {
                "first": "Honza",
                "last": "Král"
              },
              "lang": "python",
              "twitter": "honzakral",
            },
          },
          {
            "_index": "test-index",
            "_type": "employee",
            "_id": "53",
            "_score": 16.0,
            "_parent": "elasticsearch",
          },
        ],
        "max_score": 12.0,
        "total": 123
      },
      "timed_out": False,
      "took": 123
    }

@fixture
def faceted_response():
    return {
        "_shards": {
            "failed": 0,
            "successful": 10,
            "total": 10
        },
        "hits": {
            "hits": []
        },
        "aggregations": {
            "_filter_price": {
                "doc_count": 100,
                "price": {
                    "buckets": {
                        "Under 60": {
                            "to": 60,
                            "to_as_string": "60",
                            "doc_count": 10
                        },
                        "60-150": {
                            "from": 60,
                            "from_as_string": "60.0",
                            "to": 150,
                            "to_as_string": "150",
                            "doc_count": 70
                        },
                        "150+": {
                            "from": 150,
                            "from_as_string": "150.0",
                            "doc_count": 20
                        }
                    }
                }
            },
            "_filter_availability": {
                "doc_count": 100,
                "availability": {
                    "buckets": [
                        {
                            "key": "*-0.0",
                            "to": 0,
                            "to_as_string": "0.0",
                            "doc_count": 10
                        },
                        {
                            "key": "0.0-5.0",
                            "from": 0,
                            "from_as_string": "0.0",
                            "to": 5,
                            "to_as_string": "5.0",
                            "doc_count": 20
                        },
                        {
                            "key": "5.0-*",
                            "from": 5,
                            "from_as_string": "5.0",
                            "doc_count": 70
                        }
                    ]
                }
            }
        },
        "timed_out": False,
        "took": 123
    }
