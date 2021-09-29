# Question 2

### Answer

* answer_2.py
```python
import json


def main():
    with open('./raw.json') as f:
        content = json.load(f)
    content_id = content['data']['filename'].rstrip('.html')

    def sort_condition(this_result):
        return this_result['value']['endOffset'] - this_result['value']['startOffset']

    def output_format(raw_result):
        return {
            "label": raw_result["value"]["htmllabels"][0],
            "sentence": raw_result["value"]["text"],
            "contract_id": content_id,
        }

    contracts = content['completions']

    for contract in contracts:
        results = contract['result']
        sorted_results = sorted(results, key=sort_condition)
        print(list(map(output_format, sorted_results)))


if __name__ == '__main__':
    main()
```

### Note
 * `htmllabels` 可能有多個 label，目前只取第一個。