from elasticsearch_dsl.connections import connections
connections.create_connection()

from django_elasticsearch_dsl import DocType, Index
from .models import Titles
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

# Create a connection to ElasticSearch

client = Elasticsearch()
my_search = Search(using=client)

titles = Index('titles')
titles.settings(
    number_of_shards=1,
    number_of_replicas=0
)

@titles.doc_type
class TitlesDocument(DocType):

    class Meta:
        model = Titles
        fields = ['title',]

def search(title):
    query = my_search.query("match", title=title)
    response= query.execute()
    return response
