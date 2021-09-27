# Question 1

### Answer

使用 Airflow + MongoDB 的架構。

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

### Note
 * 詳細安裝方式，待補充。