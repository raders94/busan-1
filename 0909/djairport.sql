drop database if exists air_delivery;
create database if not exists air_delivery;
use air_delivery;

-- Q1. 수기로 작성된 물류대장표를 DBMS에 옮겨주세요.
create table draft(
  id int unsigned not null primary key auto_increment,
  sort varchar(4) not null,
  is_rush tinyint unsigned not null,
  export varchar(5) not null,
  import varchar(5) not null,
  airline varchar(10) not null,
  distance tinyint unsigned not null,
  special_rate int unsigned not null,
  freight_charge int unsigned not null,
  reg_date date not null
);


INSERT INTO `draft`
(
    `sort`,
    `is_rush`,
    `export`,
    `import`,
    `airline`,
    `distance`,
    `special_rate`,
    `freight_charge`,
    `reg_date`
)
VALUES
('식품',     0, '중국', '한국', '대한항공', 1, 0,    1500, '2022-02-07'),
('기호품',   0, '한국', '호주', '아시아나', 2, 0,    2500, '2022-02-07'),
('전자제품', 1, '일본', '한국', '닛폰항공', 1, 1000, 1500, '2022-02-07'),
('의약품',   1, '미국', '한국', '델타항공', 4, 1000, 3000, '2022-02-08'),
('식품',     0, '인도', '한국', '고우에어', 3, 0,    2500, '2022-02-08'),
('일반우편', 0, '한국', '캐나다', '대한항공', 4, 0,    3000, '2022-02-08'),
('의류',     1, '한국', '일본', '아시아나', 1, 1000, 1500, '2022-02-10'),
('전자제품', 1, '미국', '한국', '델타항공', 4, 1000, 3000, '2022-02-10'),
('주류',     1, '칠레', '한국', '라탐항공', 4, 1000, 3000, '2022-02-11'),
('주류',     1, '독일', '한국', '대한항공', 4, 1000, 3000, '2022-02-11')
;


-- Q2. DBMS 작성한 테이블의 전체 데이터를 조회합니다.
select *
from draft;

-- Q3. 우리 공항에서 보낸 항공편의 전체 데이터를 보고싶습니다. (항공편 갯수 집계)
select
 export as '보내는곳',
 count(export) as '항공편 수'
from
  draft
group by export
;


-- Q4. 보내는 곳이 한국만 나오게 출력을 조정
select
 export as '보내는곳',
 count(export) as '항공편 수'
from
  draft
group by export
having export = '한국'
;

-- Q5. 미국에서 우리 공항으로 들어오는 물류의 항공편
select
  export as '받는곳',
  count(export) as '항공편수'
from
  draft
group by 
  export 
having 
  export = '미국'
;

-- Q6. 품류(범주형데이터)를 관리할 수 있는 테이블을 하나 만들어주세요
desc draft;

create table sort_table(
  id int unsigned not null primary key auto_increment,
  sort varchar(4) not null,
  is_rush tinyint unsigned not null
);


insert into sort_table
  ( sort, is_rush )
values
  ( '식품', 0 ),
  ( '기호품', 0 ),
  ( '전자제품', 1),
  ( '의약품', 1),
  ( '의류', 0 ),
  ( '주류', 1 ),
  ( '일반우편', 0)
;

-- Q7. 특별 수하물은 o, 아니면 x로 출력
select 
  id as 번호,
  sort as 품류,
  case
  	when is_rush = 0
  	then 'x'
  	else 'o'
  end as 특별수하물
from 
  sort_table
;

update
  draft d
join
  sort_table st
on 
  d.sort = st.sort
set
  d.sort = st.id
;

select * from draft;

alter table draft drop column is_rush;

desc draft;

alter table draft change sort sort_id int not null;
alter table draft modify column sort_id int unsigned not null;
alter table draft add foreign key(sort_id) references sort_table(id);

select
  d.id as 물류대장표_번호,
  st.sort as 품목,
  case
  	when st.is_rush = 0
  	then 'x'
  	else 'o'
  end as 특별수하물여부
from
  draft d
left join
  sort_table st
on d.sort_id = st.id
;


create table distance_charge(
  id int unsigned not null primary key auto_increment,
  distance int not null,
  culture_code varchar(5) not null unique,
  freight_charge int unsigned not null
);

select * from draft;

insert into distance_charge
set 
  culture_code = '아시아',
  distance = 1,
  freight_charge = 1500
;

insert into distance_charge
set 
  culture_code = '오세아니아',
  distance = 2,
  freight_charge = 2000
;

insert into distance_charge
set 
  culture_code = '인도',
  distance = 3,
  freight_charge = 2500
;


insert into distance_charge
set 
  culture_code = '유럽-미주',
  distance = 4,
  freight_charge = 3000
;

create table culture(
  id int unsigned not null primary key auto_increment,
  culture_code varchar(5) not null,
  nation varchar(10) not null
);

insert into culture
  ( culture_code, nation )
values
  ( '아시아', '한국' ),
  ( '아시아', '중국' ),
  ( '아시아', '일본' ),
  ( '오세아니아', '호주' ),
  ( '인도', '인도' ),
  ( '유럽-미주', '칠레' ),
  ( '유럽-미주', '미국' ),
  ( '유럽-미주', '캐나다' )
;

select * from culture;

select
  c.nation as 국가명,
  dc.distance as 거리단위,
  dc.freight_charge as 운임
from
  culture c
left join
  distance_charge dc
on
  c.culture_code = dc.culture_code
;
ALTER TABLE sort_table
ADD COLUMN special_rate INT UNSIGNED NOT NULL DEFAULT 0;

UPDATE sort_table
SET special_rate = 1000
WHERE is_rush = 1;

SELECT
    c.nation AS 도착국가,
    st.sort AS 품류,
    dc.freight_charge AS 기본운임료,
    st.special_rate AS 특별운임료,
    dc.freight_charge + st.special_rate AS 총운임료
FROM culture c
JOIN distance_charge dc
    ON c.culture_code = dc.culture_code
JOIN sort_table st
    ON st.sort = '전자제품'
WHERE c.nation = '칠레';