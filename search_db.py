from typesense_client import client

def search_expression(q):
    highlight_start_tag = "<found>"
    highlight_end_tag = "</found>"
    response = client.collections['english_videos'].documents.search({
        'q': f'"{q}"',
        'query_by': 'transcript_text',
        # 'filter_by': 'channel := The Weekend',
        'page': 1,
        'highlight_full_fields': ['transcript_text'],
        'highlight_start_tag': highlight_start_tag,
        'highlight_end_tag': highlight_end_tag
    })
    return response
print(search_expression("many people"))