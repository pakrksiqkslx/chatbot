"""
Excel 파일 읽기 유틸리티 - pandas + calamine 사용
"""
import json
import math
from pathlib import Path
import pandas as pd
from typing import Any, Optional, List, Dict


class ExcelReader:
    """Excel 파일 읽기 클래스 (calamine 엔진 사용)"""
    
    def __init__(self, file_path: str):
        """
        Args:
            file_path: Excel 파일 경로
        """
        self.file_path = file_path
        self._cache = {}  # 시트 캐시
    
    def _load_sheet(self, sheet_name: Any = 0) -> pd.DataFrame:
        """시트 로드 (캐시 사용)"""
        if sheet_name not in self._cache:
            self._cache[sheet_name] = pd.read_excel(
                self.file_path, 
                sheet_name=sheet_name, 
                engine='calamine', 
                header=None
            )
        return self._cache[sheet_name]
    
    def get_cell(self, sheet_name: Any = 0, row: int = 0, col: int = 0) -> Any:
        """
        특정 셀 값 읽기
        
        Args:
            sheet_name: 시트 이름 또는 인덱스 (기본값: 0 = 첫 번째 시트)
            row: 행 번호 (0부터 시작)
            col: 열 번호 (0부터 시작)
        
        Returns:
            셀 값 (범위를 벗어나면 None 반환)
        
        Example:
            reader = ExcelReader('data.xlsx')
            value = reader.get_cell('Sheet1', 0, 0)  # A1 셀
        """
        df = self._load_sheet(sheet_name)
        try:
            return df.iloc[row, col]
        except IndexError:
            return None
    
    def get_range(self, sheet_name: Any = 0, 
                  start_row: int = 0, start_col: int = 0,
                  end_row: Optional[int] = None, end_col: Optional[int] = None) -> List[List[Any]]:
        """
        셀 범위 읽기
        
        Args:
            sheet_name: 시트 이름 또는 인덱스
            start_row: 시작 행 (0부터)
            start_col: 시작 열 (0부터)
            end_row: 끝 행 (None이면 마지막까지)
            end_col: 끝 열 (None이면 마지막까지)
        
        Returns:
            2차원 리스트
        
        Example:
            reader = ExcelReader('data.xlsx')
            data = reader.get_range('Sheet1', 0, 0, 4, 2)  # A1:C5
        """
        df = self._load_sheet(sheet_name)
        
        if end_row is None:
            end_row = len(df) - 1
        if end_col is None:
            end_col = len(df.columns) - 1
        
        return df.iloc[start_row:end_row+1, start_col:end_col+1].values.tolist()
    
    def get_column(self, sheet_name: Any = 0, col: int = 0, 
                   skip_header: bool = True) -> List[Any]:
        """
        특정 열 전체 읽기
        
        Args:
            sheet_name: 시트 이름 또는 인덱스
            col: 열 번호 (0부터)
            skip_header: 첫 행 건너뛰기
        
        Returns:
            열 데이터 리스트
        
        Example:
            reader = ExcelReader('data.xlsx')
            column_data = reader.get_column('Sheet1', 0, skip_header=True)
        """
        df = self._load_sheet(sheet_name)
        start_row = 1 if skip_header else 0
        return df.iloc[start_row:, col].dropna().tolist()
    
    def get_row(self, sheet_name: Any = 0, row: int = 0) -> List[Any]:
        """
        특정 행 전체 읽기
        
        Args:
            sheet_name: 시트 이름 또는 인덱스
            row: 행 번호 (0부터)
        
        Returns:
            행 데이터 리스트
        
        Example:
            reader = ExcelReader('data.xlsx')
            row_data = reader.get_row('Sheet1', 0)
        """
        df = self._load_sheet(sheet_name)
        return df.iloc[row].tolist()
    
    def get_sheet_names(self) -> List[str]:
        """
        모든 시트 이름 목록 가져오기
        
        Returns:
            시트 이름 리스트
        """
        excel_file = pd.ExcelFile(self.file_path, engine='calamine')
        return excel_file.sheet_names
    
    def to_json(self, output_file: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Excel 파일을 JSON으로 변환
        
        Args:
            output_file: JSON 출력 파일 경로 (선택)
        
        Returns:
            딕셔너리 (시트별 데이터)
        
        Example:
            reader = ExcelReader('data.xlsx')
            result = reader.to_json('output.json')
        """
        excel_data = pd.read_excel(self.file_path, sheet_name=None, engine='calamine')
        
        result = {}
        for sheet_name, df in excel_data.items():
            df_cleaned = df.where(pd.notna(df), None)
            result[sheet_name] = df_cleaned.to_dict('records')
        
        if output_file:
            def convert_to_json(obj):
                if isinstance(obj, float) and math.isnan(obj):
                    return None
                return str(obj)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=convert_to_json)
            print(f"💾 JSON 저장: {output_file}")
        
        return result
    
    def __enter__(self):
        """Context manager 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self._cache.clear()


# 편의 함수들 (하위 호환성)
def read_excel_cell(file_path: str, sheet_name: Any = 0, row: int = 0, col: int = 0) -> Any:
    """특정 셀 읽기 (편의 함수)"""
    reader = ExcelReader(file_path)
    return reader.get_cell(sheet_name, row, col)


def read_excel_range(file_path: str, sheet_name: Any = 0, 
                     start_row: int = 0, start_col: int = 0,
                     end_row: Optional[int] = None, end_col: Optional[int] = None) -> List[List[Any]]:
    """셀 범위 읽기 (편의 함수)"""
    reader = ExcelReader(file_path)
    return reader.get_range(sheet_name, start_row, start_col, end_row, end_col)


def read_excel_column(file_path: str, sheet_name: Any = 0, col: int = 0, 
                      skip_header: bool = True) -> List[Any]:
    """특정 열 읽기 (편의 함수)"""
    reader = ExcelReader(file_path)
    return reader.get_column(sheet_name, col, skip_header)


def read_excel_row(file_path: str, sheet_name: Any = 0, row: int = 0) -> List[Any]:
    """특정 행 읽기 (편의 함수)"""
    reader = ExcelReader(file_path)
    return reader.get_row(sheet_name, row)


def read_excel_to_json(file_path: str, output_file: Optional[str] = None) -> Dict[str, List[Dict]]:
    """JSON 변환 (편의 함수)"""
    reader = ExcelReader(file_path)
    return reader.to_json(output_file)


# ===== 수업계획서 파싱 함수들 =====

def parse_class_info(reader: ExcelReader, page: str) -> tuple[Dict, str]:
    """Page 1: 교과목 운영 정보 파싱"""
    class_info_mapping = {
        '담당교수': (3, 4),    
        '교과목': (3, 11),     
        '이수구분': (3, 16),   
        '시간/학점': (4, 4),   
        '이론/실습': (4, 11),   
        '연락처': (5, 4),       
        'E-Mail': (5, 11)      
    }
    
    class_info_dict = {}
    for key, (row, col) in class_info_mapping.items():
        value = reader.get_cell(page, row, col)
        class_info_dict[key] = value
    
    subject_name = class_info_dict.get('교과목', '교과목')
    return {'교과목 운영': class_info_dict}, subject_name


def parse_competency(reader: ExcelReader, page: str) -> Dict:
    """Page 1: 교과목 역량 정보 파싱"""
    # 기본 역량 정보
    competency_dict = {
        '역량시수(시간)': reader.get_cell(page, 7, 2),
        '역량갯수': reader.get_cell(page, 7, 9)
    }
    
    # 테이블 헤더
    column_index = [1, 5, 8, 10, 13, 15, 17]
    headers = [reader.get_cell(page, 8, col) for col in column_index]
    
    # 데이터 추출 (9행부터 시작)
    current_index = 9
    i = 1
    
    while True:
        cell_value = reader.get_cell(page, current_index, 0)
        if not cell_value or "◎교과목 개요" in str(cell_value):
            break
        
        row_data = [reader.get_cell(page, current_index, col) for col in column_index]
        record = {headers[j]: row_data[j] for j in range(len(headers))}
        competency_dict[str(i)] = record
        
        current_index += 1
        i += 1
    
    return {'교과목 역량': competency_dict}, current_index + 1


def parse_outline_page1(reader: ExcelReader, page: str, start_index: int) -> Dict:
    """Page 1: 교과목 개요 시작 부분 파싱"""
    outline = {}
    current_index = start_index
    
    while True:
        column = reader.get_cell(page, current_index, 0)
        if column is None or pd.isna(column) or column == "":
            break
        value = reader.get_cell(page, current_index, 3)
        outline[column] = value
        current_index += 1
    
    return outline


def parse_outline_page2(reader: ExcelReader, page: str, outline: Dict) -> Dict:
    """Page 2: 교과목 개요 나머지 부분 파싱"""
    current_index = 0
    
    while True:
        column = reader.get_cell(page, current_index, 0)
        if column == "수업방법":
            break
        value = reader.get_cell(page, current_index, 1)
        outline[column] = value
        current_index += 1
    
    # 출석점수
    outline['출석점수'] = {
        '출석': reader.get_cell(page, 10, 5),
        '역량평가': reader.get_cell(page, 10, 13),
        '전체': reader.get_cell(page, 10, 21)
    }
    outline['더 좋은 수업을 위한 노력'] = reader.get_cell(page, 12, 1)
    
    return {'교과목 개요': outline}


def parse_class_week(reader: ExcelReader, start_page_num: int) -> tuple[Dict, int, str]:
    """Page 3, 4, ...: 주차별 수업계획 파싱 (여러 페이지에 걸칠 수 있음)"""
    page_num = start_page_num
    current_page = f'Page {page_num}'
    current_index = 2
    class_week = {}
    
    while True:
        column = reader.get_cell(current_page, current_index, 0)
        
        # 현재 행이 비어있으면 다음 페이지 확인
        if column is None or pd.isna(column) or column == "":
            page_num += 1
            next_page = f'Page {page_num}'
            
            # 다음 페이지가 존재하는지 안전하게 확인
            try:
                next_column = reader.get_cell(next_page, 0, 0)
                
                if next_column == "프로젝트 수업운영(안)":
                    current_page = next_page
                    break
                elif next_column is not None and not pd.isna(next_column) and next_column != "":
                    # 다음 페이지에 데이터가 있으면 계속
                    current_page = next_page
                    current_index = 2
                    continue
                else:
                    # 다음 페이지가 비어있거나 없으면 종료
                    break
            except Exception:
                # 페이지가 존재하지 않으면 종료
                break
        
        # 주차 데이터 읽기
        class_week[column] = {
            '수업주제 및 내용': reader.get_cell(current_page, current_index, 1),
            '수업방법': reader.get_cell(current_page, current_index, 2),
            '학생성장(역량제고) 전략': reader.get_cell(current_page, current_index, 3)
        }
        current_index += 1
    
    project_plan = reader.get_cell(current_page, 1, 0)
    return {'수업계획': class_week, '프로젝트 수업운영(안)': project_plan}, page_num + 1, current_page


def parse_evaluation_info(reader: ExcelReader, page: str, outline: Dict) -> Dict:
    """평가개요, 평가차수, 평가차수별세부평가요약 파싱"""
    try:
        first_cell = reader.get_cell(page, 0, 0)
    except Exception:
        # 페이지가 존재하지 않으면 그대로 반환
        return outline
    
    if not first_cell or "평가개요" not in str(first_cell):
        return outline
    
    # 평가개요 읽기
    evaluation_info = {}
    current_index = 2
    
    while True:
        column = reader.get_cell(page, current_index, 0)
        if column is None or pd.isna(column) or column == "" or column == "◎평가차수":
            break
        
        evaluation_info[column] = {
            '평가내용': reader.get_cell(page, current_index, 2)
        }
        current_index += 1
    
    outline['평가개요'] = evaluation_info
    
    # 평가차수 읽기
    evaluation_degree = {}
    current_index = 8
    
    while True:
        column = reader.get_cell(page, current_index, 0)
        if column is None or pd.isna(column) or column == "" or column == "◎평가차수별세부평가요약":
            break
        
        evaluation_degree[column] = {
            '하위역량': reader.get_cell(page, current_index, 1),
            '구성요인': reader.get_cell(page, current_index, 4),
            '역량시수': reader.get_cell(page, current_index, 6),
            '반영비율': reader.get_cell(page, current_index, 8),
            '평가횟수': reader.get_cell(page, current_index, 10)
        }
        current_index += 1
    
    outline['평가차수'] = evaluation_degree
    
    # 평가차수별세부평가요약 읽기
    evaluation_detail = {}
    current_index = 12
    
    while True:
        column = reader.get_cell(page, current_index, 0)
        if column is None or pd.isna(column) or column == "":
            break
        
        evaluation_detail[column] = {
            '평가차수': reader.get_cell(page, current_index, 0),
            '평가목적': reader.get_cell(page, current_index, 3),
            '평가시기': reader.get_cell(page, current_index, 5),
            '평가방법': reader.get_cell(page, current_index, 7),
            '평가주체': reader.get_cell(page, current_index, 9)
        }
        current_index += 1
    
    outline['평가차수별세부평가요약'] = evaluation_detail
    
    return outline


def parse_syllabus(file_path: str) -> Dict:
    """수업계획서 전체 파싱"""
    with ExcelReader(str(file_path)) as reader:
        # Page 1: 교과목 운영
        class_info, subject_name = parse_class_info(reader, 'Page 1')
        
        # Page 1: 교과목 역량
        competency, outline_start_index = parse_competency(reader, 'Page 1')
        
        # Page 1: 교과목 개요 시작
        outline = parse_outline_page1(reader, 'Page 1', outline_start_index)
        
        # Page 2: 교과목 개요 나머지
        class_outline = parse_outline_page2(reader, 'Page 2', outline)
        
        # Page 3, 4, ...: 수업계획
        week_data, next_page_num, last_page = parse_class_week(reader, 3)
        class_outline.update(week_data)
        
        # 평가 정보
        class_outline = parse_evaluation_info(reader, f'Page {next_page_num}', class_outline)
        
        # 결과 통합
        result = {}
        result.update(class_info)
        result.update(competency)
        result.update(class_outline)
        
        return {subject_name: result, "status": "success"}


def convert_to_json(obj):
    """NaN 값을 None으로 변환"""
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if pd.isna(obj):
        return None
    return obj


if __name__ == "__main__":
    # 현재 스크립트 위치 찾기
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    data_dir = project_root / "data"
    
    # Excel 파일 찾기
    excel_files = list(data_dir.glob("*.xlsx"))
    
    if not excel_files:
        result = {"error": "xlsx 파일을 찾을 수 없습니다."}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"총 {len(excel_files)}개의 파일을 처리합니다...")
        
        all_results = {}
        success_count = 0
        error_count = 0
        errors = []
        
        for idx, excel_file in enumerate(excel_files, 1):
            try:
                print(f"[{idx}/{len(excel_files)}] {excel_file.name} 처리 중...")
                
                # 수업계획서 파싱
                result = parse_syllabus(excel_file)
                
                # status를 제외한 교과목 데이터 병합
                for key, value in result.items():
                    if key != "status":
                        all_results[key] = value
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                error_info = {
                    "file": excel_file.name,
                    "error_message": str(e),
                    "error_type": type(e).__name__
                }
                errors.append(error_info)
                print(f"  ✗ 에러 발생: {str(e)}")
        
        # 최종 결과에 상태 정보 추가
        all_results["_metadata"] = {
            "total_files": len(excel_files),
            "success": success_count,
            "errors": error_count,
            "error_details": errors if errors else None
        }
        
        # utils 디렉토리에 저장
        output_path = script_dir / "output.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2, default=convert_to_json)
        
        print(f"\n=== 처리 완료 ===")
        print(f"성공: {success_count}개")
        print(f"실패: {error_count}개")
        print(f"결과 저장: {output_path}")