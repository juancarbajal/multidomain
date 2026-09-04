set @sql1 = 'alter table domains add column status_bk tinyint unsigned;';
set @sql2 = 'update domains set status_bk = status;';
set @sql3 = 'update domains set status = null;';
set @sql4 = 'alter table domains modify status enum("initiated", "route53_created", "tucows_created", "acm_created", "route53_updated", "acm_validated", "cloudfront_created", "finished", "cancel") default "initiated" comment "status of domain request";';
set @sql5 = 'update domains set status = case status_bk
when 1 then "initiated"
when 10 then "route53_created" 
when 20 then "tucows_created"
when 30 then "acm_created"
when 35 then "route53_updated" 
when 40 then "acm_validated" 
when 50 then "cloudfront_created" 
when 100 then "finished" 
when 200 then "cancel" 
end;';

SELECT @statusDataType := DATA_TYPE from INFORMATION_SCHEMA.COLUMNS where
table_schema = database() and table_name = "domains" and column_name="status";

set @s = IF (@statusDataType = "tinyint", @sql1, 'select "fallo sql1"');	
prepare stm1 from @s;
execute stm1;
deallocate prepare stm1;

set @s = IF (@statusDataType = "tinyint", @sql2, 'select "fallo sql2"');	
prepare stm2 from @s;
execute stm2;
deallocate prepare stm2;

set @s = IF (@statusDataType = "tinyint", @sql3, 'select "fallo sql3"');	
prepare stm3 from @s;
execute stm3;
deallocate prepare stm3;

set @s = IF (@statusDataType = "tinyint", @sql4, 'select "fallo sql4"');	
prepare stm4 from @s;
execute stm4;
deallocate prepare stm4;

set @s = IF (@statusDataType = "tinyint", @sql5, 'select "fallo sql5"');	
prepare stm5 from @s;
execute stm5;
deallocate prepare stm5;
