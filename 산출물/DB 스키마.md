# 데이터베이스 스키마

이 문서는 `entities.py`에 정의된 데이터베이스 스키마를 설명합니다.

## 1. `item` - 개별 문제 테이블

개별 문항에 대한 상세 메타데이터를 저장하는 테이블입니다.

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|---|---|---|---|
| `id` | `Integer` | Primary Key | 고유 식별자 |
| `created_time` | `DateTime` | Not Null, Default: `now()` | 레코드 생성 시간 |
| `grade` | `String` | Not Null | 학년 |
| `subject` | `String` | | 과목 |
| `main_chap1` | `String` | | 추천 대단원 1 |
| `mid_chap1` | `String` | | 추천 중단원 1 |
| `small_chap1` | `String` | | 추천 소단원 1 |
| `reason1` | `String` | | 추천 이유 1 |
| `main_chap2` | `String` | | 추천 대단원 2 |
| `mid_chap2` | `String` | | 추천 중단원 2 |
| `small_chap2` | `String` | | 추천 소단원 2 |
| `reason2` | `String` | | 추천 이유 2 |
| `difficulty` | `Enum` | Not Null | 난이도 (상, 중, 하) |
| `difficulty_reason` | `String` | Not Null | 난이도 평가 이유 |
| `item_type` | `Enum` | Not Null | 문제 유형 |
| `points` | `Integer` | | 배점 |
| `intent` | `String` | | 출제의도 |
| `keywords` | `String` | | 핵심 키워드 |
| `content` | `String` | | 문제 원문 텍스트 |

## 2. `exam` - 시험지 테이블

생성된 시험지에 대한 정보를 저장하는 테이블입니다.

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|---|---|---|---|
| `id` | `Integer` | Primary Key | 고유 식별자 |
| `title` | `String` | Not Null | 시험지 제목 |
| `description` | `String` | Not Null | 시험지 설명 |
| `created_time` | `DateTime` | Not Null, Default: `utcnow` | 레코드 생성 시간 |

*참고: `entities.py`의 `Exam.created_time`에 있는 `datetime.utinow`는 `datetime.utcnow`의 오타로 보입니다.*

## 3. `curriculum` - 교육과정 테이블

교육과정의 단원 정보를 계층적으로 저장하는 테이블입니다.

| 컬럼명 | 데이터 타입 | 제약 조건 | 설명 |
|---|---|---|---|
| `id` | `Integer` | Primary Key, Index | 고유 식별자 |
| `grade` | `String` | Not Null | 학년 |
| `subject` | `String` | Not Null | 과목 |
| `main_chap_num` | `Integer` | Not Null, Index | 대단원 번호 |
| `main_chap` | `String` | Not Null, Unique | 대단원 이름 |
| `mid_chap_num` | `Integer` | Nullable | 중단원 번호 |
| `mid_chap` | `String` | Nullable | 중단원 이름 |
| `small_chap_num` | `Integer` | Nullable | 소단원 번호 |
| `small_chap` | `String` | Nullable | 소단원 이름 |
