# Copyright 2016 Measurement Lab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse

import html5_driver
import names


def main(args):
    if args.client == names.NDT_HTML5:
        driver = html5_driver.NdtHtml5SeleniumDriver(args.browser,
                                                     args.client_url,
                                                     timeout=20)
    else:
        raise ValueError('unsupported NDT client: %s' % args.client)

    for i in range(args.iterations):
        print 'starting iteration %d...' % (i + 1)
        result = driver.perform_test()
        print '\tc2s_throughput: %s Mbps' % result.c2s_throughput
        print '\ts2c_throughput: %s Mbps' % result.s2c_throughput
        if result.errors:
            print '\terrors:'
            for error in result.errors:
                print '\t * %s: %s' % (
                    error.timestamp.strftime('%y-%m-%d %H:%M:%S'),
                    error.message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='NDT E2E Testing Client Wrapper',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--client',
                        help='NDT client implementation to run',
                        choices=(names.NDT_HTML5,),
                        required=True)
    parser.add_argument('--browser',
                        help='Browser to run under (for browser-based client)',
                        choices=('chrome', 'firefox', 'safari', 'edge'))
    parser.add_argument('--client_url',
                        help='URL of NDT client (for server-hosted clients)')
    parser.add_argument('--iterations',
                        help='Number of iterations to run',
                        type=int,
                        default=1)
    main(parser.parse_args())
