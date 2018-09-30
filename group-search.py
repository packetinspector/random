from fuzzywuzzy import fuzz
import json
import http.server
import socketserver
import requests

# import pprint
PORT = 1234
style = '<style type="text/css">table a:link{color: #666;font-weight: bold;text-decoration:none;}table a:visited{color: #999999;font-weight:bold;text-decoration:none;}table a:active,table a:hover{color: #bd5a35;text-decoration:underline;}table{font-family:Arial, Helvetica, sans-serif;color:#666;font-size:12px;text-shadow: 1px 1px 0px #fff;background:#eaebec;margin:20px;border:#ccc 1px solid;-moz-border-radius:3px;-webkit-border-radius:3px;border-radius:3px;-moz-box-shadow: 0 1px 2px #d1d1d1;-webkit-box-shadow: 0 1px 2px #d1d1d1;box-shadow: 0 1px 2px #d1d1d1;}table th{padding:21px 25px 22px 25px;border-top:1px solid #fafafa;border-bottom:1px solid #e0e0e0;background: #ededed;background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));background: -moz-linear-gradient(top, #ededed, #ebebeb);}table th:first-child{text-align: left;padding-left:20px;}table tr:first-child th:first-child{-moz-border-radius-topleft:3px;-webkit-border-top-left-radius:3px;border-top-left-radius:3px;}table tr:first-child th:last-child{-moz-border-radius-topright:3px;-webkit-border-top-right-radius:3px;border-top-right-radius:3px;}table tr{text-align: center;padding-left:20px;}table td:first-child{text-align: left;padding-left:20px;border-left: 0;}table td{padding:8px;border-top: 1px solid #ffffff;border-bottom:1px solid #e0e0e0;border-left: 1px solid #e0e0e0;background: #fafafa;background: -webkit-gradient(linear, left top, left bottom, from(#fbfbfb), to(#fafafa));background: -moz-linear-gradient(top, #fbfbfb, #fafafa);}table tr.even td{background: #f6f6f6;background: -webkit-gradient(linear, left top, left bottom, from(#f8f8f8), to(#f6f6f6));background: -moz-linear-gradient(top, #f8f8f8, #f6f6f6);}table tr:last-child td{border-bottom:0;}table tr:last-child td:first-child{-moz-border-radius-bottomleft:3px;-webkit-border-bottom-left-radius:3px;border-bottom-left-radius:3px;}table tr:last-child td:last-child{-moz-border-radius-bottomright:3px;-webkit-border-bottom-right-radius:3px;border-bottom-right-radius:3px;}table tr:hover td{background: #f2f2f2;background: -webkit-gradient(linear, left top, left bottom, from(#f2f2f2), to(#f0f0f0));background: -moz-linear-gradient(top, #f2f2f2, #f0f0f0);}</style>'
API_KEY = ""
url = ""
fuzziness = 65


class Serve(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        global style
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        print(self.requestline)
        if self.requestline != 'GET / HTTP/1.1':
            return
        self.wfile.write(style.encode())
        o = indent_table(group_matches(online_titles()))
        self.wfile.write(o.encode())
        return


def offline_titles():
    with open('test.json', 'r') as f:
        input_json = json.load(f)
    return [x['title'] for x in input_json['item']]


def remove_things(s):
    # Remove things that won't be unique to increase matching
    return s.replace('hevc', '').replace('HEVC', '').replace('x265-MeGusta', '').replace('x265', '').replace('720p', '').replace('1080p', '')


def online_titles():
    print("Fetching Search Results...")
    querystring = {"t": "search", "q": "hevc 1080p", "o": "json", "apikey": API_KEY, "cat": 5000}
    input_json = requests.request("GET", url, params=querystring).json()
    ten80 = [remove_things(x['title']) for x in input_json['item']]
    # Query again and combine
    querystring = {"t": "search", "q": "hevc", "o": "json", "apikey": API_KEY, "cat": 5000}
    input_json = requests.request("GET", url, params=querystring).json()
    reg = [remove_things(x['title']) for x in input_json['item']]
    return ten80 + reg


def indent_table(a):
    output = '<table>'
    # Loop
    for x in a:
        output = output + "<tr><td><b>{}</b></td></tr>".format(x.pop())
        # If after pop, then indent all the others
        if (len(x) != 0):
            for y in x:
                output = output + "<tr><td></td><td>{}</td></tr>".format(y)
    output = output + '</table>'
    return str(output)


def group_matches(titles):
    # From S/O, Thanks!
    grs = list()
    for name in titles:
        for g in grs:
            if all(fuzz.ratio(name, w) > fuzziness for w in g):
                g.append(name)
                break
        else:
            grs.append([name, ])
    return grs


if __name__ == '__main__':
    Handler = http.server.SimpleHTTPRequestHandler
    Handler = Serve
    httpd = socketserver.TCPServer(("", PORT), Handler)

    print("serving at port", PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()