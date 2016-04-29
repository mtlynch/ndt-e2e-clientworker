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
import contextlib
import os

import banjo_driver
import fake_mlabns
import filename
import html5_driver
import http_server
import names
import result_encoder
import os_metadata


def main(args):
    if args.client == names.BANJO:
        fake_mlabns_server = fake_mlabns.FakeMLabNsServer(args.server)
        print 'starting fake mlab-ns server on port %d' % (
            fake_mlabns_server.port)
        with contextlib.closing(http_server.ReplayHTTPServer(
                args.replay_port, fake_mlabns_server, args.client_path)):
            print 'replay server replaying %s on port %d' % (args.client_path,
                                                             args.replay_port)
            url = 'http://localhost:%d/' % args.replay_port
            driver = banjo_driver.BanjoDriver(args.browser, url)
            _run_test_iterations(driver, args.iterations, args.output)
    if args.client == names.NDT_HTML5:
        driver = html5_driver.NdtHtml5SeleniumDriver(args.browser,
                                                     args.client_url,
                                                     timeout=20)
        _run_test_iterations(driver, args.iterations, args.output)
    else:
        raise ValueError('unsupported NDT client: %s' % args.client)


def _run_test_iterations(driver, iterations, output_dir):
    """Use the given client driver to run the specified number of iterations.

    Given an NDT client driver, run NDT tests for the given number of
    iterations. On completion of each test, save the result to disk and print
    the result to the console.

    Args:
        driver: An NDT client driver that supports the perform_test API.
        iterations: The total number of test iterations to run.
        output_dir: Directory in which to result file.
    """
    for i in range(iterations):
        print 'starting iteration %d...' % (i + 1)
        result = driver.perform_test()
        result.os, result.os_version = os_metadata.get_os_metadata()
        print _jsonify_result(result)
        _save_result(result, output_dir)


def _save_result(result, output_dir):
    """Saves an NdtResult instance to a file in output_dir.

    Serializes an NdtResult to JSON format, automatically generates a
    filename based on the NdtResult metadata, then saves it to output_dir.

    Args:
        result: NdtResult instance to save.
        output_dir: Directory in which to result file.
    """
    output_filename = filename.create_result_filename(result)
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w') as output_file:
        output_file.write(_jsonify_result(result))


def _jsonify_result(result):
    return result_encoder.NdtResultEncoder(indent=2,
                                           sort_keys=True).encode(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='NDT E2E Testing Client Wrapper',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--client',
                        help='NDT client implementation to run',
                        choices=(names.NDT_HTML5, names.BANJO),
                        required=True)
    parser.add_argument('--browser',
                        help='Browser to run under (for browser-based client)',
                        choices=('chrome', 'firefox', 'safari', 'edge'))
    parser.add_argument('--client_path',
                        help=('Path to client files. Depending on the type of '
                              'client, these can be replay files, static HTML '
                              'files (not implemented), or a client binary '
                              '(not implemented)'))
    parser.add_argument('--client_url',
                        help='URL of NDT client (for server-hosted clients)')
    parser.add_argument('--server', help='FQDN of NDT server to test against')
    parser.add_argument('--replay_port',
                        help='Port to listen on for replay server',
                        default=8888)
    parser.add_argument('--output', help='Directory in which to write output')
    parser.add_argument('--iterations',
                        help='Number of iterations to run',
                        type=int,
                        default=1)
    main(parser.parse_args())
