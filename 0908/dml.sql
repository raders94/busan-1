drop database if exists `d_1`;
create database if not exists `d_1`;
use `d_1`;


-- 회원
-- 식별자, 이메일, 이름, 연령, 등급, 생성일자 
-- 이메일은 중복되지 않았으면 좋겠다
create table members(
  id bigint not null auto_increment primary key,
  email varchar(100) not null unique,
  name varchar(50) not null,
  age int,
  grade varchar(10) default 'BRONZE',
  created_at timestamp default now()
);

show tables;
desc members;

-- 주문테이블
create table orders(
  id bigint not null auto_increment primary key,
  member_id bigint not null,
  product varchar(100) not null,
  amount int not null,
  ordered_at timestamp default now(),
  -- foreign key () references ``()
  foreign key (member_id) references `members`(id)
);

show tables;
desc orders;

insert into members
  ( name, email, age, grade )
values
  ( '김민수', 'kim2@example.com', 28, 'SILVER' )
;

insert into members
  ( name, email, age )
values
  ( '이영희', 'lee@example.com', 34 )
;

insert into members
  ( name, email, age )
values
  ( '박민수', 'park@example.com', NULL )
;

insert into members
  ( name, email, age, grade )
values
  ( '홍길동', 'a@google.com', 25, 'BRONZE'),
  ( '강감찬', 'b@naver.com', 41, 'GOLD'),
  ( '이순신', 'c@google.com', 33, 'SILVER')
;
select
  *
from
  members
;

select
  name as 이름, email as 이메일, age as 나이
from
  members;

select
  *
from
  members
where  
  grade = "BRONZE";

select  
  *
from
  members
where  
  grade = "BRONZE"
  and 
  age > 10;


select  
  *
from
  members
where  age
  between 10 and 30;

select
  *
from
  members
where name
  like '김%';


select
  *
from
  members
where name
  like '%google.com';

select
  *
from
  members
where name
  like '__수';

select
  *
from
  members
where 
  age is null;

select
  distinct grade
from
  members
order by grade asc;

select count(*) total_member_count
from members;

select count(age)
from members;

select 
  avg(age) '평균나이',
  min(age) '최소나이',
  max(age) '최대나이'
from members;

select 
  grade,
  count(*)
from members
group by
  grade
having 
  count(*) >= 2;



select 
  avg(age) '평균나이'
  from members;


select 
  name,
  age
from members
where
  age>= (select avg(age) from members)  
; #서브쿼리, 비효율적임, 가급적 사용자제


select
  *
from
  members
limit 5 #가져올 데이터 량
offset 5 #가져올 데이터 초기값
;


update members
set 
  grade = 'GOLD'
where 
  id = 1
  ;
select * from members;

update members
set
  grade = 'SILVER',
  age = 29
where 
  email = 'kim2@example.com';


update members
set
  age = age + 1
where
  id = 3
;

delete from members
where 
  id =3
  ;

delete from members
where 
  age is null
  ;






