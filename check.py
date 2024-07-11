import requests


base_url = "https://showfast.sc.couchbase.com/api/v1/timeline/"
metric = "ycsb_trans_workloadtca_1s1c_4nodes_48cores_dur_maj_hercules_kv"

url = base_url + metric

response = requests.get(url, verify=False)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}")
    print(response.text)



def get_value(input_version, data):
    for version, value in data:
        if version == input_version:
            return value
    return None

input_version = '7.6.2-3694'


showfast_result = get_value(input_version, data)

if showfast_result is not None:
    print(f"The corresponding value for {input_version} is {showfast_result}")
else:
    print(f"{input_version} not found in the data")

