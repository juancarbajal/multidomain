create table if not exists domains(
    company_id varchar(255) comment 'id of the company', 
    url varchar(64) primary key comment 'domain url',
    owner text comment 'data of the owner',
    status  tinyint unsigned comment 'status of the domain requeriment',
    renewal_type  tinyint unsigned default 1 comment '0: disabled, 1: auto, 2, forced',
    release_date datetime comment 'date of domain activation, status 100',
    aws_r53_id varchar(255) comment 'aws route 53 info',
    aws_acm_id varchar(255) comment 'aws acm info',
    aws_clf_id varchar(255) comment 'aws cloudfront info', 
    created_at datetime default now() comment 'date of creation',
    updated_at datetime default now() comment 'date of updated'
);
