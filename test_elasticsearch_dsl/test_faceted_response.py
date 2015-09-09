from elasticsearch_dsl.faceted_search import FacetedSearch, FacetedResponse
from elasticsearch_dsl import A

class ProductSearch(FacetedSearch):
    doc_types = ['product']
    fields = ('title', 'body', )

    facets = {
        'price': A('range', field='price', keyed=True, ranges=[
            {'key': 'Under 60', 'to': 60},
            {'key': '60-150', 'from': 60, 'to': 150},
            {'key': '150+', 'from': 150}
        ]),
        'availability': A('range', field='availability', ranges=[
            {'to': 0},
            {'from': 0, 'to': 5},
            {'from': 5}
        ])
    }

def test_faceted_response(faceted_response):
    bs = ProductSearch('white tshirt')
    response = FacetedResponse(bs, faceted_response)
    assert {
        'availability': [
            ('*-0.0', 10, False),
            ('0.0-5.0', 20, False),
            ('5.0-*', 70, False)
        ],
        'price': [
            ('60-150', 70, False),
            ('Under 60', 10, False),
            ('150+', 20, False)
        ]
    } == response.facets.to_dict()


def test_faceted_response_with_filter(faceted_response):
    bs = ProductSearch('white tshirt')
    bs._raw_filters['price'] = '60-150'
    response = FacetedResponse(bs, faceted_response)
    assert {
        'availability': [
            ('*-0.0', 10, False),
            ('0.0-5.0', 20, False),
            ('5.0-*', 70, False)
        ],
        'price': [
            ('60-150', 70, True),
            ('Under 60', 10, False),
            ('150+', 20, False)
        ]
    } == response.facets.to_dict()
