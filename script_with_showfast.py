from cb_build_bisector import (
    JenkinsInstance,
    TesterResult,
    VersionInfo,
    auto_connect_jenkins,
    bisect,
    get_perfrunner_results,
)
import requests


# Connect using credentials from the environment
perf = auto_connect_jenkins(JenkinsInstance.PERF)

def get_value(input_version, data):
    for version_temp, value in data:
        if version_temp == input_version:
            return value
    return None

def value_check(version: VersionInfo) -> TesterResult:
    """Tests using the perf.jenkins.couchbase.com instance"""
    # base_url = "https://showfast.sc.couchbase.com/api/v1/timeline/"
    # metric = "ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj_hercules_kv"
    # url = base_url + metric
    # response = requests.get(url, verify=False)
    # print(version)
    # if response.status_code == 200:
    #     data = response.json()
    #     print(data)
    # else:
    #     print(f"Error: {response.status_code}")
    #     print(response.text)

    # result = get_value(version, data)
    # input_version = '7.6.2-3694'
    # value = get_value(input_version, data)

    # if value is not None:
    #     print(f"The corresponding value for {input_version} is {value}")
    # else:
    #     print(f"{input_version} not found in the data")

    print("Starting the build for baby version", version)
    build = perf.check_build(job_name='hercules-txn', parameters={
        'test_config': 'transactions/ycsb_trans_latency_workloadt_4nodes_48cores_dur_none.test',
        'cluster': 'hercules_kv.spec',
        'version': f'{version.version}-{version.build}',
        'override': '',
        'dry_run': 'true',
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
        good=VersionInfo('7.6.2-3694'),
        bad=VersionInfo('7.6.2-3716'),
        tester=value_check)
    print(
        f'The first Couchbase Server build which might be responsible for regression is: {regression_version}')
except Exception as e:
    print(f'Failed: {e}')
    

