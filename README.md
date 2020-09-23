# SmartProcedure AI
제품 설치 [리포트](https://docs.google.com/document/d/1kJ9uFPWnUiRx0PrnSZ7YrXkf52QmT1GQxj8zOnvsANc/edit?usp=sharing) 와 설치관련 결과데이터를 분석후, 이를 AI 모델로 개발하여, Report 작성시 발견되는 이상징후를 작업자에게 전달함

## 모델 생성 단계
1. 작업자가 고객사에 제품 설치시, 작성하는 [리포트](https://docs.google.com/document/d/1kJ9uFPWnUiRx0PrnSZ7YrXkf52QmT1GQxj8zOnvsANc/edit?usp=sharing) 를 수집  
2. 고객사 제품에 설치관련 문제 발생시, 해당 Report 에 체크
3. 누적되는 데이터를 이용하여 모델 생성

### 모델 생성 단계 1
1. 작업자가 [리포트](https://docs.google.com/document/d/1kJ9uFPWnUiRx0PrnSZ7YrXkf52QmT1GQxj8zOnvsANc/edit?usp=sharing) 작성
2. 리포트의 체크박스, 라디오버튼 및 텍스트박스(숫자) 에서 데이터를 수집됨
   - 체크박스와 라디오 버튼은 이진수로 텍스트박스 값은 숫자 그대로 복사됨
       * 체크박스 [V] [ ] [ ] [V] ===> 1,0,0,1 로 변환됨
       * 라디오버튼 ( ) (O) ( ) ====> 0,1,0 로 변환됨
       * 텍스트박스 {20} ===> 20 으로 변환됨
   - 아래와 같은 리포트 경우는 "1,0,0,1,0,1,0,20" 라는 데이터가 생성됨
       * 체크박스 [V] [ ] [ ] [V], 라디오버튼 ( ) (O) ( ), 텍스트박스 {20}
  
### 모델 생성 단계 2         
1. 설치된 제품에 설치 관련 문제 발생시, 해당 제품 설치시 작성한 리포트에 체크함 
    - 예를 들어, 리포트 1번와 관련된 제품에 설치
    
    | report_id | installation_issue |
    | --------- | ------------------ |
    |         1 |                  1 |
    |         2 |                  0 | 
    
### 모델 생성 단계 3
1. 모델을 생성할 가이드의 데이터를 DB 에서 검색하여 준비

    | guide_id |  v1 |  v2 |  v3 |  v4 |  v5 |  v6 |  v7 |  v8 |  r  |
    | -------- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
    | 1        |  1  |  1  |  0  |  1  |  0  |  0  |  1  |  0  |  0  |
    | 1        |  0  |  1  |  1  |  0  |  1  |  1  |  1  |  0  |  0  | 
    | 1        |  0  |  0  |  1  |  1  |  1  |  0  |  1  |  1  |  0  | 
    | 1        |  0  |  1  |  0  |  1  |  1  |  1  |  0  |  0  |  1  | 
    | 1        |  0  |  1  |  1  |  1  |  0  |  1  |  0  |  1  |  0  | 

2. 준비된 데이터를 이용하여 모델 생성
   - 담당자가 Tensorflow 로 개발된 프로그램을 이용하여 모델 생성
   - 모델은 파일 형식으로 저장됨
 
### 모델 생성시, 예외 상황
* 가이드가 변경될 시, 기존에 만든 모델은 사용불가하기 때문에, 새로 모델을 생성해야 함

## 생성된 모델 배치 

### 모델 배치 프로세스
* [tensorflow_model_server 와 Docker 를 통한 서비스](https://www.tensorflow.org/tfx/serving/docker)
1. Docker 설치 후, TensorFlow Serving 설치(docker pull tensorflow/serving) 
2. 모델 폴더에 AI 모델 복사 
    * 가이드 1에 대한 모델인 경우 /models/guide_1/1/ 에 저장 (/1/ 은 버전정보. 강제적으로 폴더 이름에 숫자만 있어야 함)
    * 가이드 2에 대한 모델인 경우 /models/guide_2/1/ 에 저장
3. config 작성
    ``` 
     model_config_list {
      config {
        name: 'guide_1'
        base_path: '/models/guide_1/'
        model_platform: 'tensorflow'
      }
      config {
        name: 'guide_2'
        base_path: '/models/guide_2/'
        model_platform: 'tensorflow'
      }
    }
    ```   
3. 컨테이너 실헹
    * bin 폴더의 run.sh 실
    ```
    cd ..
    docker run -t --rm -p 8501:8501 \
        -v "$(pwd)/models/:/models/" tensorflow/serving \
        --model_config_file=/models/models.config \
        --model_config_file_poll_wait_seconds=60
    ```

#### 폴더구조
    ```
    ai
     L bin
        L run.sh
     L data
     L models
        L guide_1
        L guide_2
     L src   
    ```

## 모델에서 예측 값 얻기
### 옵션 1 REST 방식
[ 예측값 얻기 ]
``` 
[ 가이드 1 의 예측값 얻기 ]
curl -d '{"instances": [[1,1,1,1,0,0,1,0]]}' /
 -X POST http://localhost:8501/v1/models/guide_1:predict

[ 가이드 2 의 예측값 얻기 ]
curl -d '{"instances": [[1,1,1,1,0,0,1,0]]}' /
 -X POST http://localhost:8501/v1/models/guide_2:predict
``` 
[ 결과 값 ]
```
{"predictions": [[0.0067783]]}
```

## 이상증후 표시
### 옵션 1. 작업자가 리포트 작성 후, Save 버튼 클릭 시, 이상 징후 정보 표시
