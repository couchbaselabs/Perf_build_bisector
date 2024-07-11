from cb_build_bisector import (
    JenkinsInstance,
    TesterResult,
    VersionInfo,
    auto_connect_jenkins,
    bisect,
    get_perfrunner_results,
)

# Connect using credentials from the environment
perf = auto_connect_jenkins(JenkinsInstance.PERF)


def value_check(version: VersionInfo) -> TesterResult:
    """Tests using the perf.jenkins.couchbase.com instance"""
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
    if value == 13075:
        return TesterResult.GOOD
    else:
        return TesterResult.BAD

try:
    regression_version = bisect(
        good=VersionInfo('7.6.2-3688'),
        bad=VersionInfo('7.6.2-3710'),
        tester=value_check)
    print(
        f'The first Couchbase Server build which scores < 2M is: {regression_version}')
except Exception as e:
    print(f'Failed: {e}')
    

