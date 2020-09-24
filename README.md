# SPA
Smart-procedure AI 저장소 입니다.

## 개발 및 테스트를 위한 SPA software 설치 방법

### docker 설치
- 리눅스는 아래 설명에 따라 설치. 윈도우나 MacOS 는 패키지를 설치
```shell script
# 패키지 관리 도구 업데이트
$ sudo apt update
$ sudo apt-get update

# 기존 docker 설치된 리소스 확인 후 발견되면 삭제
$ sudo apt-get remove docker docker-engine docker.io

# docker를 설치하기 위한 각종 라이브러리 설치
$ sudo apt-get install apt-transport-https ca-certificates curl software-properties-common -y

# curl 명령어를 통해 gpg key 내려받기
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# 키를 잘 내려받았는지 확인
$ sudo apt-key fingerprint 0EBFCD88

# 패키지 관리 도구에 도커 다운로드 링크 추가
$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# 패키지 관리 도구 업데이트
$ sudo apt-get update

# docker-ce 설치 
$ sudo apt-get install docker-ce docker-ce-cli containerd.io

# Docker 설치 완료 후 테스트로 hello-world 컨테이너 구동
$ sudo docker run hello-world
```

### AI 서버 실행
- spa/models 폴더에 모델 폴더들(ex. /guide_1, /guide_2)과 모델 설정 파일(models.config)이 존재해야 함
```shell script
$ ./bin/spa_server.sh
```

### AI 서버에서 예측 값 얻기
#### curl 
[ 실행 ]
```shell script
[ 가이드 1 의 예측값 얻기 ]
curl -d '{"instances": [[1,1,1,1,0,0,1,0]]}' /
 -X POST http://localhost:8501/v1/models/guide_1:predict

[ 가이드 2 의 예측값 얻기 ]
curl -d '{"instances": [[1,1,1,1,0,0,1,0]]}' /
 -X POST http://localhost:8501/v1/models/guide_2:predict
```

[ 결과 값 ]
```json
{"predictions": [[0.0067783]]}
```

#### 파이썬
[ 실행 ]
```python
import json
import requests

print("send a request")
data = {"instances": [[1,1,1,1,0,0,1,0,0,1,1,1,0,1,1,1,0,1,0,1,1,0,0,1,1,0,1,1]]}
url = "http://{ip}:{port}/v1/models/{guide}:predict".format(**{'ip': '34.69.98.244', 'port': 8501, 'guide': 'guide_1'})
r = requests.post(url, data=json.dumps(data))
result = r.json()

prediction = result['predictions'][0][0] * 100
print('prediction: {result}'.format(result=prediction))
```
