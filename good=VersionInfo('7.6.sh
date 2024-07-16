good=VersionInfo('7.6.2-3694')
bad=VersionInfo('7.6.2-3716')
base_url = "m"
metric = "ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj_hercules_kv"
testfile = "transactions/collections/ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj.test"

env/bin/python modified_script.py --good 7.6.2-3694 --bad 7.6.2-3716 --percentage 10 --base_url https://showfast.sc.couchbase.com/api/v1/timeline/ --metric ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj_hercules_kv --testfile transactions/collections/ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj.test
