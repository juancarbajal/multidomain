
create table md_domain(
url varchar(64) primary key,
company_id varchar(255), 
owner text, 
aws_r53_id varchar(255),
aws_acm_id varchar(255),
aws_clf_id varchar(255), 
status integer
);
create index idx_md_domain on md_domain(company_id);


alter table md_domain add ins_date datetime default now();
alter table md_domain add upd_date datetime;
create trigger md_tg_upd_domain before update on md_domain 
for each row set new.upd_date =now();

create table md_domain_log(
url varchar(64),
t timestamp default current_timestamp,
action varchar(64), 
log text
);

create index md_idx_domain_log on md_domain_log(url);
