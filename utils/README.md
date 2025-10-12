# Excel Utils (Read Only)

Excel 파일 읽기를 위한 유틸리티 모듈입니다.

> ⚠️ **Excel 엔진 호환성 문제가 있나요?** [EXCEL_ENGINE_ISSUES.md](./EXCEL_ENGINE_ISSUES.md) 문서를 참고하세요.

## 설치

```bash
pip install -r requirements.txt
```

**필수 패키지:**
- `pandas>=2.0.0` - 데이터 처리
- `python-calamine>=0.1.7` - Excel 읽기 엔진 (권장)
- `openpyxl>=3.1.2` - 백업 엔진

## 주요 기능

### 📌 특정 셀/범위 읽기
- `read_excel_cell()`: 특정 셀 값 읽기
- `read_excel_range()`: 셀 범위 읽기 (A1:C5 등)
- `read_excel_column()`: 특정 열 전체 읽기
- `read_excel_row()`: 특정 행 전체 읽기

### 📌 JSON 변환
- `read_excel_to_json()`: Excel 파일 전체를 JSON으로 변환

## 사용 예제

### 1. 특정 셀 읽기

```python
from utils import read_excel_cell

# 특정 셀 값 읽기 (시트명, 행번호, 열번호 - 0부터 시작)
value = read_excel_cell('data/file.xlsx', 'Sheet1', 0, 0)  # A1 셀
print(f"A1 셀 값: {value}")

# 시트 인덱스로도 가능
value = read_excel_cell('data/file.xlsx', 0, 2, 4)  # 첫 시트의 3행 5열
print(f"C3 셀 값: {value}")
```

### 2. 셀 범위 읽기

```python
from utils import read_excel_range

# A1:C5 범위 읽기 (시작행, 시작열, 끝행, 끝열 - 0부터 시작)
data = read_excel_range('data/file.xlsx', 'Sheet1', 0, 0, 4, 2)

# 결과: [[A1, B1, C1], [A2, B2, C2], ...]
for i, row in enumerate(data):
    print(f"행 {i+1}: {row}")

# 끝 행/열 생략 시 마지막까지 읽기
data = read_excel_range('data/file.xlsx', 'Sheet1', 0, 0)  # A1부터 끝까지
```

### 3. 특정 열/행 읽기

```python
from utils import read_excel_column, read_excel_row

# 특정 열 전체 읽기 (0부터 시작)
column_data = read_excel_column('data/file.xlsx', 'Sheet1', 0, skip_header=True)
print(f"A열 데이터: {column_data}")

# 특정 행 전체 읽기
row_data = read_excel_row('data/file.xlsx', 'Sheet1', 0)  # 첫 번째 행
print(f"첫 행 데이터: {row_data}")

# 여러 열 조합
names = read_excel_column('data/file.xlsx', 'Sheet1', 0, skip_header=True)
ages = read_excel_column('data/file.xlsx', 'Sheet1', 1, skip_header=True)
for name, age in zip(names, ages):
    print(f"{name}: {age}세")
```

### 4. JSON으로 변환

```python
from utils import read_excel_to_json

# Excel 전체를 JSON으로 변환
result = read_excel_to_json('data/file.xlsx', 'output.json')

# 결과: {'Sheet1': [{...}, {...}], 'Sheet2': [{...}]}
for sheet_name, data in result.items():
    print(f"{sheet_name}: {len(data)}행")
```

## 주요 함수

| 함수 | 설명 | 예시 |
|------|------|------|
| `read_excel_cell(file, sheet, row, col)` | 특정 셀 읽기 | `read_excel_cell('file.xlsx', 'Sheet1', 0, 0)` |
| `read_excel_range(file, sheet, start_row, start_col, end_row, end_col)` | 셀 범위 읽기 | `read_excel_range('file.xlsx', 0, 0, 0, 4, 2)` |
| `read_excel_column(file, sheet, col, skip_header)` | 특정 열 읽기 | `read_excel_column('file.xlsx', 0, 0, True)` |
| `read_excel_row(file, sheet, row)` | 특정 행 읽기 | `read_excel_row('file.xlsx', 0, 0)` |
| `read_excel_to_json(file, output_file)` | JSON 변환 | `read_excel_to_json('file.xlsx', 'out.json')` |

## 특징

- ✅ **calamine 엔진**: openpyxl 호환성 문제 해결
- ✅ **빠른 성능**: 읽기 전용으로 최적화
- ✅ **간단한 API**: 함수 하나로 셀/범위/행/열 읽기
- ✅ **JSON 변환**: Excel → JSON 자동 변환
- ✅ **타입 안전**: NaN 값 자동 처리
- ✅ **0-based 인덱스**: Python 표준 방식 사용

## 라이센스

MIT

