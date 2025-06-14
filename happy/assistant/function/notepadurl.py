from urllib.parse import urlencode

def create_content_url(content):
    query_string = urlencode({'content': content})

    return "?" + query_string

if __name__ == "__main__":
    print(create_content_url("Hello, world!"))
