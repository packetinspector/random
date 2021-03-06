from fuzzywuzzy import fuzz
import json
import http.server
import socketserver
import requests
import re
from dateutil import parser
import datetime
import urllib

# import pprint
PORT = 1234

# HTML Stuff
style = '<style type="text/css">table a:link{color: #666;font-weight: bold;text-decoration:none;}table a:visited{color: #999999;font-weight:bold;text-decoration:none;}table a:active,table a:hover{color: #bd5a35;text-decoration:underline;}table{font-family:Arial, Helvetica, sans-serif;color:#666;font-size:12px;text-shadow: 1px 1px 0px #fff;background:#eaebec;margin:20px;border:#ccc 1px solid;-moz-border-radius:3px;-webkit-border-radius:3px;border-radius:3px;-moz-box-shadow: 0 1px 2px #d1d1d1;-webkit-box-shadow: 0 1px 2px #d1d1d1;box-shadow: 0 1px 2px #d1d1d1;}table th{padding:21px 25px 22px 25px;border-top:1px solid #fafafa;border-bottom:1px solid #e0e0e0;background: #ededed;background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));background: -moz-linear-gradient(top, #ededed, #ebebeb);}table th:first-child{text-align: left;padding-left:20px;}table tr:first-child th:first-child{-moz-border-radius-topleft:3px;-webkit-border-top-left-radius:3px;border-top-left-radius:3px;}table tr:first-child th:last-child{-moz-border-radius-topright:3px;-webkit-border-top-right-radius:3px;border-top-right-radius:3px;}table tr{text-align: center;padding-left:20px;}table td:first-child{text-align: left;padding-left:20px;border-left: 0;}table td{padding:8px;border-top: 1px solid #ffffff;border-bottom:1px solid #e0e0e0;border-left: 1px solid #e0e0e0;background: #fafafa;background: -webkit-gradient(linear, left top, left bottom, from(#fbfbfb), to(#fafafa));background: -moz-linear-gradient(top, #fbfbfb, #fafafa);}table tr.even td{background: #f6f6f6;background: -webkit-gradient(linear, left top, left bottom, from(#f8f8f8), to(#f6f6f6));background: -moz-linear-gradient(top, #f8f8f8, #f6f6f6);}table tr:last-child td{border-bottom:0;}table tr:last-child td:first-child{-moz-border-radius-bottomleft:3px;-webkit-border-bottom-left-radius:3px;border-bottom-left-radius:3px;}table tr:last-child td:last-child{-moz-border-radius-bottomright:3px;-webkit-border-bottom-right-radius:3px;border-bottom-right-radius:3px;}table tr:hover td{background: #f2f2f2;background: -webkit-gradient(linear, left top, left bottom, from(#f2f2f2), to(#f0f0f0));background: -moz-linear-gradient(top, #f2f2f2, #f0f0f0);}</style>'
js = '''<script src='https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js'></script>
<script>$('table tr.child').hide();
$('table tr.parent').on('click', function(e) {
   // e.preventDefault();
   $(this).nextUntil('.parent').toggle(); 
});</script>'''

NZ_API_KEY = ""
nz_url = ""

sab_url = 'http://sab:8000/api'
sab_nzb_key = ''

fuzziness = 65

last_served = datetime.datetime.now(datetime.timezone.utc)


class Serve(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        global style
        global last_served
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
        self.end_headers()
        print(self.requestline)
        if self.path == '/':
            action = 'search'
        elif self.path == '/browse':
            action = 'browse'
        else:
            return
        # Style
        self.wfile.write(style.encode())
        # Body
        if action == 'browse':
            o = indent_table(group_matches(browse_titles()))
        elif action == 'search':
            o = indent_table(group_matches(search_titles()))
        self.wfile.write(o.encode())
        # Javascript
        self.wfile.write(js.encode())
        last_served = datetime.datetime.now(datetime.timezone.utc)
        return


def offline_titles():
    with open('test.json', 'r') as f:
        input_json = json.load(f)
    return process_results(input_json)


def diff_date(d):
    return round((datetime.datetime.now(datetime.timezone.utc) - parser.parse(d)).total_seconds() / 3600, 1)


def remove_things(s):
    # Remove things that won't be unique to increase match
    p = re.compile('hevc|x265-MeGusta|x265|1080p|720p|internal|proper|x264|amzn|web-dl|hdtv|h264|ddp', re.IGNORECASE)
    return p.sub('', s)


def process_results(input_json):
    return [{'title': x['title'], 'gtitle': remove_things(x['title']), 'download': sab_link(x['link']), 'link': x['guid']['text'], 'age': diff_date(x['pubDate'])} for x in input_json['item']]


def search_titles():
    print("Fetching Search Results...")
    querystring = {"t": "search", "q": "hevc 1080p", "o": "json", "apikey": NZ_API_KEY, "cat": 5000}
    input_json = requests.request("GET", nz_url, params=querystring).json()
    ten80 = process_results(input_json)
    # Query again and combine
    querystring = {"t": "search", "q": "hevc", "o": "json", "apikey": NZ_API_KEY, "cat": 5000}
    input_json = requests.request("GET", nz_url, params=querystring).json()
    reg = process_results(input_json)
    return ten80 + reg


def sab_link(link):
    querystring = { "mode": "addurl", "name": link, "apikey": sab_nzb_key, "output": "text"}
    return sab_url + '?' + urllib.parse.urlencode(querystring)


def browse_titles():
    print("Browsing...")
    cats = [5040, 5010, 2040]
    nz_rss_url = 'https://nzb/rss'
    browse_all = []
    for cat in cats:
        querystring = {"t": cat, "i": 22730, "o": "json", "r": NZ_API_KEY, "num": 50}
        input_json = requests.request("GET", nz_rss_url, params=querystring).json()
        reg = process_results(input_json)
        browse_all = browse_all + reg
    return browse_all


def indent_table(a):
    output = '<table>'
    last_age = (datetime.datetime.now(datetime.timezone.utc) - last_served).seconds / 3600
    # Loop
    for x in a:
        t = x.pop()
        if t['age'] <= last_age:
            t['new'] = 'NEW!'
        else:
            t['new'] = ''
        output = output + "<tr class=\"parent\"><td><b><a href='{link}'>{title}</a> [{age} hours]</b> <a href=\"{download}\">Push</a> {new}</td></tr>".format(**t)
        # If after pop, then indent all the others
        if (len(x) != 0):
            for y in x:
                output = output + "<tr class=\"child\"><td></td><td>{title} [{age} hours]</td></tr>".format(**y)
    output = output + '</table>'
    return str(output)


def group_matches(titles):
    # From S/O, Thanks!
    grs = list()
    for name in titles:
        for g in grs:
            if all(fuzz.ratio(name['gtitle'], w['gtitle']) > fuzziness for w in g):
                g.append(name)
                break
        else:
            grs.append([name, ])
    s = []
    # Sort each group
    for t in grs:
        s.append(sorted(t, key=lambda d: d['age'], reverse=True))
    # Now sort the entire list, by the earliest in each group
    return sorted(s, key=lambda d: d[-1]['age'])


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
