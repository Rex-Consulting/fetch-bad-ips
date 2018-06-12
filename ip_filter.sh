#!/bin/sh
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

# $1 - elasticsearch ip
# $2 - elasticsearch port
# $3 - gateway host ip (has to be host that runs this script)

oldIFS=$IFS
IFS=' '

RESULT=`~/rex_agg_field_2.py --doctype 'syslog' --fieldname '((alert' --fieldvalue '"Did not receive identification string") OR (alert:"Timeout before authentication") OR (alert:"Bad protocol version identification") OR (alert:"Invalid user") OR (alert:"maximum authentication attempts") OR (alert:"Too many authentication failures")) AND (host:$3)' --lookback 10m --timeout 60 --aggfield 'ip_address' --display --threshold 3 --justbuckets --donotshow --elasticip $1 --elasticport $2` 

parsed_result=`echo $RESULT | tr "\n" " "`
for ip in $parsed_result
do
    grep -q $ip "~/whitelist" 
    if [ $? -eq 0 ]    
    then 
        continue
    fi
    pfctl -t testblacklist -T add $ip
done

IFS=$oldIFS
