# fetch-bad-ips
Queries elasticsearch for potentially malicious IPs

## Arguments

  --help/-h:            show this help message and exit
  
  --doctype/-d:        The doctype, either syslog or eventlog
  
  --fieldname/-f:       The field name to filter out result
  
  --fieldvalue/-v:      The field valuethat acts as a filter
  
  --lookback/-l:        Time window to look from now
  
  --timeout/-t:         The timeout time of the query
  
  --aggfield/-a:        The field to aggregate on
  
  --display/-di [DISPLAY [DISPLAY ...]]:
  
                       Accepts the number of fields to output per result
                       
  --threshold/-th:      Only display bucket values with count greater than the given threshold
  
  --elasticip/-eip:     The IP Address of the elasticsearch instance
  
  --elasticport/-epo:   The port of the elasticsearch instance
  
  --donotshow/-o
  
  --justbuckets/-j

## Examples

> ~/rex_agg_field_2.py --doctype 'syslog' --fieldname '((alert' --fieldvalue '"Did not receive identification string") OR (alert:"Timeout before authentication") OR (alert:"Bad protocol version identification") OR (alert:"Invalid user") OR (alert:"maximum authentication attempts") OR (alert:"Too many authentication failures")) AND (host:$3)' --lookback 10m --timeout 60 --aggfield 'ip_address' --display --threshold 3 --justbuckets --donotshow --elasticip $1 --elasticport $2

127.0.0.1

## Also See

[Blog Post](http://www.rexconsulting.net/making-use-of-nagios-logserver-to-block-malicious-attackers.html)
