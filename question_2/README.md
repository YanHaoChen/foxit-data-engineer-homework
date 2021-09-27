# Question 1

### Answer

```sql
SELECT
    Author,
    Title,
    Content
FROM Documnet as doc 
    LEFT JOIN Content as con 
        ON doc.DocumentId = con.DocumentId
```

### Note
 * 兩張 Table 都沒有 `Subtype` 欄位。
 * 如為 `Content.DocumentId` 建 Index，或主鍵改為(`DocumentId,ContentId`)的組合，預期會有更好的效能。