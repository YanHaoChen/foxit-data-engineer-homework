# Question 1

### Answer

#### 使用 Airflow + MongoDB 的架構

1. 透過 `for_setup_airflow/docker-compose` 建起環境。建立方式同[環境安裝](https://github.com/YanHaoChen/tw-financial-report-analysis#%E7%92%B0%E5%A2%83%E5%AE%89%E8%A3%9D)
2. 設定 mongo 使用者
```
docker exec -it foxit-airflow_mongo_1 bash
use dcard
db.createUser(
	{
		user:"dcarder",
		pwd: "homework",
		roles:[
			{ role: "readWrite", db: "dcard" }
		]
	}
)
```
3. 其餘與[建立 Mongo Connection](https://github.com/YanHaoChen/tw-financial-report-analysis#%E5%BB%BA%E7%AB%8B-mongo-connection), [把檔案導入 dags](https://github.com/YanHaoChen/tw-financial-report-analysis#%E5%88%9D%E5%A7%8B%E5%8C%96%E5%B0%88%E6%A1%88), [初始化專案](https://github.com/YanHaoChen/tw-financial-report-analysis#%E5%88%9D%E5%A7%8B%E5%8C%96%E5%B0%88%E6%A1%88) 類同。

#### Dag
```
check_post_exist_task - no data in mongo (insert)  >> crawl_forum_task  >> done_task
                                                                        >> has_error_task
                      - has data in mongo (update) >> update_posts_task >> update_done_task
                                                                        >> update_has_error_task
```

#### update date

透過 catchup 方式。
```
./airflow.sh tasks clear -s 2021-09-27 -e 2021-09-28 -d crawl_dcard_apple_dag
```


#### data in mongo

```json
[
  {
    _id: ObjectId("6151ff6855316d26ceb40e9d"),
    postID: 237077503,
    title: '#Mac Macbook 觸控板手勢問題',
    createdAt: '2021-09-26T11:45:29.158Z',
    mediaMeta: [
      {
        id: '718724b2-cc72-4686-ac1a-ff6b4ababdfe',
        url: 'https://i.imgur.com/EzMrd31l.jpg',
        normalizedUrl: 'https://i.imgur.com/EzMrd31l.jpg',
        thumbnail: 'https://i.imgur.com/EzMrd31l.jpg',
        type: 'image/thumbnail',
        tags: [ 'ANNOTATED' ],
        createdAt: '2021-09-26T11:45:29.158Z',
        updatedAt: '2021-09-26T11:46:00.213Z',
        width: 2000,
        height: 2000
      },
      {
        id: '718724b2-cc72-4686-ac1a-ff6b4ababdfe',
        url: 'https://i.imgur.com/EzMrd31.jpg',
        normalizedUrl: 'https://imgur.com/EzMrd31',
        thumbnail: 'https://i.imgur.com/EzMrd31l.jpg',
        type: 'image/imgur',
        tags: [ 'ANNOTATED' ],
        createdAt: '2021-09-26T11:45:29.158Z',
        updatedAt: '2021-09-26T11:46:00.213Z',
        width: 2000,
        height: 2000
      },
      {
        id: '00074f73-0cba-4a96-a339-34f592b44e8d',
        url: 'https://i.imgur.com/TjLOgh1.jpg',
        normalizedUrl: 'https://imgur.com/TjLOgh1',
        thumbnail: 'https://i.imgur.com/TjLOgh1l.jpg',
        type: 'image/imgur',
        tags: [ 'ANNOTATED' ],
        createdAt: '2021-09-26T11:45:29.158Z',
        updatedAt: '2021-09-26T11:46:00.213Z',
        width: 1500,
        height: 2000
      },
      {
        id: '0977b80a-c7e0-44f0-be1f-cf56f85f8b5a',
        url: 'https://www.dcard.tw/v2/vivid/videos/a410938f-8cde-4a7a-8ef8-4f9d39e27b38?r=1.7777777777777777',
        normalizedUrl: '',
        thumbnail: 'https://vivid.dcard.tw/Public/a410938f-8cde-4a7a-8ef8-4f9d39e27b38/thumbnail.jpg',
        type: 'video/vivid',
        tags: [ 'ANNOTATED_FAILED' ],
        createdAt: '2021-09-26T11:45:29.158Z',
        updatedAt: '2021-09-26T11:46:00.213Z'
      }
    ],
    categories: [ 'Mac' ],
    content: '最近因為bts方案 購入了一台MacBook air\n' +
      '因為之前不是用蘋果的 所以還在慢慢上手🥲\n' +
      '有先看了影片學幾個基本的手勢 遇到了兩個問題\n' +
      '也上網找過答案 但是都沒辦法\n' +
      '在想是不是哪裡有問題😭😭 可是其他的手勢都正常能使用 有人能教教我嗎\n' +
      '\n' +
      '1.查詢單字\n' +
      '已經有先選擇一直用力長按 也有嘗試三指輕按\n' +
      '我有看旁邊的教學 但是都沒辦法啊啊啊🥲\n' +
      'https://i.imgur.com/EzMrd31.jpg\n' +
      'https://i.imgur.com/TjLOgh1.jpg\n' +
      '2.三指換頁面（不確定名字是不是這樣😅\n' +
      '因為之前看朋友用三指就能換很多頁面 那時候覺得很酷 可是自己怎麼用都沒辦法\n' +
      '\n' +
      '（我有先開了三個頁面）\n' +
      'https://www.dcard.tw/v2/vivid/videos/a410938f-8cde-4a7a-8ef8-4f9d39e27b38?r=1.7777777777777777',
    topics: [ '請益' ]
  },
]
```

### Note
 * 詳細安裝方式，待補充。