-- 기존에 a2 데이터베이스가 존재 한다면 삭제
drop database if exists `a_2`;

-- 새 데이터베이스(`a2`) 생성
CREATE DATABASE `a_2`;

-- 새 데이터베이스(`a2`) 선택
use `a_2`;

-- article 테이블 생성(id, created_at, title, body)
CREATE TABLE article(
    id BIGINT,
    created_at TIMESTAMP,
    title VARCHAR(150),
    body TEXT
);

-- article 테이블 조회(*)
SELECT *
FROM article;

-- article 테이블에 data insert (created_at = NOW(), title = '제목', body = '내용')
INSERT into article
 (created_at, title, body)
 VALUES
 (NOW(), '제목', '내용');

-- article 테이블에 data insert (created_at = NOW(), title = '제목', body = '내용')
INSERT into article
 (created_at, title, body)
 VALUES
 (NOW(), '제목', '내용');

-- article 테이블 조회(*)
SELECT *
FROM article;

-- id 데이터는 꼭 필수 이기 때문에 NULL을 허용하지 않게 바꾼다.(alter table, not null)
-- 기존의 NULL값 때문에 경고가 발생한다.
-- 기존의 NULL값이 0으로 변경된다.
UPDATE article
set id = 0;

alter table article MODIFY COLUMN id bigint not null;
SELECT * FROM article;


-- article 테이블 조회(*)
SELECT * FROM article;

desc article

-- 생각해 보니 모든 행(row)의 id 값은 유니크 해야한다.(ADD PRIMARY KEY(id))
-- 오류가 발생한다. 왜냐하면 기존의 데이터 중에서 중복되는게 있기 때문이다
-- id가 0인 것 중에서 1개를 id 1로 바꾼다.
UPDATE article
SET 
  id = 1
WHERE
  id=0
limit 1 ;

-- article 테이블 조회(*)
SELECT * FROM article;

-- id가 0인것을 id 2로 바꾼다.
UPDATE article
SET 
  id = 2
WHERE
  id=0;

 SELECT * FROM article; 
-- 생각해 보니 모든 행(row)의 id 값은 유니크 해야한다.
---- 이제 적용이 잘 된다.
alter table article add PRIMARY KEY(id);
desc article;
-- id 컬럼에 auto_increment 제약조건을 추가한다
---- auto_increment 을 추가하기전에 해당 칼럼은 무조건 key 여야 한다.
ALTER table article modify column id bigint not null AUTO_INCREMENT;

-- article 테이블 구조확인(desc)
desc article;

-- 나머지 칼럼 모두에도 not null을 적용해주세요.
ALTER Table article MODIFY COLUMN created_at TIMESTAMP not NULL;
ALTER Table article MODIFY COLUMN title VARCHAR(150) not null;
ALTER Table article MODIFY COLUMN body text not null;

desc article;

-- id 칼럼에 UNSIGNED 속성을 추가하세요. #음수 할당 안하겠다
ALTER TABLE article MODIFY COLUMN id BIGINT UNSIGNED not NULL AUTO_INCREMENT

-- article 테이블 구조확인(desc)
desc article;

-- 작성자(writer) 칼럼을 title 칼럼 다음에 추가해주세요.
ALTER Table article add COLUMN writer VARCHAR(100) after title;
desc article;   #column 순서영향 속성 순서 자유

-- 작성자(writer) 칼럼의 이름을 nickname 으로 변경해주세요
ALTER Table article change writer nickname VARCHAR(100);
desc article

-- nickname 칼럼의 위치를 body의 다음으로 보내주세요.
ALTER Table article MODIFY COLUMN nickname VARCHAR(100) after body;

-- hit 조회수 칼럼 추가 
ALTER Table article add COLUMN hit int UNSIGNED not null;
select * 
from article;
-- 기존의 비어있는 닉네임 채워넣기(무명)
update article 
set nickname = '무명'

-- article 테이블에 데이터 추가(created_at = NOW(), title = '제목3', body = '내용3', nickname = '홍길순', hit = 10)
insert into article
  (created_at, title, body, nickname, hit)
VALUES
  (Now(), '제목3','내용3','홍길순',10),
  (Now(), '제목4','내용4','홍길동',55),
  (Now(), '제목5','내용5','홍길동',10),
  (Now(), '제목6','내용6','임꺽정',100);
-- article 테이블에 데이터 추가(created_at = NOW(), title = '제목4', body = '내용4', nickname = '홍길동', hit = 55)
-- article 테이블에 데이터 추가(created_at = NOW(), title = '제목5', body = '내용5', nickname = '홍길동', hit = 10)
-- article 테이블에 데이터 추가(created_at = NOW(), title = '제목6', body = '내용6', nickname = '임꺽정', hit = 100)
-- 조회수 가장 많은 게시물 3개 만 보여주세요.
SELECT * from article
order by hit DESC
limit 3;

-- 작성자명이 '홍길'로 시작하는 게시물만 보여주세요.
SELECT * from article
WHERE nickname like '홍길%'

-- 조회수가 10 이상 55 이하 인것만 보여주세요.
SELECT * from article
WHERE hit >= 10 and hit <=55

-- 작성자가 '무명'이 아니고 조회수가 50 이하인 것만 보여주세요.
SELECT * from article
WHERE nickname != '무명' and hit <= 50;

-- 작성자가 '무명' 이거나 조회수가 55 이상인 게시물을 보여주세요.
SELECT * from article
WHERE nickname = '무명' or hit >= 55;