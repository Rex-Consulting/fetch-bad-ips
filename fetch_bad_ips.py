#!/usr/local/bin/python
# Copyright 2018 Rex Consulting, Inc.

# Rex Consulting hereby grants to Client, solely for Client's internal business purposes, a
# non exclusive, transferable and assignable, royalty-free, paid-up, irrevocable worldwide
# license to copy, modify, use and, as applicable, execute the Work Product. The above
# copyright notice and this permission notice shall be included in allcopies or substantial
# portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import os
import argparse
import time
import re
from elasticsearch import Elasticsearch, TransportError, ConnectionError

parser = argparse.ArgumentParser(description='Does a search for a specific field value then aggregates on a given field. Returns given field values. Once this is done, it display the most recent document containing the bucketized results, along with a set of chosen values.')
parser.add_argument('--doctype', '-d', required=True, help='The doctype, either syslog or eventlog')
parser.add_argument('--fieldname', '-f', required=True, help='The field name to filter out result')
parser.add_argument('--fieldvalue', '-v', required=True, help='The field valuethat acts as a filter')
parser.add_argument('--lookback', '-l', required=True, help='Time window to look from now')
parser.add_argument('--timeout', '-t', required=True, help='The timeout time of the query')
parser.add_argument('--aggfield', '-a', required=True, help='The field to aggregate on')
parser.add_argument('--display', '-di',  nargs='*', help='Accepts the number of fields to output per result', required=True)
parser.add_argument('--threshold', '-th', required=False, help='Only display bucket values with count greater than the give threshold')
parser.add_argument('--elasticip', '-eip', required=True, help='The IP Address of the elasticsearch instance')
parser.add_argument('--elasticport', '-epo', required=False, default='9200', help='The port of the elasticsearch instance')
parser.add_argument('--donotshow', '-o', action='store_true')
parser.add_argument('--justbuckets', '-j', action='store_true')

parser.set_defaults(debug=False)
args = parser.parse_args()
re_split = re.split('([0-9.]+)([a-zA-Z]+)', args.lookback)

if re_split[2] == "m":
    args.lookback = str(int(re_split[1]) + 1) + "m"

if args.fieldname is None or args.fieldvalue is None:
    fieldname = "None"
    fieldvalue = "None"
else:
    fieldname = args.fieldname
    fieldvalue = args.fieldvalue

if not args.threshold:
    args.threshold = 0

lookback = "now-" + args.lookback
query = {
    "sort":{
        "@timestamp":{
            "order":"desc"
        }
    },
    "query":{
        "filtered":{
            "query":{
                "bool":{
                    "must":[{"query_string":{"query": fieldname + ":" + fieldvalue}}]
                }
            },
            "filter":{
                "bool":{
                    "must":[{ "range":{"@timestamp":{"from": lookback ,"to":"now"}} }]
                }
            },
            "strategy":"leap_frog_filter_first"
        }
    }
}
body = {
    "size": 0,
    "aggregations":{
        "host_agg":{
            "terms":{
                "field": args.aggfield + ".raw",
                "size":0
            }
        }
    }
}
body["query"] = query["query"]


if args.timeout is None:
    timeout = None
else:
    timeout = float(args.timeout)

es = Elasticsearch([args.elasticip + ':' + args.elasticport], timeout=timeout)
res = es.search(index="logstash-*", doc_type=args.doctype, body=body)

if res['hits']['total'] > 0:
    buckets = []
    for bucket in res['aggregations']['host_agg']['buckets']:
        if bucket['doc_count'] >= int(args.threshold):
            buckets.append(bucket['key'])
    
    #Set query size to 1 to return only the most recent hit
    query["size"] = 1

    if args.justbuckets:
        for bucket in buckets:
            print bucket
    else:
        COUNT = False
        #Now iterate through the buckets and print out the newest document
        for val in buckets:
            #Reset the query to find only specific value of the buckets
            query["query"]["filtered"]["query"]["bool"]["must"] = [{"query_string":{"query": fieldname + ":\"" + fieldvalue + "\" AND " + args.aggfield + ":\"" + val + "\""}}]
            results = es.search(index="logstash-*", doc_type=args.doctype, body=query)  
            
            if not COUNT:
                print(val)
            else:
                print(args.aggfield + ": " + val)

            for field in args.display:
                try:
                    print("    " + field + ": " + str(results['hits']['hits'][0]['_source'][field]))
                except:
                    print("    " + field + ": Invalid field name")
            print("")
            COUNT = True
        sys.exit(2)
else:
    if not args.donotshow:
        print("OK: 0 log messages found containing \"%s\" in past %s" % ( args.fieldvalue, args.lookback))

sys.exit(0)
