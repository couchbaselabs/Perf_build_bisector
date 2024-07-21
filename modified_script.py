from cb_build_bisector import (
    JenkinsInstance,
    TesterResult,
    VersionInfo,
    auto_connect_jenkins,
    bisect,
    get_perfrunner_results,
)
import requests
import argparse

parser = argparse.ArgumentParser(description='Couchbase build bisector script')
parser.add_argument('--good', type=str, help='Good version info (e.g., 7.6.2-3694)')
parser.add_argument('--bad', type=str, help='Bad version info (e.g., 7.6.2-3716)')
parser.add_argument('--percentage', type=int, help='Percentage value for threshold calculation')
parser.add_argument('--base_url', type=str, default='https://showfast.sc.couchbase.com/api/v1/timeline/',
                    help='Base URL for API requests (default: https://showfast.sc.couchbase.com/api/v1/timeline/)')
parser.add_argument('--metric', type=str, default='ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj_hercules_kv',
                    help='Metric to fetch from API')
parser.add_argument('--testfile', type=str, default='transactions/collections/ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj.test',
                    help='Path to test file')
parser.add_argument('--post_on_showfast', type=str, help='Should post to showfast or not')
parser.add_argument('--job_name', type=str, help='jenkins job to run builds')
parser.add_argument('--cluster', type=str, help='Cluster spec file to be used')

args = parser.parse_args()
good = VersionInfo(args.good)
bad = VersionInfo(args.bad)
percentage = args.percentage
base_url = args.base_url
metric = args.metric
testfile = args.testfile
post_on_showfast = args.post_on_showfast
job_name = args.job_name
cluster = args.cluster
url = base_url + metric
print("hello", url)

showfast_response = requests.get(url, verify=False)
if showfast_response.status_code == 200:
    showfast_data = showfast_response.json()
    print(showfast_data)
else:
    print(f"Error: {showfast_response.status_code}")
    print(showfast_response.text)

def get_value(input_version):
    for version, value in showfast_data:
        if version == input_version:
            return value
    return None


# Connect using credentials from the environment
perf = auto_connect_jenkins(JenkinsInstance.PERF)

def get_build_value(version: VersionInfo):
    showfast_result = get_value(str(version).split('/')[1])

    if showfast_result is not None:
        value = showfast_result
        print(f"The corresponding value for {str(version).split('/')[1]} is {showfast_result}")
    else:
        build = perf.check_build(job_name=job_name, parameters={
            'test_config': testfile,
            'cluster': cluster,
            'version': f'{version.version}-{version.build}',
            'override': '',
            'dry_run': post_on_showfast,
            'collect_logs': 'false',
            'cherrypick': '',
        })
        if not build.status.is_success():
            return TesterResult.SKIP
        results = get_perfrunner_results(build)
        result = next((r for r in results if r.get('metric', None) == metric))
        value = result['value']
    return value

good_value = get_build_value(good)
percentage_value = (good_value * percentage)/100



def value_check(version: VersionInfo) -> TesterResult:
    """Tests using the perf.jenkins.couchbase.com instance"""
    value = get_build_value(version)
    print(value)
    diff = abs(value-good_value)

    if diff >= percentage_value:
        return TesterResult.BAD
    else:
        return TesterResult.GOOD

try:
    regression_version = bisect(
        good,
        bad,
        tester=value_check)
    print(
        f'The first Couchbase Server build which might be responsible for regression is: {regression_version}')
except Exception as e:
    print(f'Failed: {e}')