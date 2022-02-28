from django.test import TestCase

# Create your tests here.

import json
import requests

def article_post():
    url = 'http://127.0.0.1:8000/api/article'
    data = {
        'title': 'test_title1',
        'text': 'test_text1',
        'categories': json.dumps([{'name': 'blog', 'slug': 'blog'}]),
        'tags': json.dumps([{'name': 'blog', 'slug': 'blog'}])
    }

    result = requests.put(url=url, data=data)
    print(result.text)

# 归并排序

# 合并两个有序数组
def merge(left_array,right_array):
    result = []

    while left_array and right_array:
        if left_array[0] <= right_array[0]:
            result.append(left_array.pop(0))
        else:
            result.append(right_array.pop(0))

    while left_array:
        result.append(left_array.pop(0))

    while right_array:
        result.append(right_array.pop(0))
    print(f"result=={result}")
    return  result

def merge_sort(array):

    if len(array) < 2:
        return array

    middle = len(array) // 2

    left_array = array[:middle]
    right_array = array[middle:]
    print(f"leftArr=={left_array} rightArr=={right_array}")
    return merge(merge_sort(left_array), merge_sort(right_array))


if __name__ == "__main__":
    import random

    array = [random.randint(0, 100) for i in range(20)]
    result = merge_sort(array)
    print(result)