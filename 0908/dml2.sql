drop database if exists `d_2`;
create database if not exists `d_2`;
use `d_2`;

create table members(
  id bigint not null auto_increment primary key,
  name varchar(50) not null,
  dept_id bigint
  #foreign key (dept_id) references `members`(id)
);

create table dept(
  id bigint not null auto_increment primary key,
  name varchar(50) not null
);

create table orders(
  id bigint not null auto_increment primary key,
  member_id bigint not null,
  product varchar(100) not null,
  amount bigint
);


insert into dept
  ( name )
values
  ( '개발팀'),
  ( '디자인팀'),
  ( '마켓팅팀')
;

insert into members
  (name, dept_id)
values
  ('김철수', 1),
  ('이영자', 1),
  ('박준수', 2),
  ('최민수', null),
  ('한명호', null)
;

insert into orders
  (member_id, product, amount)
values   
  (1, '노트북', 1500000),  
  (1, '마우스', 35000),  
  (2, '키보드', 39000),  
  (3, '모니터', 450000),  
  (99, '헤드셋', 120000)
  ;

select
  *
from
  dept
;
select *
from 
  orders;


select 
  m.id as '회원 번호',
  m.name as '회원 이름',
  d.name as '부서 이름'
from 
  members m
inner join
  dept d
on 
  m.dept_id = d.id
;


select *
from members m 
inner join orders o
on m.id = o.member_id;


select 
  m.id as '회원 번호',
  m.name as '회원 이름',
  o.product as '상품명',
  o.amount as '상품가액'
from members m
inner join
  orders o
on 
  m.id = o.member_id
;

select d.name as '부서명',
       m.name as '회원명',
       o.product as '상품명',
       o.amount as '상품가액'
from members m
inner join dept d
on m.dept_id = d.id
inner join orders o
on o.member_id = m.id;


select 
  m.name as '회원명',
  count(o.id) as '주문 건수',
  sum(o.amount) as '주문 금액'
from members m
inner join dept d
on m.dept_id =d.id
inner join orders o
on o.member_id=m.id
where d.name = '개발팀'
group by m.id, m.name;


select *
from members m
left join dept d
on m.dept_id = d.id
;
