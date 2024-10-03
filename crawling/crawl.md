1. crawling> yes_24_project > yes_24_project > detail.py 에서 코드를 수정한다.
    1. start_requests(self) 부분을 찾는다.
    2. d_path = {기본 정보 데이터들이 있는 폴더 (구글 드라이브에서 다운로드할 것)}
    3. cate_code_list = [수집할 카테고리 코드를 리스트로 입력]
2. 수집 결과를 저장할 폴더를 생성한 후에 save_info(self) 의 save_path 에  입력한다.
3. 커맨드 프롬프트 실행
4. scrapy.cfg 가 있는 yes_24_project 폴더로 이동한다.
5. 커맨드에 scrapy crawl detail 입력