from fastapi import FastAPI
from pydantic import BaseSettings
import typesense
import logging
app = FastAPI()



client = typesense.Client({
    'nodes': [{
        'host': 'de5ul3igzpwo4mxbp-1.a1.typesense.net',
        'port': '443',
        'protocol': 'https'
    }],
    # 'api_key': 'KscLUMHl6UEyLlBp1IPE2IHhp1NpJRAt',
    'api_key': 'OGjoBAaoWS7Uv6YEelPCMQVi5BD9EbbB',
    'connection_timeout_seconds': 2
})



def parse_response(q, response, highlight_start_tag):
    found_results_num = response['found']
    if(found_results_num == 0):
        print("No Results Found!")
        exit()
    result = {}
    parsed_response = {}
    if(found_results_num > 10):
        results_per_page = 10
    else:
        results_per_page = found_results_num
    start_times = response['hits'][0]['document']['start_times']
    for i in range(0, results_per_page):
        text = response['hits'][i]['highlights'][0]['value']
        title = response['hits'][i]['document']['title']
        thumbnail = response['hits'][i]['document']['thumbnail']
        view_count = response['hits'][i]['document']['view_count']
        duration = response['hits'][i]['document']['duration']
        category_id = response['hits'][i]['document']['category_id']
        start_times = response['hits'][i]['document']['start_times']
        transcript = response['hits'][i]['document']['transcript']
        id = response['hits'][i]['document']['id']
        parsed_response[i] = {'title': title,'view_count':view_count,'thumbnail': thumbnail, 'duration':duration,'category_id':category_id,'id': id,'matched_start_times': [], 'transcript': transcript}
        result[i] = {'text': text.split(),
                     'start_times': start_times}
    matched_tokens = q.split()
    last_index = len(matched_tokens)
    word_ranges = {}
    index = 0
    for i in range(0, results_per_page):
        text = result[i]['text']
        word_ranges[i] = []
        if(last_index >= 2):
            for counter, word in enumerate(text, start=1):
                if index == last_index:
                    word_ranges[i].append(counter - index)
                    index = 0
                if (matched_tokens[index] in word) and (highlight_start_tag in word):
                    index += 1
                else:
                    index = 0
        else:
            for counter, word in enumerate(text, start=1):
                if highlight_start_tag in word:
                    word_ranges[i].append(counter)
    for i in range(0, results_per_page):
        start_times = result[i]['start_times']
        word_ranges_list = word_ranges[i]
        first_start_time = int(next(iter(start_times)))
        matched_start_time = None
        for word_index in word_ranges_list:
            isFound = False
            while(not isFound):
                isFound = False
                matched_start_time = start_times.get(str(word_index))
                if matched_start_time == None:
                    if word_index > first_start_time:
                        word_index -= 1
                    else:
                        word_index += 1
                else:
                    parsed_response[i]['matched_start_times'].append(
                        matched_start_time)
                    isFound = True
    return parsed_response

def search_expression(lang,q):
    try : 
        highlight_start_tag = "<found>"
        highlight_end_tag = "</found>"
        collection_name = "english_videos"
        if(lang == "ru"):
            collection_name = "russian_videos"
        elif(lang == "ja"):
            collection_name = "japanese_videos"
        response = client.collections[collection_name].documents.search({
            'q': f'"{q}"',
            'query_by': 'transcript_text',
            # 'filter_by': 'channel := The Weekend',
            'page': 1,
            'highlight_full_fields': 'transcript_text',
            'highlight_start_tag': highlight_start_tag,
            'highlight_end_tag': highlight_end_tag
        })
        parsed_response = parse_response(q, response, highlight_start_tag)
        return parsed_response
        # return response
    except Exception as e:
        logging.error(e)
        return {"error": '404'}



# print(search_expression("many people"))


@app.get("/search")
async def read_root(lang:str,q: str):
    return search_expression(lang,q)
