
![image](architecture.png)

#### 1. 관리자가 `Checklist Authoring Tool`를 통해 가이드별 체크리스트를 작성한다.

작성결과를 쿼리로 검색하면 아래와 같다.
```sql
SELECT	ST.id AS step_id, TK.id AS task_id, AC.id AS action_id, TK.type
FROM	(
            SELECT  id
            FROM    guide
            WHERE   id = 28
        )	AS GD
        JOIN step AS ST ON ST.guide_id = GD.id
        JOIN (
            SELECT  id, step_id, type
            FROM    task
            WHERE   is_analytics = True
        ) AS TK ON TK.step_id = ST.id
        JOIN task_action AS AC ON AC.task_id = TK.id
ORDER BY TK.step_id, TK.id, AC.id -- This should not be changed for AI model
;
```
| STEP | TASK | ACTION | TYPE |
|----|-----|-----|---------|
| 67 | 452 | 512 | "RADIO" |
| 71 | 462 | 525 | "CHECK" |
| 71 | 460 | 532 | "RADIO" |
| 71 | 466 | 544 | "CHECK" |
| 71 | 473 | 554 | "RADIO" |
| 71 | 472 | 567 | "RADIO" |
| 70 | 479 | 575 | "RADIO" |
| 70 | 490 | 584 | "RADIO" |
| 68 | 508 | 606 | "RADIO" |

#### 2. AI 관리자가 `Check list AI Model Generator`를 통해 모델을 생성한다.

물론 실제 사용중인 데이터기반으로 모델생성을 해야하지만, 여건상 가상의 데이터를 생성하여 모델을 생성한다.
