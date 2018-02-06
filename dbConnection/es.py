# -*- coding: utf-8 -*-
from elasticsearch import Elasticsearch


def test():
    es = Elasticsearch(['10.214.208.166:9200'])
    body = {
        "name": "王俊福",
        "s_id": "2162"
    }
    es.create(body)

    pass


if __name__ == "__main__":
    test()
