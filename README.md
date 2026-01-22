# 실행 방법

1. Poetry 설치
- Poetry가 설치되어 있지 않다면 공식 문서를 참고하여 설치합니다.

2. 의존성 설치
프로젝트 루트에서 다음 명령어 실행
- poetry install

3. **프로그램 실행**
poetry run python -m ppt_parser.main

4. 다른 파일로 테스트하기
main.py 파일에서 아래 항목을 수정하여 테스트할 수 있습니다.
- BASE_DIR
- sample_file (테스트할 PPT 파일 이름)