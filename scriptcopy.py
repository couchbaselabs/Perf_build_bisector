from cb_build_bisector import (
    JenkinsInstance,
    TesterResult,
    VersionInfo,
    auto_connect_jenkins,
    bisect,
    get_perfrunner_results,
)
import requests

good=VersionInfo('7.6.2-3694')
bad=VersionInfo('7.6.2-3716')
def get_value(input_version, data):
    for version, value in data:
        if version == input_version:
            return value
    return None


# Connect using credentials from the environment
perf = auto_connect_jenkins(JenkinsInstance.PERF)

def value_check(version: VersionInfo) -> TesterResult:
    """Tests using the perf.jenkins.couchbase.com instance"""

    base_url = "https://showfast.sc.couchbase.com/api/v1/timeline/"
    metric = "ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj_hercules_kv"

    url = base_url + metric

    showfast_response = requests.get(url, verify=False)

    if showfast_response.status_code == 200:
        data = showfast_response.json()
        print(data)
    else:
        print(f"Error: {showfast_response.status_code}")
        print(showfast_response.text)

    good_version = str(good).split('/')[1]
    input_version = str(version).split('/')[1]

    initial_result = get_value(good_version, data)
    showfast_result = get_value(input_version, data)

    if showfast_result is not None:
        value = showfast_result
        print(f"The corresponding value for {input_version} is {showfast_result}")
    else:
        print(f"{input_version} not found in the data")

        build = perf.check_build(job_name='hercules-txn', parameters={
            'test_config': 'transactions/collections/ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj.test',
            'cluster': 'hercules_kv.spec',
            'version': f'{version.version}-{version.build}',
            'override': '',
            'dry_run': 'false',
            'collect_logs': 'false',
            'cherrypick': '',
        })
        if not build.status.is_success():
            return TesterResult.SKIP

        results = get_perfrunner_results(build)
        result = next((r for r in results if r.get('metric', None) ==
                    'ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj_hercules_kv'))

        value = result['value']
    print(value)
    if value > 13000:
        return TesterResult.BAD
    else:
        return TesterResult.GOOD

try:
    regression_version = bisect(
        good,
        bad,
        tester=value_check)
    print(
        f'The first Couchbase Server build which scores < 2M is: {regression_version}')
except Exception as e:
    print(f'Failed: {e}')
    

