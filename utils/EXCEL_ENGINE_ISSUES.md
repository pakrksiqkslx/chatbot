# Excel 엔진 호환성 문제 해결 가이드

## 📋 발생한 문제

### 1. openpyxl 엔진 문제
**증상:**
```
TypeError: __init__() got an unexpected keyword argument 'applyNumberForm'
```

**원인:**
- openpyxl 3.1.x 버전에서 특정 Excel 파일의 숫자 서식(`applyNumberForm`) 속성을 인식하지 못함
- Excel 2019/2021에서 저장된 파일에 포함된 특수 스타일 속성과의 호환성 문제
- 해당 파일: `2025학년도 2학기 수업계획서.xlsx`

**시도한 해결 방법:**
- ❌ openpyxl 3.1.5 → 실패
- ❌ openpyxl 3.1.2 → 실패  
- ❌ openpyxl 3.0.10 → pandas와 호환성 문제 (pandas는 3.1.0+ 요구)
- ❌ `read_only=True`, `data_only=True` 옵션 → 실패

### 2. xlrd 엔진 문제
**증상:**
- xlsx 파일을 읽을 수 없음

**원인:**
- xlrd는 구버전 Excel 형식(.xls)만 지원
- xlrd 2.0.0부터 xlsx 지원 중단
- .xlsx 파일 읽기 시도 시 오류 발생

**결론:**
- ❌ xlrd는 .xlsx 파일에 사용 불가

## ✅ 해결 방법

### 최종 해결: calamine 엔진 사용

```bash
pip install python-calamine
```

**장점:**
- ✅ openpyxl의 스타일 파싱을 우회
- ✅ 빠른 읽기 성능
- ✅ 복잡한 Excel 서식에 강함
- ✅ .xlsx 및 .xls 모두 지원

**사용 예시:**
```python
import pandas as pd

# calamine 엔진 사용
df = pd.read_excel('파일.xlsx', engine='calamine')

# 모든 시트 읽기
excel_data = pd.read_excel('파일.xlsx', sheet_name=None, engine='calamine')
```

## 📊 엔진 비교표

| 엔진 | .xls | .xlsx | 스타일 처리 | 속도 | 비고 |
|------|------|-------|------------|------|------|
| **openpyxl** | ❌ | ✅ | 엄격 | 중간 | 복잡한 서식에서 오류 발생 가능 |
| **xlrd** | ✅ | ❌ | - | 빠름 | xlsx 지원 중단 (v2.0+) |
| **calamine** | ✅ | ✅ | 우회 | 빠름 | ✅ **권장** |
| **pyxlsb** | ❌ | ✅ (xlsb) | - | 빠름 | xlsb 전용 |

## 🔧 현재 프로젝트 설정

### requirements.txt
```txt
pandas>=2.0.0
python-calamine>=0.1.7
openpyxl>=3.1.2  # 백업용
```

### 코드 예시 (utils/excel_utils.py)
```python
import pandas as pd
from pathlib import Path

# Excel 읽기 (calamine 엔진)
def read_excel_to_json(file_path):
    excel_data = pd.read_excel(file_path, sheet_name=None, engine='calamine')
    
    result = {}
    for sheet_name, df in excel_data.items():
        # NaN을 None으로 변환
        df_cleaned = df.where(pd.notna(df), None)
        result[sheet_name] = df_cleaned.to_dict('records')
    
    return result
```

## 🚨 다른 프로젝트에서 같은 문제 발생 시

### 방법 1: calamine 사용 (권장)
```bash
pip install python-calamine
```

### 방법 2: Excel 파일 재저장
1. Excel에서 파일 열기
2. "다른 이름으로 저장" 선택
3. Excel 통합 문서(.xlsx) 형식으로 저장
4. 기존 openpyxl 엔진으로 시도

### 방법 3: 엔진 자동 선택
```python
def read_excel_safe(file_path):
    engines = ['calamine', 'openpyxl', 'xlrd']
    
    for engine in engines:
        try:
            return pd.read_excel(file_path, engine=engine)
        except:
            continue
    
    raise Exception("모든 엔진에서 실패")
```

## 📝 참고 사항

### 설치된 버전 확인
```bash
pip show pandas openpyxl python-calamine
```

### 오류 발생 시 디버깅
```python
import pandas as pd

try:
    df = pd.read_excel('파일.xlsx', engine='calamine')
    print("✅ calamine 성공")
except Exception as e:
    print(f"❌ calamine 실패: {e}")
    
    try:
        df = pd.read_excel('파일.xlsx', engine='openpyxl')
        print("✅ openpyxl 성공")
    except Exception as e:
        print(f"❌ openpyxl 실패: {e}")
```

## 🎯 결론

이 프로젝트에서는 **calamine 엔진**을 사용하여 Excel 파일의 복잡한 서식 문제를 해결했습니다.

**핵심 교훈:**
1. openpyxl은 표준 Excel 파일에는 좋지만, 복잡한 서식에는 취약
2. xlrd는 구버전 .xls 파일 전용
3. calamine은 성능과 호환성 면에서 가장 안정적
4. 프로덕션 환경에서는 여러 엔진을 fallback으로 구현하는 것이 좋음

---
*최종 수정: 2025-10-09*
*프로젝트: chatbot*

